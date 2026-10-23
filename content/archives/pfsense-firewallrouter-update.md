+++
author = "Shane Cunningham"
date = 2012-04-14T14:52:21Z
description = ""
draft = false
slug = "pfsense-firewallrouter-update"
title = "pfSense firewall/router update"

+++


I had some issues with accessing IPMI in my <a title="My pfSense firewall/router build" href="http://cunninghamshane.com/?p=178">pfSense</a> build. It seemed like if I let pfSense boot up and I was not accessing IPMI at the same time, pfSense would take over the whole NIC and not let me access IPMI. I read <a href="http://forum.pfsense.org/index.php/topic,28238.0.html">here</a> that this is normal to not be able to access IPMI once pfSense boots but that defeats the whole purpose of IPMI so I don't think the system should behave in that way. After messing with it for a few days all I can say is IPMI seems really finicky when sharing a NIC, or maybe I'm doing something goofy.

I had planned on doing a dedicated IPMI NIC anyway so I bought a cheap Supermicro riser card RSC RR1U-E16. I then hooked my LAN to the Intel PCI-Express NIC that I connected to the riser card. In the BIOS I set a static IP for the IPMI NIC and it has been stable since. I would still recommend this combo for a low power firewall/router build.