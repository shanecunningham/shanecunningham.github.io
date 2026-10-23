+++
author = "Shane Cunningham"
date = 2010-09-11T15:36:50Z
description = ""
draft = false
slug = "convert-vmware-server-2-disks"
title = "Convert VMware Server 2 disks"

+++


Tested using .vmdk created in VMware Server 2, converted to .vhd and successfully ran in Microsoft Hyper-V R2. No settings to change unless you converted a Linux VM, probably will have to add legacy NIC driver to Hyper-V to get connectivity.

<a href="http://vmtoolkit.com/blogs/announcements/archive/2006/11/20/vmdk-to-vhd-converter-available.aspx" target="_blank">Vmdk2Vhd 1.0.13: 2/13/2006</a>