# fbs
Easily create cross-platform desktop apps based on PyQt.

## Motivation
Cross-platform desktop applications require a lot more work than other apps:

 * Packaging standalone executables / installers is not trivial.
 * Code signing is a hassle but necessary to avoid OS warnings "untrusted app".
 * Auto-updating is a pain.

What makes the situation even worse is that solutions to the above problems are
usually platform-specific. So you have to create an installer for Mac, one for
Windows, etc.

In recent years, [Electron](https://electronjs.org/) has seen a lot of interest
as a platform for cross-platform desktop apps. The problem is, its performance
is not good enough for many use cases.

An alternative to Electron is [Qt](https://www.qt.io). It can offer much better
performance than Electron. Qt has has been around for many years and is very
stable. Originally written in C++, bindings are available for many other
languages such as for instance Python via
[PyQt](https://riverbankcomputing.com/software/pyqt/intro).

The goal of this project is to solve the above problems for applications written
with PyQt. It open sources code that was originally written for
[fman](https://fman.io) (hence the name: **f**man **b**uild **s**ystem).
By packaging field-tested solutions in one cohesive package, it should let you
create and distribute a stable app in hours, not months.