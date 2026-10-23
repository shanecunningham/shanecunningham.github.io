---
title: "Analyze Apache and MySQL configurations"
date: 2013-03-24T04:04:18Z
tags: ["lamp"]
---

I use these two tools pretty often and thought I would mention them here. They analyze your Apache and MySQL configurations and make general recommendations. That doesn't mean you need to follow these, but they are good at showing you overviews of your configs that you can use in addition to other data to make configuration change decisions.

[**Apachebuddy.pl**](https://github.com/gusmaskowitz/apachebuddy.pl)

This is a one liner you can use to run apachebuddy.pl, it will analyze your currently running Apache processes and configurations, how much memory they are using and how much memory you have on the server to make recommendations. Run as root.

```text
perl <( curl http://cloudfiles.fanatassist.com/apachebuddy.pl )
```

If you have issues with that oneliner, just wget using the URL above, make it executable and run. If you have Varnish on port 80 and Apache on 8080 you can also specify which port apachebuddy.pl is run against with the following.

```text
perl <( curl http://cloudfiles.fanatassist.com/apachebuddy.pl -p 8080 )
```

[**MySQLTuner.pl**](http://mysqltuner.pl)

This is a very popular MySQL tuning script from [Major Hayden](http://rackerhacker.com). Once again, these are just recommendations so make sure you understand the changes you make based on the recommendations MySQLTuner provides.

```sh
wget https://raw.github.com/major/MySQLTuner-perl/master/mysqltuner.pl && perl mysqltuner.pl
```

If you use any tools to analyze systems please let me know!
