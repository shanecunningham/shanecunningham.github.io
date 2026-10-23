---
title: "Automate Virtual Hosts creation"
date: 2013-03-24T05:25:54Z
tags: ["lamp"]
---

These tools will help in never having to manually add virtual hosts to your Apache server. Well, maybe not ever, but they will be able to create your virtual hosts in most cases.

[**justcurl.com**](http://justcurl.com)

These tools need to be run on the server you are trying to setup the vhosts on. It will autodetective your Linux distribution and work accordingly.

```sh
bash <( curl -H 'x-docroot: /var/www/vhosts/example.com' -H 'x-port: 80' -H 'host: example.com' justcurl.com )
```

You can set the DocumentRoot, port and ServerName in the options. You can also use this to automagically install Wordpress, but it's still in testing so use with caution.

```sh
bash <( curl -H 'x-docroot: /var/www/vhosts/example.com' -H 'x-port: 80' -H 'x-install: wordpress' -H 'host: example.com' justcurl.com )
```

This is basically the same tool but executed a little differently. There is an excellent post on [community.rackspace.com](https://community.rackspace.com/products/f/25/t/35.aspx) that covers usage. First run this to include all .conf files and create the vhost.d directory in CentOS/RHEL.

```sh
echo "Include vhost.d/*.conf" >> /etc/httpd/conf/httpd.conf && mkdir /etc/httpd/vhost.d
```

CentOS/RHEL

```sh
curl $DOMAIN.c.jonsjava.com | bash
```

Debian/Ubuntu

```sh
curl $DOMAIN.u.jonsjava.com | bash
```

Where $DOMAIN is your virtual host you're trying to create.

```sh
curl example.com.c.jonsjava.com | bash
```
