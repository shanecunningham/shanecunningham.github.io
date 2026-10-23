+++
author = "Shane Cunningham"
date = 2012-10-07T03:34:35Z
description = ""
draft = false
slug = "all-in-one-zfs-solution"
title = "All-in-one ZFS SAN/NAS solution"

+++


Decided to stop using Hyper-V as my main hypervisor and go with ESXi or XenServer full time. Leaning towards ESXi as I know for sure my hardware is compatible. Also, adding an <a href="http://www.servethehome.com/ibm-serveraid-br10i-lsi-sas3082e-r-pciexpress-sas-raid-controller/">IBM BR10i</a> controller flashed to IT mode, removes RAID and is JBOD. Plan to run ESXi/XenServer off a USB drive, use onboard controller for datastore and passthrough the IBM card for NFS access for my VMs. When my <a href="http://www.monoprice.com/products/product.asp?c_id=102&amp;cp_id=10254&amp;cs_id=1025406&amp;p_id=8186&amp;seq=1&amp;format=2">SAS cables</a> come in I plan on going with <a href="http://openindiana.org/">OpenIndiana</a> and <a href="http://www.napp-it.org/">napp-it</a> for an all-in-one ZFS based SAN/NAS. Looking forward to trying it out, will be using <a href="http://www.napp-it.org/doc/downloads/all-in-one.pdf">this</a> guide.

Very long and informative thread <a href="http://hardforum.com/showthread.php?t=1573272&amp;highlight=nappit">here</a>.

&nbsp;