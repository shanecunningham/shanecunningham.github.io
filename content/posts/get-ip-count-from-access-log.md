---
title: "Get IP count from access log"
date: 2012-08-15T00:11:01Z
tags: []
---

This will list the IP and number of times that it appears in your access log if more than once.

```sh
awk '{!a[$1]++}END{for(i in a) if ( a[i] >1 ) print a[i],i }' /var/pathtoyour/access.log | sort -n
```

If you only want it to show the IP if it appears, for example, more than 10 times change a[i] >1 to a[i] >10.
