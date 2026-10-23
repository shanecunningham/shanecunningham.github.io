+++
author = "Shane Cunningham"
date = 2011-06-26T08:46:00Z
description = ""
draft = false
slug = "ubuntu-apt-get-update-fails-with-404"
title = "Ubuntu apt-get-update fails with 404"

+++


I went to update my Nagios server running Ubuntu Server 8.04 and received a 404 error when I tried to update the repositories. Something along the lines of 404 Not Found [IP: xx.xx.xx.xx]. Obviously, 8.04 is EOL so I guess when that happens they also move the official repositories too. Fix it with the following.

Edit <code>/etc/apt/sources.list</code>

Replace all references of <code>archive.ubuntu.com</code> with <code>old-releases.ubuntu.com</code></pre>