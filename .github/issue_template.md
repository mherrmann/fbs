Welcome to fbs's issue tracker!

Have you already purchased a license for fbs, or are you planning to do so in the near future? If yes, feel free to ask anything you want here. Just delete this text and type away. We will be very happy to help.

Otherwise, please understand that we are essentially helping you in our spare time. We get many requests. While we're happy to help, we have little patience for people who do not take the time to make it easy for us.

First: This is not a place for general programming questions. We do not provide help with PyQt5, even if you are using fbs. If you have a question or an error that is not specific to fbs, please go to StackOverflow instead.

Do you want to request a feature in fbs? If yes, please delete this text and explain your suggestion clearly and why it would be useful for other fbs users.

Or are you getting an error? Maybe `fbs run` works, but the app created with `fbs freeze` won't start? If yes, please follow the steps at https://build-system.fman.io/troubleshooting. Don't just skim over them. Read and follow them line by line. Hopefully this will fix your problem. If not, read on.

Are you using Python 3.7 and / or Anaconda? These distributions are not (yet) supported. Please switch to vanilla Python 3.5 or 3.6. If the problem persists, read on.

So you're still getting an error, or something else doesn't work as expected in fbs.

Is it a problem with one of your dependencies? If the dependency that causes the problem is PyQt5 or PySide2, then please jump to the next paragraph and let us know! Otherwise, try googling "[your dependency problem] PyInstaller". We don't implement workarounds for library-related PyInstaller problems in fbs. (Unless the library is PyQt5 or PySide2.) Such problems should be reported to (and fixed in) PyInstaller.

Okay. So it really does appear as if the problem you are facing is caused by fbs. In this case, please delete this text and let us know the following:

 * Your operating system(s)
 * Your Python version (Must be 3.5 or 3.6 because you followed the above instructions.)
 * Your fbs version
 * Your PyInstaller version
 * Your PyQt5 / PySide2 version
 * A copy of any error messages you are getting. Use ```...``` to format them.
 * A (minimal!) script that reproduces the problem you are experiencing.

Please don't just paste the output of `pip freeze` here. Also please don't post your entire application's code. We simply won't have time to read it. Create a _minimal_, self-contained script that reproduces the problem.

Thanks!