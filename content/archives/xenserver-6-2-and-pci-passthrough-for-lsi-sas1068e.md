+++
author = "Shane Cunningham"
categories = ["XenServer"]
date = 2013-07-01T01:35:57Z
description = ""
draft = false
slug = "xenserver-6-2-and-pci-passthrough-for-lsi-sas1068e"
tags = ["XenServer"]
title = "XenServer 6.2 and PCI passthrough for LSI SAS1068E"

+++


I had tried to passthrough my LSI SAS1068E to a virtual machine in XenServer 6.0 or 6.1, I forget, but I couldn't get it working for some reason. I didn't troubleshoot it very much though, a few Google searches seemed to point to my whitebox setup and driver/support issues. Recently, XenServer 6.2 was released so I thought I would try this again on my whitebox server. To my surprise I was able to get PCI passthrough working pretty easily on 6.2. For this setup I'm using a XenServer 6.2 host with a LSI SAS1068E card set to IT mode, so RAID is disabled and the card is JBOD, with Ubuntu Server 12.04 as the guest OS using the LSI card and being able to access the drives attached to it.

On your XenServer host run lspci and get the device ID of the device you want to passthrough. Mine was 02:00.0.
<pre><code>lspci
02:00.0 SCSI storage controller: LSI Logic / Symbios Logic SAS1068E PCI-Express Fusion-MPT SAS (rev 08)</code></pre>

Next edit /boot/extlinux.conf and add pciback.hide=(deviceID) to the options and run extlinux -i /boot then reboot the XenServer host.
<pre><code>
vi /boot/extlinux.conf

label xe
  # XenServer
  kernel mboot.c32
  append /boot/xen.gz mem=1024G dom0_max_vcpus=4 dom0_mem=752M,max:752M watchdog_timeout=300 lowmem_emergency_pool=1M crashkernel=64M@32M cpuid_mask_xsave_eax=0 console=vga vga=mode-0x0311 --- /boot/vmlinuz-2.6-xen root=LABEL=root-kgiswlbk ro xencons=hvc console=hvc0 console=tty0 quiet vga=785 splash <b>pciback.hide=(02:00.0)</b> --- /boot/initrd-2.6-xen.img

extlinux -i /boot
reboot now</code></pre>
Now we need to grab the uuid of the VM that you want to passthrough the device to. We need to shut it down to modify the params of the VM. Then we set the paramater to passthrough the device using its device ID.
<pre><code>
xe vm-list
xe vm-shutdown uuid=2b8ea8e5-87cf-326c-704f-2918c63f73af
xe vm-param-set other-config:pci=0/0000:02:00.0 uuid=2b8ea8e5-87cf-326c-704f-2918c63f73af
</code></pre>
Start the VM. After that we can make the required changes to the VM so it can access the device. SSH to the VM and we need to add iommu=soft swiotlb=force to GRUB_CMDLINE_LINUX_DEFAULT, save the changes then run update-grub and reboot.
<pre><code>xe vm-start uuid=2b8ea8e5-87cf-326c-704f-2918c63f73af

vi /etc/default/grub
GRUB_CMDLINE_LINUX_DEFAULT="splash quiet iommu=soft swiotlb=force"
update-grub
reboot now</code></pre>
SSH back into the VM and a fdisk -l should list the drives connected to the LSI card. You can also run lspci on the VM and it should list the LSI card with device ID 00:00.0. This was really easy to get working and it opens a few more possibilities with your infrastructure. Credit to <a href="http://ogris.de/howtos/xen-pci-passthrough.html">this</a> blog post for most of the commands and Google for how to edit Grub2 in Ubuntu Server.