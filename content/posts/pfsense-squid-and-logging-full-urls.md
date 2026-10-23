---
title: "pfSense, Squid and logging full URLs"
date: 2012-11-02T04:18:41Z
tags: ["pfsense"]
---

By default the Squid package that pfSense installs will cut off the URLs if they are longer than a certain length. If you want it to log the full URL, add this to your squid.conf file. The config file says not to manually edit it, but I inserted this and restarted squid and everything continued working.

```text
strip_query_terms off
```
