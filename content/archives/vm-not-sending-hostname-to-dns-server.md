+++
author = "Shane Cunningham"
date = 2013-02-13T07:23:18Z
description = ""
draft = false
slug = "vm-not-sending-hostname-to-dns-server"
title = "VM not sending hostname to DNS/DHCP server"

+++


On some VMs I spin up on ESXi the hostname is not sent to my DNS/DHCP server running in pfSense. Haven't found exactly why because it seems occasionally Ubuntu VMs do send this correctly on first boot. I'm probably doing something not smart. Anyway, you can easily fix this problem by adding the following -

<strong>CentOS/Ubuntu</strong>
Add this to /etc/sysconfig/network

<pre><code>DHCP_HOSTNAME=hostname</code></pre>
Replace hostname with your servers hostname and restart networking. It should now send the hostname to your DNS/DHCP server.