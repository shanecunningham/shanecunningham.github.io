---
title: "CentOS and locate"
date: 2011-11-26T18:14:00Z
description: "Installing mlocate on CentOS and running its daily cron script to build the locate database."
tags: ["linux"]
archived: true
---

The following install and daily cron database update need to be done to get locate working.

```sh
yum install mlocate
/etc/cron.daily/mlocate.cron
```
