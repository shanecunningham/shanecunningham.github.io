---
title: "Windows VM loses time sync"
date: 2012-09-15T16:19:14Z
description: "Fixing Windows VMs on Hyper-V Server 2012 that had a three-day time offset by toggling Time Synchronization in Integration Services."
tags: ["windows", "virtualization"]
archived: true
---

I experienced a weird time sync issue today with my Windows VMs. I went to stream something to my PS3 from a network share, but I received an error. I thought the share had just lost connection and I needed to reconnect it. When I tried that I received a couple errors, extended error or something and an error stating the time in Windows was different than the server I was trying to connect to. That's when I noticed the date being reported was 9/12/12, which was 3 days behind. I logged into my DC and tried to sync with a couple Internet time servers, but those still resulted in a date that was 3 days behind. Manually changing the time and date resulted in Windows completely ignoring what I entered and going back to 9/12/12.

I have Hyper-V running on Windows Server 2012. I had to log in to my Hyper-V server and go to each VM settings > Integration Services > uncheck Time Synchronization > Apply, then check Time Synchronization > Apply. This fixed all the VMs and they started pulling the correct date and time from the Internet time servers. I've read about time sync issues in virtual machines but I had never had an issue before today. I'll keep an eye out if this is a bug with Windows Server 2012, Hyper-V or Integration Services.
