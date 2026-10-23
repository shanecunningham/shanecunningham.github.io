+++
author = "Shane Cunningham"
date = 2012-09-08T16:53:05Z
description = ""
draft = false
slug = "uuencode-and-mail"
title = "uuencode and mail"

+++


Needed to e-mail an attachement using only mail, after a little Googling I found the following which works great! The first .gz is the file location, the second .gz is what will show up in the body of the email allowing you to download it.

<pre><code>uuencode accesslogs.gz accesslogs.gz | mail -vs "Access Logs" youremail@blah.com</code></pre>
