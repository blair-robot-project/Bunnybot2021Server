import os
import re
import subprocess as sub
import sys
from sys import platform
from time import sleep

from frc449server.interface import printing


# Runs a command in the shell
def _run(command):
    try:
        process = sub.Popen(command, shell=True, stdout=sub.PIPE, stderr=sub.PIPE)
        return process.communicate()
    except Exception as e:
        printing.printf(
            "Unknown exception on system._run(" + command + "):",
            end=" ",
            style=printing.ERROR,
            log=True,
            logtag="system._run.error",
        )
        printing.printf(e, style=printing.ERROR)


def is_windows():
    return sys.platform.startswith("win")


# From https://askubuntu.com/questions/938255/
def find_usb_partitions():
    if is_windows():
        return []
    return tuple(
        os.path.realpath(os.path.join("/dev/disk/by-id", p))
        for p in os.listdir("/dev/disk/by-id")
        if p.startswith("usb-") and p.rstrip("0123456789") != p
    )


def find_mounted_usbs():
    devs = []
    with open("/proc/mounts") as mounts:
        for line in mounts:
            if line.startswith("/dev/"):
                devs.append(line.split(" ", 1)[0])
    return [d for d in devs if d in find_usb_partitions()]


# Checks for a flash drive
def checkdev():
    return len(find_usb_partitions()) > 0


def get_mount_point(block):
    assert not is_windows()
    p = _run("udisksctl info -b " + block)
    if p[1]:
        return None
    else:
        return (
            [l for l in p[0].decode("utf-8").split("\n") if "MountPoints:" in l][0]
            .split(":")[1]
            .split(",")[0]
            .strip()
        )


def mount(drive=None):
    """Mounts a flash drive

    :param drive: The location of the flash drive or ``None`` if it should be found automatically"""
    if is_windows():
        # Assume Windows just automatically mounts it
        return

    if not drive:
        # If the drive wasn't given to us, find it automatically
        devs = find_usb_partitions()
        if not devs:
            return None
        dev = [d for d in devs if d not in find_mounted_usbs()]
        if not dev:
            loc = get_mount_point(devs[0])
            if not loc:
                return None
            printing.printf(
                "Drive " + devs[0] + " already mounted to " + loc,
                style=printing.YELLOW,
                log=True,
                logtag="system.mount",
            )
            return loc

        drive = dev[0]
        printing.printf(
            "Found drive at " + drive + ", attempting to mount ...",
            end=" ",
            style=printing.FLASH_DRIVE,
        )

    done = 0
    while done < 10:
        p = _run("udisksctl mount -b " + drive)
        error_string = p[1].decode("utf-8").strip("\n")
        if "AlreadyMounted" in error_string:
            loc = get_mount_point(drive)
            printing.printf(
                "Drive " + drive + " already mounted to " + loc,
                style=printing.YELLOW,
                log=True,
                logtag="system.mount",
            )
            return loc
        elif error_string:
            sleep(0.2)
            done += 1
        else:
            message = p[0].decode("utf-8").strip("\n")
            printing.printf(
                message, style=printing.FLASH_DRIVE, log=True, logtag="system.mount"
            )
            return message.split("at")[1].strip(". ")
    printing.printf(
        "Error mounting: " + error_string,
        style=printing.ERROR,
        log=True,
        logtag="system.mount.error",
    )
    return None


# Copies the data file to the mounted flash drive
def copy(fin, fout):
    printing.printf(
        "Copying " + fin + " to " + fout + " ...",
        end=" ",
        style=printing.FLASH_DRIVE,
        log=True,
        logtag="system.copy",
    )

    # with open(fout, 'w') as f:
    # f.write(open(fin).read())
    # copyfile(fin, fout)

    if is_windows():
        _, err = _run(f"echo F | xcopy /Y {fin} {fout}")
    else:
        _, err = _run(f"cp {fin} {fout}")
    if err:
        printing.printf(
            "Error copying: " + err.decode("utf-8"),
            style=printing.ERROR,
            log=True,
            logtag="system.copy.error",
        )
    else:
        printing.printf(
            "Copying successful",
            style=printing.FLASH_DRIVE,
            log=True,
            logtag="system.copy",
        )


# Unmounts the flash drive
def unmount():
    if is_windows():
        # Let the user take care of it
        return

    for dev in find_mounted_usbs():
        printing.printf(
            "Unmounting drive from " + dev + " ...",
            end=" ",
            style=printing.FLASH_DRIVE,
            log=True,
            logtag="system.unmount",
        )
        p = _run("udisksctl unmount -b " + dev)
        if p[1]:
            printing.printf(
                "Error unmounting: " + p[1].decode("utf-8"),
                style=printing.ERROR,
                log=True,
                logtag="system.unmount.error",
            )
        else:
            printing.printf(
                "Unmounting successful, remove device",
                style=printing.FLASH_DRIVE_SUCCESS,
                log=True,
                logtag="system.unmount",
            )


# Finds the MAC address of the bluetooth adapter
# If hcitool is not installed, you can change the script to use some other command,
#   or you can just find it manually and hard code it in
def get_host_mac():
    out = ""
    try:
        if platform == "linux":
            out, _ = _run("hcitool dev")
            return out.decode("utf8").split("\n")[1].split()[1]
        elif platform == "darwin":  # macOS
            # Mac is not yet fully supported
            out, _ = _run("system_profiler SPBluetoothDataType")
            return out.decode("utf8").split("\n")[5].split()[1]
        elif is_windows():
            out, _ = _run("ipconfig /all")
            # TODO this is very janky, may break at some point
            matched = re.search(
                r"Bluetooth.*?Physical Address *(\. )*: *(?P<mac>[A-Za-z0-9-]{17})",
                str(out),
            )
            if matched:
                mac = matched.group("mac")
                return mac.replace("-", ":")
            else:
                printing.printf(
                    "No Windows bluetooth adapter found",
                    style=printing.ERROR,
                    log=True,
                    logtag="system.gethostMAC.error",
                )
        else:
            printing.printf(
                "Server does not run on " + platform,
                style=printing.WARNING,
                log=True,
                logtag="system.gethostMAC",
            )
    except IndexError:
        if out:
            printing.printf(
                "No bluetooth adapter available",
                style=printing.ERROR,
                log=True,
                logtag="system.gethostMAC.error",
            )
        else:
            printing.printf(
                "hcitool/system_profiler not found, please install it or edit systemctl.py to use something else",
                style=printing.ERROR,
                log=True,
                logtag="system.gethostMAC.error",
            )
