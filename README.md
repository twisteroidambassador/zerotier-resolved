# zerotier-resolved

[ZeroTier networks can be configured with a DNS server and search domain.](https://docs.zerotier.com/dns-management)
Once configured, Windows, macOS and mobile clients can automatically resolve any hostname under the search domain using the configured DNS server.
Linux clients, however, has no such capability.
`zerotier-resolved` provides this much-needed capability.


# Requirements

- `systemd-resolved`, to provide per-interface and per-domain name resolution.
Note that `systemd-resolved` can work alongside [NetworkManager](https://wiki.archlinux.org/title/NetworkManager#systemd-resolved),
[ConnMan](https://wiki.archlinux.org/title/ConnMan#Using_systemd-resolved)
and [`iwd`](https://wiki.archlinux.org/title/Iwd#Select_DNS_manager),
making this solution viable for many desktop Linux distros.

- A reasonably up-to-date version of Python 3. I believe 3.9 and higher should work, although this is only tested with 3.13 at the moment.

  - No 3rd-party Python packages are required.


# Related projects

[`zeronsd`](https://github.com/zerotier/zeronsd) is a DNS **server** running on Linux.
It can automatically resolve member IDs and names to corresponding addresses within a ZeroTier network,
so it's a great choice for providing DNS service for the network.
It does not help Linux clients joined in to said network configure DNS.

[`zerotier-systemd-manager`](https://github.com/zerotier/zerotier-systemd-manager) is a tool that configures per-interface DNS for Linux clients joined in ZeroTier networks.
It requires both `systemd-networkd` and `systemd-resolved`,
which can be inconvenient for desktop Linux usage.


# How it works

`zerotier-resolved` queries the local `zerotier-one` service for info on currently connected networks,
and if any network has DNS servers in its configuration,
execute `resolvectl` commands to add them to the system.
Everything is done on localhost.
It does not need to access the Internet,
or other hosts on the ZeroTier network.


# Usage

## Command line invocation

Just run the `zerotier-resolved.py` script with root privileges:

```shell
sudo python zerotier-resolved.py
```

Nothing is printed to the terminal if everything went well.
To see it in action, add one or two `-v` argument.

Check the current DNS configuration via `resolvectl` to see that it worked:

```shell
 % resolvectl

...

Link 4 (ztxxxxxxxx)
...
Current DNS Server: 192.168.0.1
       DNS Servers: 192.168.0.1
        DNS Domain: zerotier.home.arpa
...

```

This does not survive a reboot or a restart of ZeroTier service,
and it does not automatically update system if the DNS configuration on the ZeroTier network changed.

## `systemd` service bound to network interface

The included `systemd` unit file invokes `zerotier-resolved.py` whenever the network interface associated with a ZeroTier network comes up,
so DNS servers are properly configured even after a reboot.
It still does not auto update if the network's DNS configuration is changed at the controller, though.

### Manual Install

- Copy `zerotier-resolved.py` to somewhere convenient,
perhaps under `/usr/local/bin` or `/opt`.

- Modify `zerotier-resolved@.service`:
  - On the `ExecStart` line, change the absolute path of `zerotier-resolved.py` to match where you put it in the last step;
  - Also, make sure the `python` binary's absolute path is correct.
  If your distro still think `python` means Python 2,
  change it to `python3` as appropriate.
  - Optionally, marvel at all those security hardening configuration lines.
  Even though `zerotier-resolved.py` runs as root,
  the damage it can possibly do is greatly limited.
  (And if your version of `systemd` does not like some of these lines,
  it may be necessary to remove them.)

- Install the properly modified file `zerotier-resolved@.service` to `/etc/systemd/system`.

- Enable it against the interface(s) you would like to configure DNS servers for:

```shell
sudo systemctl enable --now zerotier-resolved@ztxxxxxxxx
```

### Arch Linux Install

After cloning this repository,
just run `makepkg` and install the resulting package.
Then, enable the systemd service as above.


## Other invocation methods

... are left as an exercise for the reader.

ZeroTier unfortunately does not have a "network changed" hook,
so in order to automatically update system DNS whenever new settings are pushed from the controller,
the best one can do is to poll for network information periodically.
So, maybe a systemd timer bound to the zerotier service?