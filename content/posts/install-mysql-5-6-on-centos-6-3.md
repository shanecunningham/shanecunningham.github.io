---
title: "Install MySQL 5.6 on CentOS 6.3"
date: 2013-02-14T07:36:21Z
description: "Installing MySQL 5.6.10 server and client RPMs on CentOS 6.3, after removing mysql-libs and installing libaio."
tags: ["mysql", "linux"]
archived: true
---

No guarantee this works or that it won't completely blow up your system.

```sh
wget http://dev.mysql.com/get/Downloads/MySQL-5.6/MySQL-server-5.6.10-1.el6.x86_64.rpm/from/http://cdn.mysql.com/
wget http://dev.mysql.com/get/Downloads/MySQL-5.6/MySQL-client-5.6.10-1.el6.x86_64.rpm/from/http://cdn.mysql.com/
```

libaio is required so install that bad boy.

```sh
yum install libaio
```

To make this work you need to remove mysql-libs-5.1.61-4.el6.x86_64 which also removes a few other things, please make sure you are ok with these things being removed. The programs removed are cronie, cronie-anacron, crontabs and postfix.

```sh
yum remove mysql-libs-5.1.61-4.el6.x86_64
```

Install MySQL 5.6.

```sh
rpm -ivh MySQL-server-5.6.10-1.el6.x86_64.rpm
rpm -ivh MySQL-client-5.6.10-1.el6.x86_64.rpm
```

Now start MySQL.

```sh
service mysql start
```

Notice even though this is CentOS, which usually uses service mysqld start, it's just mysql for some reason when installing this way.

*Should* have a working MySQL 5.6 install on CentOS 6.3.
