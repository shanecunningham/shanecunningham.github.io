---
title: "MySQL - Reset root password and extract table from dump"
date: 2013-03-23T02:06:15Z
tags: ["mysql"]
---

Just a couple MySQL notes.

## Debian 6 Squeeze - Reset MySQL root user password

You'll need to stop MySQL server for resetting it this way.

```sh
service mysqld stop
```

Start MySQL with --skip-grant-tables and send to background. Press enter to get back to command line.

```sh
mysqld_safe --skip-grant-tables &
```

Connect to to MySQL.

```sh
mysql -u root
```

Use mysql database and run the command to update the root user password and flush privileges.

```sql
USE mysql;
UPDATE user SET password=PASSWORD("newrootpassword") WHERE user='root';
```

```sql
FLUSH PRIVILEGES;
```

```sh
service mysqld stop
```

Start MySQL and verify you can now login with the root user.

```sh
service mysqld start
```

```sh
mysql -u root -p
```

## Extract single table from mysqldump file

There are a number of ways to do this with perl, sed, awk etc etc..., but I like scripts and I've successfully used this script before.

```sh
wget http://www.tsheets.com/downloads/oss/extract_sql.pl
```

Make it executable or run with perl and you can run ./extract_sql.pl or perl extract_sql.pl to see the options.

```sh
chmod u+x extract_sql.pl
./extract_sql.pl  or perl extract_sql.pl
```

I ran this to extract the wp_comments table from my Wordpress dump file and send it to a file.

```sh
./extract_sql.pl -t wp_comments -r wordpress.sql > wp_comments_table.sql
```

Now to import the table.

```sh
mysql -u root -p wordpress < wp_comments_table.sql
```

The article with the script and other methods of doing this is [here](http://blog.tsheets.com/2008/tips-tricks/extract-a-single-table-from-a-mysqldump-file.html).
