# fbs
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

The goal of this project is to solve the above problems for applications written
with PyQt. It open sources code that was originally written for the
cross-platform file manager [fman](https://fman.io). By packaging field-tested
solutions in one cohesive package, this project aims to let you create
cross-platform desktop apps in minutes, not months.

## Getting started
The best place to get started is the
[official tutorial](https://github.com/mherrmann/fbs-tutorial).

## Current status
Work on separating fman's source code from code useful for this project began in
mid-December 2017. At the moment, it's possible to package your app into a
standalone executable that you can distribute to your users. The project will be
very active for the coming weeks. If you want to stay up-to-date on what's new,
please subscribe to the (non-spammy) [mailing list](http://eepurl.com/ddgpnf).