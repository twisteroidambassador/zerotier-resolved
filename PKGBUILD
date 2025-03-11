## Maintainer: twisteroid ambassador <twisteroidambassador@users.noreply.github.com>
pkgname=zerotier-resolved
pkgver=0.0.1
pkgrel=1
epoch=
pkgdesc="Resolve hostnames for ZeroTier networks on Linux"
arch=("any")
url="https://github.com/twisteroidambassador/zerotier-resolved"
license=('GPL')
groups=()
depends=("python" "systemd")
makedepends=()
checkdepends=()
optdepends=()
provides=()
conflicts=()
replaces=()
backup=()
options=()
install=
changelog=
source=("zerotier-resolved.py"
        "zerotier-resolved@.service")
noextract=()
sha256sums=("SKIP" "SKIP")
validpgpkeys=()

package() {
	install -D zerotier-resolved.py "$pkgdir/usr/bin/zerotier-resolved.py"
	install -Dm644 zerotier-resolved@.service "$pkgdir/usr/lib/systemd/system/zerotier-resolved@.service"
}
