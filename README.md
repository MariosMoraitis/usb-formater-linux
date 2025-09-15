# 🙀 USB Formatter Linux 

A **safe and interactive Python CLI tool** to list and format USB drives on Linux. Perfect for personal use and learning system programming with Python.

## Features
- Lists available USB partitions
- Select partition to format (fat32, ext4, ntfs)
- Safely unmounts before formatting
- Confirmation prompt to prevent accidental data loss
- Clear CLI messages

## Requirements
- Python 3.8+
- Linux environment
- `sudo` privileges

## Usage
```bash
git clone https://github.com/MariosMoraitis/usb-formater-linux.git
cd usb-formatter-linux
sudo python3 usb_formatter.py
