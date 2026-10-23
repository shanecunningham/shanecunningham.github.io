+++
author = "Shane Cunningham"
date = 2012-12-15T07:29:30Z
description = ""
draft = false
slug = "fedora-17-on-a-2011-13-macbook-air"
title = "Fedora 17 on a 2011 13\" MacBook Air"

+++


Decided to throw Fedora 17 on my MacBook Air to see how well it works. Actually, works pretty damn well. Wireless, backlight keyboard and trackpad all work with no modifications. I still have a lot to configure, but this seems like a very nice start to something I thought would have a lot more problems.

Installed <a href="http://refit.sourceforge.net/">rEFIt</a> on my Air. Made a <a title="Convert .iso to .img and make bootable USB" href="http://cunninghamshane.com/convert-iso-to-img-and-make-bootable-usb/">USB bootable drive</a> of <a href="http://download.fedoraproject.org/pub/fedora/linux/releases/17/Fedora/x86_64/iso/Fedora-17-x86_64-DVD.iso">Fedora 17 ISO 64-bit</a>. Rebooted and held down Option key, selected Fedora media. Installed Fedora using the entire disk, I did not want to dual boot, wanted only Fedora. After install Fedora reboots the system, my system hung, but I took out the USB stick, powered off and powered back on holding the Option key. Fedora was my only bootable device so I selected that and it booted straight into Fedora 17.

The trackpad works with two finger scrolling, you just have to enable it in System Settings. But the scrolling is the opposite of OS X default scrolling. I'll admit with OS X Lion I did not like the default 'natural' scrolling. However, since Mountain Lion I have used the default 'natural' scrolling, and sure enough I prefer it and find it more 'natural'...damn Apple. To get this on Fedora 17 is a simple change. Might want to get the current settings in case you want to go back, note the 4 and 5.

<pre><code>xmodmap -pp

xmodmap -e "pointer = 1 2 3 5 4 7 6 8 9 10 11 12"</code></pre>
Your scrolling in Fedora 17 should be more OS X like. Credit to <a href="https://ask.fedoraproject.org/question/653/solved-is-there-a-way-to-have-mac-like-natural">this</a> forum post.