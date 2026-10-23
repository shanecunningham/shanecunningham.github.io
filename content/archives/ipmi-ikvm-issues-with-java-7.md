+++
author = "Shane Cunningham"
date = 2013-05-23T05:40:38Z
description = ""
draft = false
slug = "ipmi-ikvm-issues-with-java-7"
title = "IPMI & iKVM issues with Java 7"

+++


Recently I made the mistake of turning off my 1U SuperMicro router running <a href="http://pfsense.com/">pfSense</a> because we were going on a short vacation. Of course, when I came back and turned it back on I came across some nasty DMA disk errors and a read-only filesystem. No matter what I tried with fsck and remounting could fix these errors. I had my configs saved so I decided to just try a reinstall of pfSense 2.03. One cool thing about my SuperMicro board is the IPMI that's built in. On my Mac I use <a href="http://www.supermicro.com/products/nfo/ipmi.cfm">IPMIview</a> and the web interface IPMI provides to connect. Connecting with both worked fine, checking system status, all the power functions  and iKVM worked for console redirection.

The only thing I could not get working was the Virtual Storage function where you can boot the server from an .iso located on your local machine. Really cool feature. I used it to install the original pfSense I had on the server, but that was awhile ago. Every time I went to open the dialog box where you can select the .iso in your filesystem, it would hang and crash iKVM. I did some Google digging and it seemed to point to Java 7 being the issue. I decided to fire up VirtualBox, get a Windows VM running and install Java 6 and run iKVM from the IPMI web interface.  Sure enough selecting the .iso worked fine with Java 6. So if you are having issues with Virtual Storage and Java 7, run Java 6 in a VM.