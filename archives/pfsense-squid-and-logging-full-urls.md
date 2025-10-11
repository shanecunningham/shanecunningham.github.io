+++
author = "Shane Cunningham"
categories = ["pfSense"]
date = 2012-11-02T04:18:41Z
description = ""
draft = false
slug = "pfsense-squid-and-logging-full-urls"
tags = ["pfSense"]
title = "pfSense, Squid and logging full URLs"

+++


By default the Squid package that pfSense installs will cut off the URLs if they are longer than a certain length. If you want it to log the full URL, add this to your squid.conf file. The config file says not to manually edit it, but I inserted this and restarted squid and everything continued working.

<pre><code>strip_query_terms off</code></pre>