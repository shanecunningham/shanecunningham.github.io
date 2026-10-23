+++
author = "Shane Cunningham"
date = 2011-06-12T10:15:00Z
description = ""
draft = false
slug = "use-putty-to-connect-to-amazon-ec2"
title = "Use PuTTY to connect to Amazon EC2"

+++


Another I&#8217;m going to post because I&#8217;ll forget&#8230;I was messing around with Amazon EC2 and had some minor issues connecting using SSH and PuTTY. Here are the simple steps I used to connect to a CentOS EC2 instance.

Open SSH in the Security Groups section of AWS Management Console.

Download <a href="http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html" target="_blank">PuTTY and PuTTYgen</a>. Open PuTTYgen and load the .pem key you downloaded from Amazon when you created the instance.

Save private key as &#8220;id_rsa-gsg-keypair.ppk&#8221;, ignore pass phrase prompt.

Open a command prompt and cd to the directory where your putty.exe is located.

<pre><code>putty.exe -i id_rsa-gsg-keypair.ppk root@your-amazon-public-dns.amazonaws.com</code></pre>

&#8220;your-amazon-public-dns.amazonaws.com&#8221; is your own public DNS address that you can get from AWS Management Console under Instance Actions -&gt; Connect.

You could of course use the PuTTY GUI and select the .ppk file.

I could login is a root with CentOS, but I&#8217;ve read this might be ec2-user or something else depending on the EMI you are using.