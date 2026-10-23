---
title: "Locked myself out of Wordpress"
date: 2012-10-25T15:43:36Z
description: "Resetting a forgotten WordPress administrator password by updating the wp_users table directly in MySQL."
tags: ["wordpress", "mysql"]
archived: true
---

Another booboo I made while moving my Wordpress blog to another server was entirely my own fault, I forgot the administrator password I had setup, myep. Here's a way to manually correct this without using something like phpMyAdmin. I'm assuming you have root access to your web server.

Login to MySQL

```sh
mysql -u root -p
```

```sql
SHOW databases;
```

```sql
USE wordpressdb;
```

```sql
SELECT * FROM wp_users;
```

To get the md5 hash for your password you have a few options, visit this [md5 Hash Generator](http://www.miraclesalad.com/webtools/md5.php) or let MySQL do it for you...

```sql
UPDATE wp_users SET user_pass='442123aac165e12d65943f3a4114bbf3' WHERE user_login='administrator';
```

```sql
UPDATE wp_users SET user_pass = MD5('"(new-password)"') WHERE user_login='administrator';
```

You should now be able to login to Wordpress again. [Here](http://codex.wordpress.org/Resetting_Your_Password) is a useful article from Wordpress.org covering more ways to reset your admin password.
