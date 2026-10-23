---
title: "Make a bootable USB drive from .img in Mac OS X"
date: 2012-02-07T10:35:32Z
description: "Writing a pfSense .img file to a USB flash drive from Mac OS X using dd with the raw rdisk device."
tags: ["macos", "pfsense"]
archived: true
---

I needed to make a USB bootable drive of pfSense and being an OS X newb, had to Google it. Here's what I found. Run these commands from Terminal.

```sh
diskutil list
```

Find your USB drive in the list, mine was `/dev/disk2`. Unmount the drive if it is currently mounted, `umount /dev/disk2`

Now, there's two commands you can run, dd with /rdisk2 gave me 15.33 KB/s. dd with just /disk2 only gave me 4.60 KB/s.

```sh
sudo dd if=/Users/shane/Downloads/pfSense-memstick-2.0.1-RELEASE-i386.img of=/dev/rdisk2 bs=1m
```

Change input file and output file as necessary. If `/dev/rdisk` does not work for some reason just use `of=/dev/disk2`

When using rdisk2 my flash drive was constantly flashing with activity, with just disk2 it would flash for a few seconds followed by a few minutes of no activity. Use /dev/rdiskN where N is your USB drive.
