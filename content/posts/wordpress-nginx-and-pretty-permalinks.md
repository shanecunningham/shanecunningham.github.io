---
title: "Wordpress, Nginx and Pretty Permalinks"
date: 2012-10-24T15:19:21Z
tags: []
---

The only issue I had with moving my blog from Apache to Nginx was with pretty permalinks. Installation and setup was very easy. I used [this](http://www.rackspace.com/knowledge_center/article/installing-nginx-and-php-fpm-running-on-unix-file-sockets) guide from Rackspace Knowledge Center. Add in MySQL server after setting up Nginx, PHP-FPM and you're all set. My server now uses much less RAM and is better suited for serving my static content.

When I first had everything setup, I could login to Wordpress dashboard and make edits to my site, but when I tried visiting any links I received 404 errors. After some Googling and trying a couple solutions it still was not working. I finally found the simple solution below, it's on the [Official Nginx Wiki](http://wiki.nginx.org/WordPress) (should have gone there first!).

Add this to your location /

```text
try_files $uri $uri/ /index.php;
```
