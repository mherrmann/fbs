# fbs
Easily create cross-platform desktop apps based on PyQt.

## Motivation
Cross-platform desktop applications require a lot more work than other apps:

 * Creating standalone executables / installers for an app is not trivial.
 * Code signing is a hassle but necessary to avoid OS warnings "untrusted app".
 * Auto-updating is a pain.

What makes the situation even worse is that most solutions to the above 
problems are platform-specific. So you have to create an installer for Mac, one
for Windows, etc.

In recent years, [Electron](https://electronjs.org/) has seen a lot of interest
as a platform for cross-platform desktop apps. The problem is, its performance
is not good enough for many use cases.

An alternative to Electron is [Qt](https://www.qt.io). It has been around for
many years and can be much faster than Electron. Qt is written in C++, but
bindings are available for other languages. A popular choice is
[PyQt](https://riverbankcomputing.com/software/pyqt/intro) for Python.

The goal of this project is to solve the above problems for applications written
with PyQt. It open sources code that was originally written for the
cross-platform file manager [fman](https://fman.io). By packaging field-tested
solutions in one cohesive package, this project aims to let you create
cross-platform desktop apps in hours, not months.