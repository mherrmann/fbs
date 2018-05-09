# fman build system
Cross-platform desktop applications are a lot of work:

 * Packaging an app into a standalone executable is not trivial.
 * Creating installers is tedious.
 * Code signing is a hassle but necessary to avoid OS warnings "untrusted app".
 * Auto-updating is a pain.

What makes the situation even worse is that most solutions to the above 
problems are platform-specific. So you have to create an installer for Mac, one
for Windows, etc.

In recent years, [Electron](https://electronjs.org/) has seen a lot of interest
as a technology for creating cross-platform desktop apps. The problem is, it is
very resource intensive and its performance is not good enough for many use
cases.

An alternative to Electron is [Qt](https://www.qt.io). It has been around for
many more years and can be much faster than Electron. Qt is written in C++, but
bindings are available for other languages. A popular choice for Python is
[PyQt](https://riverbankcomputing.com/software/pyqt/intro).

This project addresses the above problems for applications written with PyQt.
It open sources code that was originally written for the cross-platform file
manager [fman](https://fman.io?s=fbs). By packaging field-tested solutions in
one cohesive package, this project lets you create cross-platform desktop apps
in minutes, not months.

## Getting started
The best place to get started is the
[official tutorial](https://github.com/mherrmann/fbs-tutorial).

## Licensing
This project is licensed under the GPL. In simple terms, this means you can use
it for free in open source projects that are also licensed under the GPL. If on
the other hand you want to use the project for a proprietary app where you don't
want to open source the code, then you need a commercial license. The price for
one developer is currently EUR 249. One year of updates is included. To obtain a
license, click
[here](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=NH2ANDDS48KXA).

## Current Status
It's currently possible to package apps on Windows, Mac and Linux. Installers
can be created for Windows and Mac. The next steps are to let you create an
installer for Ubuntu (Linux), then code signing, then automatic updates. To stay
updated as these features are open sourced, please subscribe
[here](https://emailoctopus.com/lists/5061ca0f-33e0-11e8-a3c9-06b79b628af2/forms/subscribe).