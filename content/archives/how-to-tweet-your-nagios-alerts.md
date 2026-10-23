+++
author = "Shane Cunningham"
categories = ["Nagios"]
date = 2011-12-13T06:14:18Z
description = ""
draft = false
slug = "how-to-tweet-your-nagios-alerts"
tags = ["Nagios"]
title = "How to Tweet your Nagios alerts"

+++


I don’t know how truly useful this is, but it’s kinda cool just for the geekiness.

I installed this on Ubuntu Server 9.04 running Nagios 3.1.2. You will want to create a Twitter account just for sending these tweets. Setup a new account and go to https://dev.twitter.com and login with the Twiiter account you will be sending tweets from. Next, create a new application. After that you need to create Access Tokens for the application, you may have to refresh a bit to receive the tokens.

If you don’t have python installed you may have to do the following.
<pre><code>apt-get install python-setuptools</code></pre>
Otherwise, install tweepy which is the python program we use to tweet the Nagios alerts.
<pre><code>easy_install tweepy</code></pre>
Next create the file we will be using to tweet. I did…
<pre><code>vi tweet</code></pre>
Paste the follow using your own `CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET` from the Twitter account you setup.
<pre><code>#!/usr/bin/env python
#
#
import sys
import tweepy
CONSUMER_KEY = 'paste Consumer Key here'
CONSUMER_SECRET = 'paste Consumer Secret here'
ACCESS_KEY = 'paste Access Key here'
ACCESS_SECRET = 'paste Access Secret here'
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth) api.update_status(sys.argv[1])</code></pre>
Next make it executable.
<pre><code>chmod +x tweet</code></pre>
Now, send a test tweet.
<pre><code>./tweet "Hello, World!"</code></pre>
Now go to your Twitter account and if your access keys and secrets are correct, a tweet should have been posted.

<strong>Setup the Nagios part </strong>

Edit your contact.cfg file with the following.

<pre><code>define contact{
contact_name twitter
alias Twitter Bot
service_notification_period 24x7
host_notification_period 24x7
service_notification_options w,u,c,r
host_notification_options d,r
service_notification_commands notify-by-twitter
host_notification_commands host-notify-by-twitter
email dummy@example.com
}</code></pre>

Add twitter to your contacts group. You should already have this part in your contacts.cfg file and would only need to add ‘twitter’ to the members section. But here it is just in case.

<pre><code>define contactgroup{
contactgroup_name admins
alias Nagios Administrators
members admin,twitter
}</code></pre>

Add the follow to your commands.cfg file. I have mine running from /home/nagios/tweepy/. Change yours as needed. Also, change ‘@TwitterAccount’ to whatever Twitter account you want to mention in the tweet. I use my main Twitter account because it’s easier to notice if you have a mention rather than just skimming your Timeline.

<pre><code> ### Twitter ###

define command{
command_name host-notify-by-twitter
command_line /home/nagios/tweepy/tweet "@TwitterAccount $HOSTALIAS$ is $HOSTSTATE$. $HOSTOUTPUT$. Time: $SHORTDATETIME$"
}

define command{
command_name notify-by-twitter
command_line <span>/home/nagios/tweepy/tweet</span><span> "@TwitterAccount $SERVICEDESC$ @ $HOSTNAME$ is $SERVICESTATE$. $SERVICEOUTPUT$. Time: $SHORTDATETIME$"
}</code></pre></span>

Let me know how this goes for you!