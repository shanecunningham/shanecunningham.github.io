---
title: "Delete blank lines in TextMate"
date: 2011-10-10T15:15:00Z
tags: []
---

Switching to Mac OS X I have noticed opening text files that were created in Windows will add spaces after every line. In TextMate you can create a macro to get rid of the extra lines very easily. In the Bundle Editor add the following command and tie it to a key combination.

```sh
sed /^$/d
```
