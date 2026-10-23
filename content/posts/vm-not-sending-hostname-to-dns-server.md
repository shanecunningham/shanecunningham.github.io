---
title: "VM not sending hostname to DNS/DHCP server"
date: 2013-02-13T07:23:18Z
description: "Setting DHCP_HOSTNAME in /etc/sysconfig/network so a Linux VM sends its hostname to the DHCP/DNS server."
tags: ["networking", "linux", "virtualization"]
archived: true
---

On some VMs I spin up on ESXi the hostname is not sent to my DNS/DHCP server running in pfSense. Haven't found exactly why because it seems occasionally Ubuntu VMs do send this correctly on first boot. I'm probably doing something not smart. Anyway, you can easily fix this problem by adding the following -

**CentOS/Ubuntu**\
Add this to /etc/sysconfig/network

```text
DHCP_HOSTNAME=hostname
```

Replace hostname with your servers hostname and restart networking. It should now send the hostname to your DNS/DHCP server.
