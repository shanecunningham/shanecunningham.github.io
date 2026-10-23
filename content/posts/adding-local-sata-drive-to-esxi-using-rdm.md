---
title: "Adding local SATA drive to VM using RDM"
date: 2012-02-19T14:01:35Z
tags: []
---

My whitebox ESXi build did not go as well as I had hoped. Even though my ASUS M4A88T-M/USB3 motherboard has the IOMMU setting available under Secure Virtual Machine, it does not appear to work. Secure Virtual Machine should allow the motherboard and a compatible AMD-V CPU to passthrough devices directly to the VM using VMWare DirectPath I/O. I needed this since I have 2 x 2 TB hard drives with all of my data that I wanted to use for my fileserver VM. These drives already have data on them and I needed to pass them to the VM without putting any VMFS on the disks.

Solution? Raw Device Mapping (RDM) using local SATA drives.

I followed [this](http://www.vm-help.com/esx40i/SATA_RDMs.php) guide from [vm-help.com](http://vm-help.com). The guide is pretty self explanatory but here's what I did for my system.

**My ESXi whitebox**

ESXi 5 booting from flash drive\
WD 640 GB\
WD 1 TB <- Main Datastore\
WD 2 TB <- Passing this drive to VM\
Samsung 2 TB

**Steps**

You can do this from the ESXi console but it's easier to SSH to the box. You can enable SSH in VSphere -> Configuration -> Security Profile

`ls /dev/disks/ -l`

This will display some info on your disks, the part you're looking for is the highlighted part in the screenshot, notice it correspondes to the WD 2 TB I want to pass to the VM.

![rdm_1](http://cunninghamshane.com/wp-content/uploads/2012/02/rdm_11-1024x135.png)

cd into your datastore directory in `/vmfs/volumes`. Mine was -

```sh
cd /vmfs/volumes/4f3f718d-a3801a12-fea4-001b2181ce29
```

Make a RDMs directory.

```sh
mkdir RDMs
```

Next, create the RDM link using the vml.# from the screenshot.

```sh
vmkfstools -r /vmfs/devices/disks/vml.0100000000202020202057442d574d415a41 30313439383538574443205744 RDM1.vmdk -a lsilogic
```

Now just add a hard disk to the VM and select the RDM1.vmdk file that you just created. When it boots you should be able to initialize it and it will appear as a local hard disk to the VM!

I'm still testing this setup and looking for any funky behavior with using this to access local storage, but it appears to be working. If anyone knows any problems with this setup please comment!
