+++
author = "Shane Cunningham"
date = 2012-10-12T18:35:01Z
description = ""
draft = false
slug = "convert-iso-to-img-and-make-bootable-usb"
title = "Convert .iso to .img and make bootable USB"

+++


Note so I don't have to Google this.

<pre><code>diskutil list</code></pre>

Find USB drive and unmount it, <code>diskutil unmountDisk /dev/disk1</code>

Convert .iso to .img. This will put a .dmg extension on the .img file, but you can leave it like that and still make a bootable USB drive with it.

<pre><code>hdiutil convert -format UDRW -o xenserver61.img /Downloads/XenServer-6.1-install-cd.iso</code></pre>

Make bootable USB drive

<pre><code>dd if=xenserver61.img.dmg of=/dev/rdisk1 bs=1m</code></pre>