#! /usr/bin/env python

import argparse
import json
import logging
import subprocess
import urllib.request


logger = logging.getLogger('zt_resolved')


def read_authtoken() -> str:
    with open('/var/lib/zerotier-one/authtoken.secret', 'rt') as f:
        return f.read()


def get_network_info(authtoken: str) -> dict:
    with urllib.request.urlopen(urllib.request.Request(
        'http://localhost:9993/network',
        headers={
            'X-ZT1-Auth': authtoken,
        },
    )) as resp:
        if resp.status != 200:
            logger.error('Response status: %d %s', resp.status, resp.reason)
            raise RuntimeError('Response status not 200')
        resp_data = resp.read()
        resp_json = json.loads(resp_data)
        logger.debug('Network info response: %r', resp_json)
        return resp_json


def generate_resolvectl_commands(
    network_info: dict,
    restrict_interfaces: list[str] | None = None,
) -> list[list[str]]:
    commands = []
    for network in network_info:
        network_id = network['id']
        device = network['portDeviceName']
        if restrict_interfaces is not None and device not in restrict_interfaces:
            logger.debug(
                'Network %s %s not in interface list, skipping', 
                network_id,
                device,
            )
            continue
        dns_servers = network['dns']['servers']
        if not dns_servers:
            logger.info(
                'Network %s %s has no DNS servers configured', 
                network_id,
                device,
            )
            continue
        dns_domain = network['dns']['domain']
        logger.info(
            'Network %s %s domain: %s, DNS servers: %r',
            network_id,
            device,
            dns_domain,
            dns_servers,
        )
        commands.extend([
            ['/usr/bin/resolvectl', 'domain', device, dns_domain],
            ['/usr/bin/resolvectl', 'dns', device, *dns_servers],
            ['/usr/bin/resolvectl', 'default-route', device, 'no'],
        ])
    return commands


def main():
    parser = argparse.ArgumentParser(
        description='Set ZeroTier per-network DNS servers for systemd-resolved',
    )

    parser.add_argument(
        '--interface',
        '-I',
        action='append',
        help="""Only configure DNS servers for specified interface(s).
        Repeat this argument for each interface."""
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='count',
        help='Increase verbosity. Specify once for INFO, twice for DEBUG.'
    )

    args = parser.parse_args()

    if not args.verbose:
        loglevel = logging.WARNING
    elif args.verbose >= 2:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel)

    logger.debug('Args: %r', args)

    authtoken = read_authtoken()
    network_info = get_network_info(authtoken)
    commands = generate_resolvectl_commands(network_info, args.interface)

    for command in commands:
        logger.debug('Executing command %r', command)
        p = subprocess.run(command)
        if p.returncode != 0:
            logger.error('Command %s returned non-zero: %d', command, p.returncode)


if __name__ == '__main__':
    main()