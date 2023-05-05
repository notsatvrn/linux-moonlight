# the remote patch syncer used by moonlight.
# this script will automatically detect which patches need to be downloaded from external sources, and merge them.

import requests
import shutil
import glob
import os

kernel_version = "6.1"
bore_version = "2.2.3"

ck_hrtimer_patches = [
    '0001-hrtimer-Create-highres-timeout-variants-of-schedule_.patch',
    '0002-time-Special-case-calls-of-schedule_timeout-1-to-use.patch',
    '0003-time-Special-case-calls-of-schedule_timeout-1-to-use.patch',
    '0004-hrtimer-Replace-all-schedule-timeout-1-with-schedule.patch',
    '0005-hrtimer-Replace-all-calls-to-schedule_timeout_interr.patch',
    '0006-hrtimer-Replace-all-calls-to-schedule_timeout_uninte.patch',
    '0007-time-Don-t-use-hrtimer-overlay-when-pm_freezing-sinc.patch',
    '0008-clockevents-hrtimer-Make-hrtimer-granularity-and-min.patch',
]

def merge_all(root: str, output: str):
    patches = glob.glob(f"{root}/*.patch")
    output = open(output, "w")

    for patch in patches:
        with open(patch) as file:
            for line in file:
                output.write(line)
        output.write("\n")
    
    output.close()

def merge_remote(root: str, files: list[str], output: str):
    output = open(output, "w")

    for file in files:
        contents = requests.get(f"{root}/{file}").content.decode("utf-8")
        output.write(contents)
        last_line = contents[len(contents) - 1]
        if last_line[len(last_line) - 1] != "\n":
            output.write("\n")

    output.close()

if __name__ == "__main__":
    # Remove existing patches.
    for patch in glob.glob("../*.patch"):
        os.remove(patch)

    # Remove existing config.
    if os.path.exists("../config"):
        os.remove("../config")

    # Use Clear Linux's kernel config.
    with open("../config", "w") as file:
        file.write(requests.get("https://raw.githubusercontent.com/clearlinux-pkgs/linux-ltscurrent/main/config").content.decode("utf-8"))

    # Kernel compiler patch - add support for compiling to more microarchitectures.
    with open("../0001-more-uarches.patch", "w") as file:
        file.write(requests.get("https://raw.githubusercontent.com/graysky2/kernel_compiler_patch/master/more-uarches-for-kernel-5.17%2B.patch").content.decode("utf-8"))

    # Arch Linux patches.
    arch_pkgbuild = requests.get("https://raw.githubusercontent.com/archlinux/svntogit-packages/packages/linux-lts/trunk/PKGBUILD").content.decode("utf-8").split("\n")
    arch_patches = []
    arch_parsing_patches = False

    for l in arch_pkgbuild:
        line = l.split("#")[0].strip().replace("\"", "", -1) # clean up line for easier parsing
        if not arch_parsing_patches:
            if line[:8] == "source=(":
                arch_parsing_patches = True
        elif arch_parsing_patches:
            if line == ")":
                break
            elif line[len(line)-6:len(line)] == ".patch":
                arch_patches.append(line)

    merge_remote("https://raw.githubusercontent.com/archlinux/svntogit-packages/packages/linux-lts/trunk", arch_patches, "../0002-arch.patch")

    # hrtimer patches from Con Kolivas.
    merge_remote(f"https://raw.githubusercontent.com/notsatvrn/linux-patches/master/linux-{kernel_version}.y/ck-hrtimer", ck_hrtimer_patches, "../0003-ck-hrtimer.patch")

    # Clear Linux patches.
    clear_spec = requests.get("https://raw.githubusercontent.com/clearlinux-pkgs/linux-ltscurrent/main/linux-ltscurrent.spec").content.decode("utf-8").split("\n")
    clear_listed_patches = {}
    clear_applied_patches = []
    clear_patches = []

    for l in clear_spec:
        line = l.split("#")[0].strip() # clean up line for easier parsing
        if line[:5] == "Patch":
            clear_listed_patches[line[5:9]] = line[11:len(line)]
        if line[:6] == "%patch":
            clear_applied_patches.append(line[6:10])

    for applied in clear_applied_patches:
        clear_patches.append(clear_listed_patches[applied])
    
    merge_remote("https://raw.githubusercontent.com/clearlinux-pkgs/linux-ltscurrent/main", clear_patches, "../0004-clear.patch")

    # CPU Schedulers - BORE
    bore = requests.get(f"https://raw.githubusercontent.com/firelzrd/bore-scheduler/main/bore-stable/0001-linux{kernel_version}.y-bore{bore_version}.patch").content.decode("utf-8")
    bore_tuning = requests.get(f"https://raw.githubusercontent.com/firelzrd/bore-scheduler/main/bore-stable/0002-constgran-v2.patch").content.decode("utf-8")

    with open("../0005-BORE.patch", "w") as file:
        file.write(bore)

    with open("../0005-BORE-tuned.patch", "w") as file:
        file.write(bore)
        file.write("\n")
        file.write(bore_tuning)

    # CPU Schedulers - TT
    with open("../0005-TT.patch", "w") as file:
        file.write(requests.get(f"https://raw.githubusercontent.com/hamadmarri/TT-CPU-Scheduler/master/patches/{kernel_version}/tt-{kernel_version}.patch").content.decode("utf-8"))

    # TODO: cherry-picked CachyOS, TKG, XanMod patches
