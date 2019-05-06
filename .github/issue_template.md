Welcome to fbs's issue tracker!

Have you already purchased a license for fbs, or are you planning to do so in the near future? If yes, feel free to ask anything you want here. Just delete this text and type away. We will be very happy to help.

Otherwise, please understand that we are essentially helping you in our spare time. We get many requests. While we're happy to help, we have little patience for people who do not make the effort to make it easy for us.

First: This is not a place for general programming questions. We do not provide help with PyQt5, even if you are using fbs. If you have a question or an error that is not specific to fbs, please go to StackOverflow instead.

Do you want to request a feature in fbs? If yes, please delete this text and explain your suggestion clearly and why it would be useful for other fbs users.

Or are you getting an error? Maybe `fbs run` works, but the app created with `fbs freeze` won't start? If yes, please follow the steps at https://build-system.fman.io/troubleshooting. Don't just skim over them. Read and follow them line by line. Hopefully this will fix your problem. If not, read on.

So you're still getting an error, or something else doesn't work as expected in fbs.

Is it a problem with one of your dependencies? If the dependency that causes the problem is PyQt5 or PySide2, then please jump to the next paragraph and let us know! Otherwise, try googling "[your dependency problem] PyInstaller". If this leaves you with any questions (eg. "how do I add/delete a shared library?"), feel free to ask our help. We'll be happy to advise. We will probably not however implement a workaround in fbs for a library-related PyInstaller problems. (Unless the library is PyQt5 or PySide2.) Such problems should be reported to (and fixed in) PyInstaller.

Okay. So it really does appear as if the problem you are facing is caused by fbs. In this case, please delete this text and let us know the following:

 * Your operating system(s)
 * Your Python version
 * Your fbs version
 * Your PyInstaller version
 * Your PyQt5 / PySide2 version
 * A copy of any error messages you are getting. Use ```...``` to format them.
 * If you want us to be able to reproduce the problem, what's a (minimal!) script that does this?

Do not just paste the output of `pip freeze`. We don't have time to parse through random output. Just let us know those library versions which you are think are relevant.
