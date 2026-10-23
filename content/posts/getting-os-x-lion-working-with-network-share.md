+++
author = "Shane Cunningham"
date = 2011-10-08T08:44:00Z
description = ""
draft = false
slug = "getting-os-x-lion-working-with-network-share"
title = "Getting OS X Lion working with network share"

+++


<p>Mac OS X Lion broke the ability for Time Machine to backup to a network share over Samba. I usually backup everything to a Windows Server 2008 R2 computer running headless in my closet, but OS X Lion will not connect any longer due to AFP 3.3 being used. I still haven&#8217;t found a way for my iMac to connect directly to the server but I have a workaround that might work for you. </p>
<p>I setup a Ubuntu Server 11.04 virtual machine that uses Netatalk and Avahi to be seen and share with Time Machine. Netatalk must be version 2.2 or greater. </p>
<p>Follow <a href="http://beacon.wharton.upenn.edu/davekonopka/2011/07/connect-os-x-lion-time-machine-to-a-network-drive/" target="_blank">this guide</a>, if that doesn&#8217;t install the correct Netatalk version, try <a href="http://tomasz.korwel.net/2011/07/21/ubuntu-nas-vs-os-x-lion-10-7/" target="_blank">this</a>, it will install a beta version that I was able to get working. </p>
<p>Let me know if you have any issues with these links or have a more efficient way for OS X Lion and Time Machine to backup to a network share!</p>