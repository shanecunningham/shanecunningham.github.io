+++
author = "Shane Cunningham"
date = 2012-06-17T21:40:25Z
description = ""
draft = false
slug = "cifs-vfs-cifs_mount-failed-wreturn-code-22"
title = "CIFS VFS: cifs_mount failed w/return code = -22"

+++


I am constantly forgetting one or more Samba/CIFS packages that are required to mount a Windows network share. The return codes don't really provide very much useful info. Even when searching Google there was not a whole lot for return code -22. For CentOS, I found installing the following package solved my CIFS error.

<pre><code>yum install cifs-utils</code></pre>
