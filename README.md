gnote-tools
===========

tools for dealing with tomboy/gnote notes, either via dbus or directly on the XML (*.note) files

usage
=====

1. create a new directory and cd to it
2. run the notewiki.py script.  it will connect to your tomboy or gnote notes via dbus and save them all as XML files in the current directory, named according to their titles and including a reference to the note-html.xsl XSLT stylesheet.
3. put the note-html.xsl file in the same directory.
4. now open either the folder or one of the XML files (perhaps your 'Start Here' note) in a web browser.

to do
=====
* the note metadata could use some love - see comments in XSLT
* notebooks
* plugins - things like bugzilla links and 'what links here'
* check this works on Windows - i've put in directory creation for notes with a "/" in the title.  not sure if Windows needs something similar.
* turn this "to do" list into github "Issues" ;-)
* alternative CSS styles?

notes
=====
there's a note-to-html stylesheet in the Tomboy source: http://git.gnome.org/browse/tomboy/tree/data/tomboy-note-clipboard-html.xsl
but it doesn't appear to work in a browser.  i think it's a namespaces issue.  might be worth just adding namespaces to it - perhaps we can make a version which works here AND in the app.

Tomboy appears to have a "--addin:html-export-all-quit [path]" option but that seems to be missing in gnote.  I think i prefer the XSL reference approach but could be persuaded.
