Welcome to fbs's issue tracker!

Have you already purchased a license for fbs, or are you planning to do so in the near future? If yes, feel free to ask anything you want here. Just delete this text and type away. I will be happy to help.

Otherwise, please understand that I am essentially helping you in my spare time. While I'm happy to help, I lead a busy life and have no patience for people who do not take the time to make it easy for me to help them.

Do you want to request an improvement to fbs? If yes, please delete this text and explain your suggestion clearly and why it would be useful for other fbs users.

Are you using Python 3.7, 3.8 and / or Anaconda? These distributions are not (yet) supported. Please switch to vanilla Python 3.5 or 3.6. Seriously. fbs's strength comes from being tested with these Python versions on tens of thousands of computers. It is not unlikely that the problems you are experiencing simply come from the fact that fbs doesn't support your Python version. Also, it doesn't exactly make me very motivated to help when I ask "please use Python 3.6" and then people come along "I know I shouldn't, but I'm using Python 3.7 and ...".

Are you getting an error? Maybe `fbs run` works, but the app created with `fbs freeze` won't start? If yes, please follow the steps at https://build-system.fman.io/troubleshooting. Do not just skim over them. Read and follow them line by line. Hopefully this will fix your problem. If not, read on.

Is it a problem with one of your dependencies? If the dependency is PyQt5 or PySide2 and you are using a version supported by fbs (see the troubleshooting link above), then please jump to the next paragraph and let me know. Otherwise, if it's another library, try googling "PyInstaller [your dependency problem]". If that doesn't help, please go to PyInstaller's issue tracker and request a fix there. fbs uses PyInstaller for dependency management and so any dependency-related problems should be fixed there.

Okay. At this point, all easy solutions to your problem have been ruled out. Are you here to get help with your app? Then please go to StackOverflow.com and ask there. This issue tracker is only for changes / improvements to fbs. Please only continue to the next paragraph if your goal of writing here is to improve fbs, not just to get help with your app. I frequently close issues here that violate this point.

If you have read all of the above, and only then, please delete this text and let me know the following:

 * Your operating system(s)
 * Your Python version (Must be 3.5 or 3.6 because you followed the above instructions.)
 * Your fbs version
 * Your PyInstaller version
 * Your PyQt5 / PySide2 version
 * A copy of any error messages you are getting. Use three backticks ```...``` before and after to format them.
 * A (minimal!) script that reproduces the problem you are experiencing.

Please don't just paste the output of `pip freeze` here. Also, I repeat, do not post your entire application's code. Nobody has time to read it. Create a _minimal_, self-contained script that reproduces the problem. Like with people using Python 3.7 instead of one of the supported versions, app-specific code in your example makes me wonder "(s)he didn't take the time to make it easy for me to help. So why should I invest my time?"

Thanks,

Michael
