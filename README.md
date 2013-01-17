gnote-tools
===========

tools for dealing with tomboy/gnote notes, either via dbus or directly on the XML (*.note) files

usage
=====

create a new directory, change to it and run the notewiki.py script.
it will connect to your tomboy or gnote notes via dbus and save them all as XML files in the current directory, named according to their titles and including a reference to the note-html.xsl XSLT stylesheet.
put the note-html.xsl file in the same directory.
now open either the folder or one of the XML files (perhaps your 'Start Here' note) in a web browser.

to do
=====
* the note metadata could use some love - see comments in XSLT
* notebooks
* plugins - things like bugzilla links and 'what links here'
