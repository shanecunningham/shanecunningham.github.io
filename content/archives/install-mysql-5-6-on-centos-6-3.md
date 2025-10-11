+++
author = "Shane Cunningham"
categories = ["MySQL"]
date = 2013-02-14T07:36:21Z
description = ""
draft = false
slug = "install-mysql-5-6-on-centos-6-3"
tags = ["MySQL"]
title = "Install MySQL 5.6 on CentOS 6.3"

+++


No guarantee this works or that it won't completely blow up your system.
<pre><code>wget http://dev.mysql.com/get/Downloads/MySQL-5.6/MySQL-server-5.6.10-1.el6.x86_64.rpm/from/http://cdn.mysql.com/
wget http://dev.mysql.com/get/Downloads/MySQL-5.6/MySQL-client-5.6.10-1.el6.x86_64.rpm/from/http://cdn.mysql.com/</code></pre>
libaio is required so install that bad boy.
<pre><code>yum install libaio</code></pre>
To make this work you need to remove mysql-libs-5.1.61-4.el6.x86_64 which also removes a few other things, please make sure you are ok with these things being removed. The programs removed are cronie, cronie-anacron, crontabs and postfix.
<pre><code>yum remove mysql-libs-5.1.61-4.el6.x86_64</code></pre>
Install MySQL 5.6.
<pre><code>rpm -ivh MySQL-server-5.6.10-1.el6.x86_64.rpm
rpm -ivh MySQL-client-5.6.10-1.el6.x86_64.rpm</code></pre>
Now start MySQL.
<pre><code>service mysql start</code></pre>
Notice even though this is CentOS, which usually uses service mysqld start, it's just mysql for some reason when installing this way.

*Should* have a working MySQL 5.6 install on CentOS 6.3.