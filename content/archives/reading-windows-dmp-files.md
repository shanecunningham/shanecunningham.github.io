+++
author = "Shane Cunningham"
date = 2011-09-03T05:02:00Z
description = ""
draft = false
slug = "reading-windows-dmp-files"
title = "Reading Windows .DMP files"

+++


A few months ago I needed to read some .DMP files and realized that I didn&#8217;t know how. I can troubleshoot fairly well and I have always figured things out without needing to go into the dump files. I knew this particular problem was hardware related but I wanted to see what the dump files had to say anyways. It seems kind of strange that Microsoft creates these files when things go bad but makes it difficult to obtain useful information from them. After some Googling I found the following, hope it helps.

Download <a href="http://msdn.microsoft.com/en-us/windows/hardware/gg463009" target="_blank">Debugging Tools for Windows</a>
Open WinDBG and open the .DMP file you want to analyze.
Enter the following commands.

<pre>.symfix
.reload
!analyze -v</pre>

You should be able to decipher what is causing the crashes. If you prefer something a little more automated check out <a href="http://www.nirsoft.net/utils/blue_screen_view.html" target="_blank">BlueScreenView</a>.