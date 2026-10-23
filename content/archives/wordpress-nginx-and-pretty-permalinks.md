+++
author = "Shane Cunningham"
date = 2012-10-24T15:19:21Z
description = ""
draft = false
slug = "wordpress-nginx-and-pretty-permalinks"
title = "Wordpress, Nginx and Pretty Permalinks"

+++


The only issue I had with moving my blog from Apache to Nginx was with pretty permalinks. Installation and setup was very easy. I used <a href="http://www.rackspace.com/knowledge_center/article/installing-nginx-and-php-fpm-running-on-unix-file-sockets">this</a> guide from Rackspace Knowledge Center. Add in MySQL server after setting up Nginx, PHP-FPM and you're all set. My server now uses much less RAM and is better suited for serving my static content.

When I first had everything setup, I could login to Wordpress dashboard and make edits to my site, but when I tried visiting any links I received 404 errors. After some Googling and trying a couple solutions it still was not working. I finally found the simple solution below, it's on the <a href="http://wiki.nginx.org/WordPress">Official Nginx Wiki</a> (should have gone there first!).

Add this to your location /

<pre><code>try_files $uri $uri/ /index.php;</code></pre>
