---
title: "Booting from wrong drive"
date: 2010-12-12T11:05:17Z
tags: []
---

I went to do a bare metal backup of my Windows Server 2008 R2 box and to my surprise it wanted to backup like 1.3 TB. This was unusual since it was a new install and all of C: was a few gigabytes. Turns out, somehow, the bootloader and boot files were installed on my 1 TB data drive.

bcdedit command will display your bootloader settings. I found a dead simple (and free!) GUI tool to edit these settings, [EasyBCD 2.0.2](http://neosmart.net/dl.php?id=1). It doesn’t list Windows Server 2008 R2 as a supported OS, but I can confirm it works on it. Choose BCD Backup / Repair - Change boot drive.
