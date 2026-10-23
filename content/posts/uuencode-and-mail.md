---
title: "uuencode and mail"
date: 2012-09-08T16:53:05Z
description: "Emailing a file as an attachment with the mail command by piping it through uuencode."
tags: ["linux"]
---

Needed to e-mail an attachement using only mail, after a little Googling I found the following which works great! The first .gz is the file location, the second .gz is what will show up in the body of the email allowing you to download it.

```sh
uuencode accesslogs.gz accesslogs.gz | mail -vs "Access Logs" youremail@blah.com
```
