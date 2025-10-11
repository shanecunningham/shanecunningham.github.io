+++
author = "Shane Cunningham"
categories = ["LAMP"]
date = 2013-03-24T05:25:54Z
description = ""
draft = false
slug = "automate-virtual-hosts-creation"
tags = ["LAMP"]
title = "Automate Virtual Hosts creation"

+++


These tools will help in never having to manually add virtual hosts to your Apache server. Well, maybe not ever, but they will be able to create your virtual hosts in most cases.
<p style="padding-left: 30px;"><a href="http://justcurl.com"><strong>justcurl.com</strong></a></p>
These tools need to be run on the server you are trying to setup the vhosts on. It will autodetective your Linux distribution and work accordingly.
<pre><code>bash &lt;( curl -H 'x-docroot: /var/www/vhosts/example.com' -H 'x-port: 80' -H 'host: example.com' justcurl.com )</code></pre>
You can set the DocumentRoot, port and ServerName in the options. You can also use this to automagically install Wordpress, but it's still in testing so use with caution.
<pre><code>bash &lt;( curl -H 'x-docroot: /var/www/vhosts/example.com' -H 'x-port: 80' -H 'x-install: wordpress' -H 'host: example.com' justcurl.com )</code></pre>

This is basically the same tool but executed a little differently. There is an excellent post on <a href="https://community.rackspace.com/products/f/25/t/35.aspx">community.rackspace.com</a> that covers usage. First run this to include all .conf files and create the vhost.d directory in CentOS/RHEL.
<pre><code>echo "Include vhost.d/*.conf" &gt;&gt; /etc/httpd/conf/httpd.conf &amp;&amp; mkdir /etc/httpd/vhost.d</code></pre>
CentOS/RHEL
<pre><code>curl $DOMAIN.c.jonsjava.com | bash</code></pre>
Debian/Ubuntu
<pre><code>curl $DOMAIN.u.jonsjava.com | bash</code></pre>
Where $DOMAIN is your virtual host you're trying to create.
<pre><code>curl example.com.c.jonsjava.com | bash</code></pre>
<p style="padding-left: 30px;"></p>