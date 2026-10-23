---
title: "Ubuntu apt-get-update fails with 404"
date: 2011-06-26T08:46:00Z
tags: []
---

I went to update my Nagios server running Ubuntu Server 8.04 and received a 404 error when I tried to update the repositories. Something along the lines of 404 Not Found [IP: xx.xx.xx.xx]. Obviously, 8.04 is EOL so I guess when that happens they also move the official repositories too. Fix it with the following.

Edit `/etc/apt/sources.list`

Replace all references of `archive.ubuntu.com` with `old-releases.ubuntu.com`
