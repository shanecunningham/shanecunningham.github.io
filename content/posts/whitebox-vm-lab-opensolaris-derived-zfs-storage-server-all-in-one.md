---
title: "Whitebox VM Lab & OpenSolaris with napp-it All-in-One"
date: 2012-11-28T02:23:23Z
description: "Building an ESXi whitebox VM lab on an ASRock 970 Extreme4 with a BR10i passed through, serving an OpenIndiana napp-it ZFS NFS datastore."
tags: ["esxi", "zfs", "hardware"]
archived: true
---

My first white box specifically for VMs was solid, but I wanted more flexibility with storage configurations. The passthrough on my ASUS M4A88T-M/USB3 would not work even when IOMMU was enabled. This seems to be quite common for AMD boards, some have the option in BIOS, but it doesn't work. The plan was to boot ESXi off USB and use the other two controllers (on-board and LSI RAID card) for my storage configuration. So, after some research I found an AMD motherboard that had working IOMMU. The board I found was an ASRock 970 Extreme4 which works with ESXi and IOMMU for passing through devices to VMs. When I bought the ASRock motherboard I overlooked the fact it did not have onboard graphics, so make sure you have an extra GPU you can throw in for installing the hypervisor. I went with a really cheap PowerColor Green Radeon AX5450 1GB. My current build is below.

**Motherboard**: [ASRock 970 Extreme4](http://www.asrock.com/mb/AMD/970%20Extreme4/)\
**CPU**: AMD II X4 620 Quad Core\
**RAM**: 16 GB GSkill Value\
**RAID**: IBM BR10i (LSI SAS3082E-R) flashed to IT mode\
**NICs**: 2 x Intel 1 x Realtek\
**GPU**: AMD Radeon 5450

I can confirm this works with ESXi 5 and ESXi 5.1 out of the box. No modifications and all 3 NICs were detected and working. The IBM BR10i is supported and also works out of the box with ESXi. Also works great with Hyper-V. I couldn't get XenServer working but I think it was only because of the LSI card. It would install, but hang when trying to boot for the first time. I might try to find a solution for this because I would rather use XenServer over ESXi.

I'm booting ESXi 5.1 off of a USB flash drive, using a WD Blue 640GB and WD Black 1TB drives for the datastores on the onboard SATA controller, and passing through the IBM BR10i card with my two 2TB data drives to my file server VM.

## My noob ZFS setup

After getting the hardware out of the way I was able to play around with different storage configurations. One that I always really liked was ZFS. I'm still experimenting with it, so this is probably not the most efficient use of the technology, but I mainly wanted to see if I could get it all working. I created an [OpenIndiana](http://openindiana.org/) VM with 6GB RAM, then installed [napp-it](http://www.napp-it.org/) which is a web-based GUI for managing your ZFS setup. Using napp-it I created a pool using both datastore drives. That pool comes out to about 1.4 TB of space. Then I setup that pool to be accessed using NFS. All you have to do after that is add a datastore within ESXi and select NFS, entering the proper information for your OpenIndiana/napp-it/pool setup. When you go to build VMs you can use the NFS datastore and your VMs will be using your ZFS SAN.

This is my first try with ZFS and I know I have a lot to learn about the best way to setup a reliable and fast all-in-one setup, but maybe someone can use this as the start for a cheap whitebox VM lab.

## Some useful links

[napp-it All-in-One guide](http://www.napp-it.org/doc/downloads/all-in-one.pdf)

[HardOCP thread on napp-it](http://hardforum.com/showthread.php?t=1573272&highlight=nappit)

![vsphere](http://cunninghamshane.com/wp-content/uploads/2012/11/vsphere-300x225.png)
