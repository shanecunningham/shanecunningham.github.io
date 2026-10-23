---
title: "CIFS VFS: cifs_mount failed w/return code = -22"
date: 2012-06-17T21:40:25Z
description: "On CentOS, installing the cifs-utils package fixes the CIFS VFS cifs_mount failed error with return code -22 when mounting a Windows share."
tags: ["linux", "windows"]
archived: true
---

I am constantly forgetting one or more Samba/CIFS packages that are required to mount a Windows network share. The return codes don't really provide very much useful info. Even when searching Google there was not a whole lot for return code -22. For CentOS, I found installing the following package solved my CIFS error.

```sh
yum install cifs-utils
```
