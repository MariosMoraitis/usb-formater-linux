#!/usr/bin/env python3

import subprocess
import os
import sys
import re

def format_usb():
    # Step 1: List devices
    print("\n📂 Available drives:")
    subprocess.run(["lsblk", "-p", "-o", "NAME,SIZE,FSTYPE,MOUNTPOINT"])#([ "grep", "-E", "sd[a-z][0-9]+"])
    print()

    # Step 2: User Input
    device = input("Enter the device (e.g. /dev/sdb1, or q to quit): ").strip()
    if device.lower() == "q" or not device:
        print("Aborted.")
        sys.exit(0)

    fs_type = input("Enter format type (fat32, ext4, ntfs): ").lower().strip()
    if fs_type not in ["fat32", "ext4", "ntfs"]:
        print("❌ Unsupported filesystem format.")
        sys.exit(1)

    # Step 3: Confirmation
    confirm = input(f"⚠️ This will ERASE ALL DATA on {device}. Continue? (y/N): ").strip().lower()
    if confirm not in ["y", "yes"]:
        print("Aborted.")
        sys.exit(0)

    # Step 4: Check if device exists
    if not os.path.exists(device):
        print(f"❌ Device {device} does not exist.")
        sys.exit(1)
    
    if not re.match(r"^/dev/sd[a-z][0-9]+$", device):
        print("❌ Please select a partition (e.g. /dev/sdb1), not a whole disk.")
        exit(1)

    # Step 5: Unmount safely
    try:
        subprocess.run(["sudo", "umount", device], check=True)
        print(f"✅ Unmounted {device}")
    except subprocess.CalledProcessError:
        print(f"ℹ️ {device} was not mounted. Proceeding...")

    # Step 6: Format
    try:
        if fs_type == "fat32":
            subprocess.run(["sudo", "mkfs.vfat", "-F", "32", device], check=True)
        elif fs_type == "ext4":
            subprocess.run(["sudo", "mkfs.ext4", "-F", device], check=True)
        elif fs_type == "ntfs":
            subprocess.run(["sudo", "mkfs.ntfs", "-F", device], check=True)

        print(f"🎉 {device} successfully formatted as {fs_type.upper()}")
    except subprocess.CalledProcessError:
        print(f"❌ Error while formatting {device}.")
        sys.exit(1)

if __name__ == "__main__":
    if sys.platform != "linux":
        print("❌ This script only works on Linux.")
        sys.exit(1)

    format_usb()
