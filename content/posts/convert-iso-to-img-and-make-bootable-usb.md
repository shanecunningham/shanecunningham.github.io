---
title: "Convert .iso to .img and make bootable USB"
date: 2012-10-12T18:35:01Z
description: "Converting a XenServer 6.1 ISO to a .img on macOS with hdiutil and writing it to a USB drive with dd."
tags: ["macos", "xenserver"]
archived: true
---

Note so I don't have to Google this.

```sh
diskutil list
```

Find USB drive and unmount it, `diskutil unmountDisk /dev/disk1`

Convert .iso to .img. This will put a .dmg extension on the .img file, but you can leave it like that and still make a bootable USB drive with it.

```sh
hdiutil convert -format UDRW -o xenserver61.img /Downloads/XenServer-6.1-install-cd.iso
```

Make bootable USB drive

```sh
dd if=xenserver61.img.dmg of=/dev/rdisk1 bs=1m
```
