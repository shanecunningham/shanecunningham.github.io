---
title: "Windows Update Error - Code 80073712"
date: 2010-08-27T01:26:36Z
description: "Using Microsoft Fix it 50202 to reset Windows Update components when updates fail with error 80073712."
tags: ["windows"]
archived: true
---

My main desktop PC was dormant for some time and I recently just got it back up. When I tried to install all the Windows Updates that had accumulated I started to receive error Code 80073712. After trying to install them multiple times I Googled the error code but found the solutions did not help. [This](http://www.windowsreference.com/windows-vista/fix-for-vista-sp1-install-error-80073712-through-windows-update/) fix didn’t help since I didn’t have the pending.xml file on my system.

After some more searching I found a free tool from Microsoft that fixed my problems. [Microsoft Fix it 50202](http://support.microsoft.com/kb/971058) will reset your Windows Update components. I ran the default fix but you can also run an Aggressive mode too. I had to search for new updates a couple times after running it but eventually I was able to install all the Windows Updates.
