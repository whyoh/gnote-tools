gnote-tools
===========
tools for dealing with tomboy/gnote notes, either via dbus or directly on the XML (*.note) files

usage 1
-------
to export all notes to a set of web pages:

1. create a new directory and cd to it
2. run notewiki.py -m export -s note-html.xsl.  it will connect to your tomboy or gnote notes via dbus and save them all as XML files in the current directory, named according to their titles and including a reference to the note-html.xsl XSLT stylesheet.
3. put the note-html.xsl file in the same directory.
4. now open either the folder or one of the XML files (perhaps your 'Start Here' note or the generated exportIndex.xml file) in a web browser.

usage 2
-------
in gnote 0.8.3 i have trouble with note titles which contain spaces and start with the name of another note - the automatic links get messed up.

also gnote sometimes convinces itself that a link is broken when it isn't.

also text in old notes doesn't automatically link to new notes.

to fix all these things:

1. run notewiki.py -m overwrite.

to do
-----
* the note metadata could use some love - see comments in XSLT
* notebooks
* indents and tabs
* plugins - things like bugzilla links and 'what links here'
* check this works on Windows.
* turn this "to do" list into github "Issues" ;-)
* alternative CSS styles?

notes
-----
there's a note-to-html stylesheet in the [Tomboy source](http://git.gnome.org/browse/tomboy/tree/data/tomboy-note-clipboard-html.xsl)
but it doesn't appear to work in a browser.  i think it's a namespaces issue.  might be worth just adding namespaces to it - perhaps we can make a version which works here AND in the app.

Tomboy appears to have a "--addin:html-export-all-quit [path]" option but that seems to be missing in gnote.  I think i prefer the XSL reference approach but could be persuaded.

notewiki.py uses the etreeEditor class from [pycontent](https://github.com/whyoh/pyContent).
