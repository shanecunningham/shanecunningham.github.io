+++
author = "Shane Cunningham"
date = 2011-11-26T18:14:00Z
description = ""
draft = false
slug = "centos-and-locate"
title = "CentOS and locate"

+++


The following install and daily cron database update need to be done to get locate working.

<pre><code>yum install mlocate
/etc/cron.daily/mlocate.cron</code></pre>
