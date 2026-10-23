---
title: "Reading Windows .DMP files"
date: 2011-09-03T05:02:00Z
description: "Opening a Windows .DMP crash dump in WinDbg and running .symfix, .reload and !analyze -v to find the crash cause."
tags: ["windows"]
---

A few months ago I needed to read some .DMP files and realized that I didn’t know how. I can troubleshoot fairly well and I have always figured things out without needing to go into the dump files. I knew this particular problem was hardware related but I wanted to see what the dump files had to say anyways. It seems kind of strange that Microsoft creates these files when things go bad but makes it difficult to obtain useful information from them. After some Googling I found the following, hope it helps.

- Download [Debugging Tools for Windows](http://msdn.microsoft.com/en-us/windows/hardware/gg463009)
- Open WinDBG and open the .DMP file you want to analyze.
- Enter the following commands.


```text
.symfix
.reload
!analyze -v
```

You should be able to decipher what is causing the crashes. If you prefer something a little more automated check out [BlueScreenView](http://www.nirsoft.net/utils/blue_screen_view.html).
