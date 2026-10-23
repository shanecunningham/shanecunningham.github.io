---
title: "ESXi 5 Whitebox"
date: 2011-10-15T07:59:00Z
description: "Hardware list for an ESXi 5 whitebox build, with notes on its NIC support and the free edition's 32GB RAM limit."
tags: ["esxi", "hardware"]
archived: true
---

If you need a whitebox build for ESXi then I have some information that might help. I got ESXi 5 up and running on the following hardware.

**Motherboard**: ASUS M4A88T-M/USB3\
**CPU**: AMD Athlon II X4 620\
**RAM**: G.Skill Value 16GB DDR3 1333\
**NICs**: 2 x Intel 1 x Realtek

With version 5 VMWare added compatibility with a few more network cards. The on-board Realtek 8111E on my ASUS was detected properly and worked fine without having to use special drivers or hacks. Another thing to note with the free ESXi version is VMWare upped the RAM limit to 32GB. They had initially limited it to 8GB but after an outcry from users they raised it, thankfully.
