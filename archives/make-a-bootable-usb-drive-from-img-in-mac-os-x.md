+++
author = "Shane Cunningham"
date = 2012-02-07T10:35:32Z
description = ""
draft = false
slug = "make-a-bootable-usb-drive-from-img-in-mac-os-x"
title = "Make a bootable USB drive from .img in Mac OS X"

+++


I needed to make a USB bootable drive of pfSense and being an OS X newb, had to Google it. Here's what I found. Run these commands from Terminal.
<pre style="padding-left: 30px;"><code>diskutil list</code></pre>
Find your USB drive in the list, mine was <code>/dev/disk2</code>. Unmount the drive if it is currently mounted, <code>umount /dev/disk2</code>

Now, there's two commands you can run, dd with /rdisk2 gave me 15.33 KB/s. dd with just /disk2 only gave me 4.60 KB/s.
<pre style="padding-left: 30px;"><code>sudo dd if=/Users/shane/Downloads/pfSense-memstick-2.0.1-RELEASE-i386.img of=/dev/rdisk2 bs=1m</code></pre>
Change input file and output file as necessary. If <code>/dev/rdisk</code> does not work for some reason just use <code>of=/dev/disk2</code>

When using rdisk2 my flash drive was constantly flashing with activity, with just disk2 it would flash for a few seconds followed by a few minutes of no activity. Use /dev/rdiskN where N is your USB drive.