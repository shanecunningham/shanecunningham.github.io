+++
author = "Shane Cunningham"
date = 2014-04-04T10:05:25Z
description = ""
draft = false
slug = "moved-to-ghost"
title = "Moved to Ghost"

+++


A couple days ago I moved my blog from Wordpress to [Ghost](http://ghost.org/). I found the the easiest way to get a full stack Ghost blog running is to use the [Rackspace Ghost Deployment](http://developer.rackspace.com/blog/launch-ghost-with-rackspace-deployments.html). The current version of the deployment comes with a full stack consisting of Ubuntu Server 12.04 LTS, Ghost 0.4, node.js 0.10.21, MySQL 5.5 and nginx 1.4.4 acting as the web server passing requests back to node.js.

I run off of a 1GB Performance Cloud Server. I don't use the included MySQL setup, instead I use a [Cloud Database](http://www.rackspace.com/cloud/databases/) with 512MB RAM - 2GB storage as the backend database and [Mailgun](http://mailgun.com "Mailgun") to send emails. To use an external database and your own SMTP settings just make the following changes to `/var/www/vhosts/yourdomain.com/ghost/config.js`. 
<pre><code>
database: {
   client: 'mysql',
   connection: {
       host: 'da0f24b528ca412fab262e0be497f8f462f7da1a.rackspaceclouddb.com',
       user: 'username',
       password: 'password',
       database: 'database',
       charset: 'utf8'
   },
   debug: false
},

mail: {
   transport: 'SMTP',
   options: {
   service: 'Mailgun',
       auth: {
           user: 'postmaster@yourdomain.com',
           pass: 'password'
       }
   }
},
</code></pre>

I like monitoring, logging and graphing things. With [Cloud Monitoring](http://www.rackspace.com/cloud/monitoring/) this makes all of that easy. I have a Cloud Monitoring check setup for my site and it automatically graphs this data (1 hr, 8hr, 24hr, week and month views) from the Rackspace control panel or the beta (awesome) service named [Cloud Intelligence](https://intelligence.rackspace.com). The following is my monitoring data provided by Cloud Monitoring and Cloud Intelligence after I switched to Ghost. Notice the improvement. :)

![Graph 1](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/intel_graph_3.png)
![Graph 2](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/intel_graph_1.png)
![Graph 3](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/intel_graph_2.png)