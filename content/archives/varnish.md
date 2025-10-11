+++
author = "Shane Cunningham"
categories = ["MySQL"]
date = 2013-03-23T02:06:15Z
description = ""
draft = false
slug = "varnish"
tags = ["MySQL"]
title = "MySQL - Reset root password and extract table from dump"

+++


Just a couple MySQL notes.

<strong>Debian 6 Squeeze - Reset MySQL root user password</strong>

You'll need to stop MySQL server for resetting it this way.
<pre><code>service mysqld stop</code></pre>
Start MySQL with --skip-grant-tables and send to background. Press enter to get back to command line.
<pre><code>mysqld_safe --skip-grant-tables &amp;</code></pre>
Connect to to MySQL.
<pre><code>mysql -u root</code></pre>
Use mysql database and run the command to update the root user password and flush privileges.
<pre><code>USE mysql;
UPDATE user SET password=PASSWORD("newrootpassword") WHERE user='root';</code></pre>
<pre><code>FLUSH PRIVILEGES;</code></pre>
<pre><code>service mysqld stop</code></pre>
Start MySQL and verify you can now login with the root user.
<pre><code>service mysqld start</code></pre>
<pre><code>mysql -u root -p</code></pre>
<strong>Extract single table from mysqldump file.</strong>

There are a number of ways to do this with perl, sed, awk etc etc..., but I like scripts and I've successfully used this script before.
<pre><code>wget http://www.tsheets.com/downloads/oss/extract_sql.pl</code></pre>
Make it executable or run with perl and you can run ./extract_sql.pl or perl extract_sql.pl to see the options.
<pre><code>chmod u+x extract_sql.pl
./extract_sql.pl  or perl extract_sql.pl</code></pre>
I ran this to extract the wp_comments table from my Wordpress dump file and send it to a file.
<pre><code>./extract_sql.pl -t wp_comments -r wordpress.sql &gt; wp_comments_table.sql</code></pre>
Now to import the table.
<pre><code>mysql -u root -p wordpress &lt; wp_comments_table.sql</code></pre>
The article with the script and other methods of doing this is <a href="http://blog.tsheets.com/2008/tips-tricks/extract-a-single-table-from-a-mysqldump-file.html">here</a>.