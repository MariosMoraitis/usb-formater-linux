#!/usr/bin/env python3

import subprocess
import os
import sys
import re
import json

def list_removable_drives():
    result = subprocess.run(
        ["lsblk", "-J", "-p", "-o", "NAME,SIZE,FSTYPE,MOUNTPOINT,RM,TRAN,TYPE"],
        check=True,
        capture_output=True,
        text=True,
    )
    devices = json.loads(result.stdout)["blockdevices"]
    rows = {}
    devices_names = set()

    def add_device(device, depth=0):
        # rows.append((depth, device))
        rows[depth] = device
        for child in device.get("children", []):
            add_device(child, depth + 1)

    for device in devices:
        is_removable = str(device.get("rm")).lower() in ("1", "true")
        uses_usb = str(device.get("tran")).lower() == "usb"
        if device.get("type") == "disk" and (is_removable or uses_usb):
            add_device(device)

    if not rows:
        print("No removable drives found.")
        return

    print(f"{'NAME':<24} {'SIZE':<8} {'FSTYPE':<8} MOUNTPOINT")
    for depth, device in rows.items():
        name = f"{'  ' * depth}{device['name']}"
        devices_names.add(name.strip().lower())
        print(f"{name:<24} {device.get('size') or '':<8} {device.get('fstype') or '':<8} {device.get('mountpoint') or ''}")

    return devices_names

def format_usb():
    # Step 1: List devices
    print("\n📂 Available drives:")
    names = list_removable_drives()
    print()

    # Step 2: User Input
    device = input("Enter the device (e.g. /dev/sdb1, or q to quit): ").strip()
    if device.lower() == "q" or not device:
        print("Aborted.")
        sys.exit(0)

    if device.lower() not in names:
        print('Input is not a listed device!')
        sys.exit(1)

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

        print(f"\n🎉 {device} successfully formatted as {fs_type.upper()}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Process Error while formatting {device}:\n{str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print('\nProgram stopped by the User.')
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Generic Error while formatting {device}:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print(r"""
_____  ________________       ______________________________  ________________________________________ 
__  / / /_  ___/__  __ )      ___  ____/_  __ \__  __ \__   |/  /__    |__  __/__  __/__  ____/__  __ \
_  / / /_____ \__  __  |________  /_   _  / / /_  /_/ /_  /|_/ /__  /| |_  /  __  /  __  __/  __  /_/ /
/ /_/ / ____/ /_  /_/ /_/_____/  __/   / /_/ /_  _, _/_  /  / / _  ___ |  /   _  /   _  /___  _  _, _/ 
\____/  /____/ /_____/        /_/      \____/ /_/ |_| /_/  /_/  /_/  |_/_/    /_/    /_____/  /_/ |_|  
                                                                                                       
    """)
    
    if sys.platform != "linux":
        print("❌ This script only works on Linux.")
        sys.exit(1)

    if not os.geteuid() == 0:
        print("usb-formatter must be run as root (try: sudo python usb-formatter)")
        sys.exit(1)

    try:        
        format_usb()
    except KeyboardInterrupt:
        print('\nProgram stopped by the User.')
        sys.exit(0)
