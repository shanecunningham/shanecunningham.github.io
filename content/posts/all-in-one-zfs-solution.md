---
title: "All-in-one ZFS SAN/NAS solution"
date: 2012-10-07T03:34:35Z
description: "Planning an all-in-one ZFS SAN/NAS with OpenIndiana and napp-it, using an IBM BR10i flashed to IT mode and ESXi or XenServer."
tags: ["zfs", "esxi"]
archived: true
---

Decided to stop using Hyper-V as my main hypervisor and go with ESXi or XenServer full time. Leaning towards ESXi as I know for sure my hardware is compatible. Also, adding an [IBM BR10i](http://www.servethehome.com/ibm-serveraid-br10i-lsi-sas3082e-r-pciexpress-sas-raid-controller/) controller flashed to IT mode, removes RAID and is JBOD. Plan to run ESXi/XenServer off a USB drive, use onboard controller for datastore and passthrough the IBM card for NFS access for my VMs. When my [SAS cables](http://www.monoprice.com/products/product.asp?c_id=102&cp_id=10254&cs_id=1025406&p_id=8186&seq=1&format=2) come in I plan on going with [OpenIndiana](http://openindiana.org/) and [napp-it](http://www.napp-it.org/) for an all-in-one ZFS based SAN/NAS. Looking forward to trying it out, will be using [this](http://www.napp-it.org/doc/downloads/all-in-one.pdf) guide.

Very long and informative thread [here](http://hardforum.com/showthread.php?t=1573272&highlight=nappit).
