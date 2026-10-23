---
title: "Fedora 17 on a 2011 13\" MacBook Air"
date: 2012-12-15T07:29:30Z
description: "Installing Fedora 17 on a 2011 MacBook Air and switching trackpad two-finger scrolling to OS X style natural scrolling with xmodmap."
tags: ["linux", "macos"]
archived: true
---

Decided to throw Fedora 17 on my MacBook Air to see how well it works. Actually, works pretty damn well. Wireless, backlight keyboard and trackpad all work with no modifications. I still have a lot to configure, but this seems like a very nice start to something I thought would have a lot more problems.

Installed [rEFIt](http://refit.sourceforge.net/) on my Air. Made a [USB bootable drive](/posts/convert-iso-to-img-and-make-bootable-usb/) of [Fedora 17 ISO 64-bit](http://download.fedoraproject.org/pub/fedora/linux/releases/17/Fedora/x86_64/iso/Fedora-17-x86_64-DVD.iso). Rebooted and held down Option key, selected Fedora media. Installed Fedora using the entire disk, I did not want to dual boot, wanted only Fedora. After install Fedora reboots the system, my system hung, but I took out the USB stick, powered off and powered back on holding the Option key. Fedora was my only bootable device so I selected that and it booted straight into Fedora 17.

The trackpad works with two finger scrolling, you just have to enable it in System Settings. But the scrolling is the opposite of OS X default scrolling. I'll admit with OS X Lion I did not like the default 'natural' scrolling. However, since Mountain Lion I have used the default 'natural' scrolling, and sure enough I prefer it and find it more 'natural'...damn Apple. To get this on Fedora 17 is a simple change. Might want to get the current settings in case you want to go back, note the 4 and 5.

```sh
xmodmap -pp

xmodmap -e "pointer = 1 2 3 5 4 7 6 8 9 10 11 12"
```

Your scrolling in Fedora 17 should be more OS X like. Credit to [this](https://ask.fedoraproject.org/question/653/solved-is-there-a-way-to-have-mac-like-natural) forum post.
