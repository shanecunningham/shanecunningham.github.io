+++
author = "Shane Cunningham"
date = 2012-10-25T15:43:36Z
description = ""
draft = false
slug = "locked-myself-out-of-wordpress"
title = "Locked myself out of Wordpress"

+++


Another booboo I made while moving my Wordpress blog to another server was entirely my own fault, I forgot the administrator password I had setup, myep. Here's a way to manually correct this without using something like phpMyAdmin. I'm assuming you have root access to your web server.

Login to MySQL
<pre><code>mysql -u root -p</code></pre>
<pre><code>SHOW databases;</code></pre>
<pre><code>USE wordpressdb;</code></pre>
<pre><code>SELECT * FROM wp_users;</code></pre>
To get the md5 hash for your password you have a few options, visit this <a href="http://www.miraclesalad.com/webtools/md5.php">md5 Hash Generator</a> or let MySQL do it for you...
<pre><code>UPDATE wp_users SET user_pass='442123aac165e12d65943f3a4114bbf3' WHERE user_login='administrator';</code></pre>
<pre><code>UPDATE wp_users SET user_pass = MD5('"(new-password)"') WHERE user_login='administrator';</code></pre>

You should now be able to login to Wordpress again. <a href="http://codex.wordpress.org/Resetting_Your_Password">Here</a> is a useful article from Wordpress.org covering more ways to reset your admin password.