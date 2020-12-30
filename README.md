# pcichk

### A program for monitoring your PCI devies (tested on Ubuntu Server 18.04)

This program can be scheduled to run using crontab, or it can be set up as a service to run on boot. The program keeps a log of the output of lspci every time it runs, and it will check for differences. It is capable of detecting new devices, missing devices, and devices with a new vendor:product ID.

### Example email message:
```
Found 3 PCI Differences:
SAME DEVICE BUT DIFFERENT ID: Host bridge [0600]: Advanced Micro Devices, Inc. [AMD] Device [1022:1234]
NEW DEVICE: PCI bridge [0604]: Advanced Micro Devices, Inc. [AMD] Device [1022:57a3]
MISSING DEVICE: SATA controller [0106]: Advanced Micro Devices, Inc. [AMD] FCH SATA Controller [AHCI mode] [1022:7901]
```

### Installation guide:

The way that you install this program depends on how you want to use it, such as a crontab job or a systemd service, however when you install it there are some things you need to set up. In the `pcichk.py` file, lines 3-6 can/need to be configured for this program to work.

 - `LSPCI_OUTPUT_FOLDER` is the folder where all of the lspci outputs will be stored.
 - `MAILTO` is the email address of the person who the emails should go to.
 - `MAILFROM` is the name of the sender (usually it would be set to the name of the server for clarity).
 - `SUBJECT` is the subject of the email, which is set to *"PCI Differences Detected"* by default.

For this program to work, you must have ssmtp set up.