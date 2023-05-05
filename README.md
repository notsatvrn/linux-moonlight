# moonlight

a high-performance custom Linux kernel based on Clear Linux's LTS kernels.

NOTE: WIP, will improve readme and add credits and such later.

## installation

```sh
git clone https://github.com/notsatvrn/linux-moonlight.git
python scripts/sync.py
makepkg -si
```

the default settings in the PKGBUILD are optimized for desktops. you may wish to change these for embedded devices or servers.
