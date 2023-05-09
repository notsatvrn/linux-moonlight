# Original Maintainer: Andreas Radke <andyrtr@archlinux.org>
# Maintainer: satvrn <pastawho@gmail.com>

### kernel version.
# OPTIONS:
# "6.1" (default)
_version="6.1"

# ---
# KERNEL OPTIONS
# ---

### CPU scheduler.
# OPTIONS:
# "cfs"        - CFS: the default CPU scheduler in Linux
# "bmq"        - BMQ: a more modern evolution of PDS
# "pds"        - PDS: simple and efficient scheduler for interactive tasks
# "bore"       - BORE: improved responsiveness over CFS
# "bore-tuned" - BORE w/ tuned sysctl config
# "tt"         - TT: handles scheduling based on task types
# (default: "cfs")
_cpu_scheduler="bore-tuned"

### CPU scheduler yield type. (pulled from TKG)
## effect is based on the CPU scheduler you picked.
# OPTIONS (PDS):
# 0 - no yield: best option for gaming
# 1 - yield only to better priority/deadline tasks: potentially unstable
# 2 - expire timeslice and recalculate deadline: usually worst performance
# OPTIONS (BMQ):
# 0 - no yield
# 1 - deboost and requeue task
# 2 - set rq skip task
# (default: 1)
_cpu_scheduler_yield=1

### NEST patches.
## improves moderate workload performance by reusing hot cores.
## only works with CFS or BORE (including tuned)!
# OPTIONS: y/n (default: y)
_nest="y"

### Con Kolivas' ck-hrtimer patches.
## improves latency with high tick rates (1000Hz+).
# OPTIONS: y/n (default: y)
_ck_hrtimer="y"

### Google's BBR2 TCP congestion control patches.
## improves TCP performance.
# OPTIONS: y/n (default: y)
_bbr2="y"

### LRNG patches.
## improves RNG performance.
# OPTIONS: y/n (default: y)
_lrng="y"

# ---
# COMPILATION OPTIONS
# ---

### C compiler to be used.
# OPTIONS: "gcc" | "clang" (default: "gcc")
_compiler="gcc"

### custom path to C compiler executable.
# OPTIONS: "" (use system path) | "<path>" (default: "")
_custom_compiler_path=""

### LLVM's LTO.
## requires that _compiler is clang.
# OPTIONS:
# full - single-threaded LTO: slower and uses more memory, highest runtime performance.
# thin - multi-threaded LTO: faster and uses less memory, lower runtime performance than full.
# none - do not use LTO
# (default: "none")
_llvm_lto="none"

### localmodconfig file.
## only builds a set number of modules at compile time
# OPTIONS: "" (disabled) or "<path>/<to>/<file>" (defualt: "")
_localmodconfig=""

### enable or disable ccache.
## improves compilation speed by reusing previously compiled objects.
# OPTIONS: y/n (default: y)
_ccache="y"

### configuration utility.
# OPTIONS:
# "nconfig"
# "menuconfig"
# "xconfig"
# "gconfig"
# "" (disabled)
# (default: "")
_configurator=""

# ---
# configuration is done.
# ---

# patch version.

_patch=0

case "$_version" in
  "6.1")
    _patch=27
    ;;
  *)
    _error "Unsupported kernel version."
    ;;
esac

# package details.

pkgbase=linux-moonlight
pkgver="$_version.$_patch"
pkgrel=1
pkgdesc="a high-performance custom Linux kernel based on Clear Linux's LTS kernels."
url="https://github.com/notsatvrn/linux-moonlight"
arch=(x86_64)
license=(GPL2)
makedepends=(
  bc libelf pahole cpio perl tar xz glibc binutils make patch
)
options=('!strip')
_srcname=linux-$pkgver

source=(
  "https://cdn.kernel.org/pub/linux/kernel/v${_version:0:1}.x/$_srcname.tar".{xz,sign}
  "config"
  "0001-more-uarches.patch"
  "0002-arch.patch"
  "0003-clear.patch"
  "0004-cachyos.patch"
)

validpgpkeys=(
  'ABAF11C65A2970B130ABE3C479BE3E4300411886' # Linus Torvalds
  '647F28654894E3BD457199BE38DBBDC86092693E' # Greg Kroah-Hartman
)

# https://www.kernel.org/pub/linux/kernel/v6.x/sha256sums.asc
sha256sums=('c2b74b96dd3d0cc9f300914ef7c4eef76d5fac9de6047961f49e69447ce9f905'
            'SKIP'
            'SKIP'
            'SKIP'
            'SKIP'
            'SKIP'
            'SKIP')

export KBUILD_BUILD_HOST=archlinux
export KBUILD_BUILD_USER=$pkgbase
export KBUILD_BUILD_TIMESTAMP
KBUILD_BUILD_TIMESTAMP="$(date -Ru${SOURCE_DATE_EPOCH:+d @$SOURCE_DATE_EPOCH})"

if [ "$_cpu_scheduler" != "cfs" ]; then
  sha256sums+=("SKIP")
  case "$_cpu_scheduler" in
    "cfs") ;;
    "bmq"|"pds") source+=("0005-prjc.patch") ;;
    "bore") source+=("0005-BORE.patch") ;;
    "bore-tuned") source+=("0005-BORE-tuned.patch") ;;
    "tt") source+=("0005-TT.patch") ;;
    *)
      _error "Invalid CPU scheduler \"$_cpu_scheduler\"."
      ;;
  esac
fi

if [ "$_nest" != "n" ]; then
  if [ "$_cpu_scheduler" == "cfs" ] || [ "${_cpu_scheduler:0:4}" == "bore" ]; then
    sha256sums+=("SKIP")
    source+=("0006-NEST.patch")
  else
    _error "NEST patches only work with CFS or BORE."
  fi
fi

if [ "$_ck_hrtimer" != "n" ]; then
  sha256sums+=("SKIP")
  source+=("0007-ck-hrtimer.patch")
fi

if [ "$_bbr2" != "n" ]; then
  sha256sums+=("SKIP")
  source+=("0008-BBR2.patch")
fi

if [ "$_lrng" != "n" ]; then
  sha256sums+=("SKIP")
  source+=("0009-LRNG.patch")
fi

case "$_compiler" in
  "gcc")
    makedepends+=(gcc gcc-libs)
    ;;
  "clang")
    makedepends+=(clang llvm lld python)
    BUILD_FLAGS=(
        CC=clang
        LD=ld.lld
        LLVM=1
        LLVM_IAS=1
    )
    ;;
  *) ;;
esac

# helper functions pulled from TKG

_undefine() {
  for _config_name in "$@"; do
    scripts/config -k --undefine "${_config_name}"
  done
}

_enable() {
  for _config_name in "$@"; do
    scripts/config -k --enable "${_config_name}"
  done
}

_disable() {
  for _config_name in "$@"; do
    scripts/config -k --disable "${_config_name}"
  done
}

_module() {
  for _config_name in "$@"; do
    scripts/config -k --module "${_config_name}"
  done
}

# helper functions pulled from CachyOS

_fatal() {
  error "$@";
  exit 1;
}

prepare() {
  cd $_srcname

  echo "Setting version..."
  scripts/setlocalversion --save-scmversion
  echo "-$pkgrel" > localversion.10-pkgrel
  echo "${pkgbase#linux}" > localversion.20-pkgname

  local src
  for src in "${source[@]}"; do
    src="${src%%::*}"
    src="${src##*/}"
    [[ $src = *.patch ]] || continue
    echo "Applying patch $src..."
    patch -Np1 < "../$src"
  done

  # CPU scheduler.
  if [ "$_cpu_scheduler" != "cfs" ]; then
    _disable "FAIR_GROUP_SCHED" "CFS_BANDWIDTH"

    if [ "$_cpu_scheduler" == "bmq" ] || [ "$_cpu_scheduler" == "pds" ]; then
      _enable "SCHED_ALT" "SCHED_${_cpu_scheduler^^}"

      # CPU scheduler yield type. (pulled from TKG)
      case "$_cpu_scheduler_yield" in
        0) sed -i -e 's/int sched_yield_type __read_mostly = 1;/int sched_yield_type __read_mostly = 0;/' ./kernel/sched/alt_core.c ;;
        2) sed -i -e 's/int sched_yield_type __read_mostly = 1;/int sched_yield_type __read_mostly = 2;/' ./kernel/sched/alt_core.c ;;
        *) ;;
      esac
    fi

    case "$_cpu_scheduler" in
      "bmq") _disable "SCHED_PDS" ;;
      "pds") _disable "SCHED_BMQ" ;;
      "bore"|"bore-tuned") _enable "SCHED_BORE" ;;
      "tt") _enable "TT_SCHED" "TT_ACCOUNTING" ;;
    esac
  fi

  echo "Setting config..."
  cp ../config .config
  make ${BUILD_FLAGS[*]} olddefconfig
  diff -u ../config .config || :

  if [ "$_localmodconfig" != "" ]; then
    msg2 "Running localmodconfig..."
    make ${BUILD_FLAGS[*]} LSMOD="$(realpath -f "$_localmodconfig")" localmodconfig
  fi

  make ${BUILD_FLAGS[*]} -s kernelrelease > version
  echo "Prepared $pkgbase version $(<version)"

  case "$_configurator" in
    "") ;;
    "nconfig"|"menuconfig"|"xconfig"|"gconfig")
      make ${BUILD_FLAGS[*]} "$_configurator"
      ;;
    *) msg "Invalid configurator, skipping...";;
  esac
}

build() {
  cd $_srcname
  make ${BUILD_FLAGS[*]} all
}

_package() {
  pkgdesc="Kernel and modules for $pkgdesc"
  depends=(coreutils kmod initramfs)
  optdepends=('wireless-regdb: to set the correct wireless channels of your country'
              'linux-firmware: firmware images needed for some devices')
  provides=(VIRTUALBOX-GUEST-MODULES WIREGUARD-MODULE KSMBD-MODULE)
  replaces=(wireguard-lts)

  cd $_srcname
  local modulesdir
  modulesdir="$pkgdir/usr/lib/modules/$(<version)"

  echo "Installing boot image..."
  # systemd expects to find the kernel here to allow hibernation
  # https://github.com/systemd/systemd/commit/edda44605f06a41fb86b7ab8128dcf99161d2344
  install -Dm644 "$(make ${BUILD_FLAGS[*]} -s image_name)" "$modulesdir/vmlinuz"

  # Used by mkinitcpio to name the kernel
  echo "$pkgbase" | install -Dm644 /dev/stdin "$modulesdir/pkgbase"

  echo "Installing modules..."
  make ${BUILD_FLAGS[*]} INSTALL_MOD_PATH="$pkgdir/usr" INSTALL_MOD_STRIP=1 \
    DEPMOD=/doesnt/exist modules_install  # Suppress depmod

  # remove build and source links
  rm "$modulesdir"/{source,build}
}

_package-headers() {
  pkgdesc="Headers and scripts for building modules for the $pkgdesc kernel"
  depends=(pahole)

  cd $_srcname
  local builddir
  builddir="$pkgdir/usr/lib/modules/$(<version)/build"

  echo "Installing build files..."
  install -Dt "$builddir" -m644 .config Makefile Module.symvers System.map \
    localversion.* version vmlinux
  install -Dt "$builddir/kernel" -m644 kernel/Makefile
  install -Dt "$builddir/arch/x86" -m644 arch/x86/Makefile
  cp -t "$builddir" -a scripts

  # required when STACK_VALIDATION is enabled
  install -Dt "$builddir/tools/objtool" tools/objtool/objtool

  # required when DEBUG_INFO_BTF_MODULES is enabled
  install -Dt "$builddir/tools/bpf/resolve_btfids" tools/bpf/resolve_btfids/resolve_btfids

  echo "Installing headers..."
  cp -t "$builddir" -a include
  cp -t "$builddir/arch/x86" -a arch/x86/include
  install -Dt "$builddir/arch/x86/kernel" -m644 arch/x86/kernel/asm-offsets.s

  install -Dt "$builddir/drivers/md" -m644 drivers/md/*.h
  install -Dt "$builddir/net/mac80211" -m644 net/mac80211/*.h

  # https://bugs.archlinux.org/task/13146
  install -Dt "$builddir/drivers/media/i2c" -m644 drivers/media/i2c/msp3400-driver.h

  # https://bugs.archlinux.org/task/20402
  install -Dt "$builddir/drivers/media/usb/dvb-usb" -m644 drivers/media/usb/dvb-usb/*.h
  install -Dt "$builddir/drivers/media/dvb-frontends" -m644 drivers/media/dvb-frontends/*.h
  install -Dt "$builddir/drivers/media/tuners" -m644 drivers/media/tuners/*.h

  # https://bugs.archlinux.org/task/71392
  install -Dt "$builddir/drivers/iio/common/hid-sensors" -m644 drivers/iio/common/hid-sensors/*.h

  echo "Installing KConfig files..."
  find . -name 'Kconfig*' -exec install -Dm644 {} "$builddir/{}" \;

  echo "Removing unneeded architectures..."
  local arch
  for arch in "$builddir"/arch/*/; do
    [[ $arch = */x86/ ]] && continue
    echo "Removing $(basename "$arch")"
    rm -r "$arch"
  done

  echo "Removing documentation..."
  rm -r "$builddir/Documentation"

  echo "Removing broken symlinks..."
  find -L "$builddir" -type l -printf 'Removing %P\n' -delete

  echo "Removing loose objects..."
  find "$builddir" -type f -name '*.o' -printf 'Removing %P\n' -delete

  echo "Stripping build tools..."
  local file
  while read -rd '' file; do
    case "$(file -Sib "$file")" in
      application/x-sharedlib\;*)      # Libraries (.so)
        strip -v "$STRIP_SHARED" "$file" ;;
      application/x-archive\;*)        # Libraries (.a)
        strip -v "$STRIP_STATIC" "$file" ;;
      application/x-executable\;*)     # Binaries
        strip -v "$STRIP_BINARIES" "$file" ;;
      application/x-pie-executable\;*) # Relocatable binaries
        strip -v "$STRIP_SHARED" "$file" ;;
    esac
  done < <(find "$builddir" -type f -perm -u+x ! -name vmlinux -print0)

  echo "Stripping vmlinux..."
  strip -v "$STRIP_STATIC" "$builddir/vmlinux"

  echo "Adding symlink..."
  mkdir -p "$pkgdir/usr/src"
  ln -sr "$builddir" "$pkgdir/usr/src/$pkgbase"
}

pkgname=("$pkgbase" "$pkgbase-headers")
for _p in "${pkgname[@]}"; do
  eval "package_$_p() {
    $(declare -f "_package${_p#"$pkgbase"}")
    _package${_p#"$pkgbase"}
  }"
done

# vim:set ts=8 sts=2 sw=2 et:
