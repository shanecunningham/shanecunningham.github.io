+++
author = "Shane Cunningham"
date = 2012-04-05T02:43:03Z
description = ""
draft = false
slug = "custom-built-pfsense-router"
title = "My pfSense firewall/router build"

+++


I stuck with a D-Link DIR-625 wireless router doing all my routing for entirely too long. I had an old P4 2.66 GHz PC laying around with a 40GB hard drive so I decided to try out <a title="pfSense" href="http://www.pfsense.org">pfSense</a>. I was hooked, the overall performance and features of this open source FreeBSD firewall/router were impressive. My old P4 machine was using too much electricity for something that was on 24 x 7, though. I decided to custom build something that was 1. powerful enough for my home network and virtual environment lab 2. low power draw 3. quite.

I settled on these parts. Newegg sells this as a <a href="http://www.newegg.com/Product/Product.aspx?Item=N82E16816101364">barebones server</a> but I found I saved about $60 buying the parts separately and assembling myself.
<ul>
	<li>Chassis: <a href="http://www.newegg.com/Product/Product.aspx?Item=N82E16811152131">SUPERMICRO CSE-502L-200B</a></li>
	<li>Motherboard &amp; CPU: <a href="http://www.newegg.com/Product/Product.aspx?Item=N82E16813182243">SUPERMICRO MBD-X7SPE-HF-D525-O</a></li>
	<li>RAM: 2 x 2GB DDR3 1066</li>
	<li>Boot Drive: <a href="http://www.newegg.com/Product/Product.aspx?Item=N82E16820239005">Kingston DataTraveler Micro 8GB</a></li>
</ul>
The chassis is a nice 1U server case. The motherboard and CPU come as one so no mounting needed, it's also fanless! The CPU is a dual core Atom D525 with Hyper-Threading running at 1.8GHz. For the RAM I used two sticks that were in my MacBook Pro, with RAM so cheap decided to upgrade my Pro to 8GB. I probably could have used 2GB with the load I'll be putting on it. This motherboard has an onboard USB Type A next to the SATA connectors so I just connected the micro USB flash drive and used that as my boot device. What I really like about this motherboard is it has two Intel 82574L NIC's, IPMI 2.0, low power draw and plenty powerful for what I need.

Install went great over IPMI using <a href="ftp://ftp.supermicro.com/utility/IPMIView/">IPMIView</a>, even on OS X! I have pfSense routing all of my home network, but it's still a basic setup and I still have to implement VLANs with my HP 1810-8G switch.

My only (slight) complaint is the PSU included in the server case has a slight whine to it. It's not as quite as I would have liked but not horrible either. When it's in my closet I can only hear it if it's dead quite and I get right next to the door. Also, IPMI shares one of the NIC's and I'm having trouble connecting to it after installing pfSense since it's now handing out IP's. I hope to figure that out soon, but other than that I think this is a good basis for a firewall/router.