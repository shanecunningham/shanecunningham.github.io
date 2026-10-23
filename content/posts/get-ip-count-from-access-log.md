+++
author = "Shane Cunningham"
date = 2012-08-15T00:11:01Z
description = ""
draft = false
slug = "get-ip-count-from-access-log"
title = "Get IP count from access log"

+++


This will list the IP and number of times that it appears in your access log if more than once.

<pre><code>awk '{!a[$1]++}END{for(i in a) if ( a[i] &gt;1 ) print a[i],i }' /var/pathtoyour/access.log | sort -n</code></pre>

If you only want it to show the IP if it appears, for example, more than 10 times change a[i] &gt;1 to a[i] &gt;10.