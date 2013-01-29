#!/usr/bin/python
# -*- coding: utf-8 -*-

# tool to read all notes from dbus, clean up the XML and either update the notes or dump them to files.

import dbus
from string import whitespace, punctuation, ascii_letters, digits
import os.path
from os import makedirs
from argparse import ArgumentParser

from etreeEditor import etreeEditor

argParser = ArgumentParser()
argParser.add_argument("-m", "--mode", help = "check notes (default), overwrite .note files or export to .xml files", choices = ['check', 'overwrite', 'export'], default="check")
argParser.add_argument("-i", "--include", help = "note title to include - repeat option to specify more than one note", action = "append")
argParser.add_argument("-v", "--verbose", help = "write a bunch of stuff to stdout", action = "store_true")
argParser.add_argument("-d", "--diff", help = "try to make 'original' and 'fixed' output files easy to diff", action = "store_true")
argParser.add_argument("-g", "--good", help = "include 'clean' files (implied by 'export' mode)", action = "store_true")
argParser.add_argument("-s", "--style", help = "include a reference to an XML stylesheet")
options = argParser.parse_args()

def findTitles(lower, titleList, note, exclusions):
# apply tomboy rules to some text to find instances of note titles
# args: lowercased note text, list of all note titles, title of this note, list of elements which can't contain links to notes
	foundTitles = []
	for title in titleList:
		if title == note: continue # don't find links to yourself
		startingFrom = len(note)
		# i think links within the title was a temporary aberration
		#if title != note: startingFrom = 0
		while lower.find(title, startingFrom) != -1: # also finds links to notes created after this note was last edited
			where = lower.index(title, startingFrom)
			startingFrom = where + 1
			if where and lower[where - 1] not in whitespace + punctuation and ((lower[where] in ascii_letters and lower[where - 1] in ascii_letters) or (lower[where] in digits and lower[where - 1] in digits)): continue
			if where + len(title) < len(lower) and lower[where + len(title)] not in whitespace + punctuation and ((lower[where] in ascii_letters and lower[where + len(title)] in ascii_letters) or (lower[where] in digits and lower[where + len(title)] in digits)): continue
			already = False
			for found in foundTitles:
				if where >= found[1] and where < found[2] or where + len(title) >= found[1] and where + len(title) < found[2]:
					already = True
					break
			if already: continue
			inLink = False
			for style in exclusions:
				if where >= style[0] and where < style[1] or where + len(title) >= style[0] and where + len(title) < style[1]:
					inLink = True
					break
			if inLink: continue
			startingFrom = where + len(title)
			foundTitles.append([title, where, where + len(title)])
	return foundTitles

def checkLinks(foundTitles, links, brokenLinks):
# compare a list of note titles to the existing set of links in the note
	errors = []
	warnings = []
	matchedLinks = []
	for toLink in foundTitles:
			title = toLink[0]
			where = toLink[1]
			linkOkay = False
			# apparently it's okay if the link is split up - so long as each bit of the title is a link
			# however, i'm going to tidy those up so they work when i transform it to HTML
			thisLink = [False] * len(title)
			anyBroken = False
			splitLink = False
			for styleDex, style in enumerate(links + brokenLinks):
				if style[0] >= where and style[1] <= where + len(title):
					for charDex in range(style[0] - where, style[1] - where): thisLink[charDex] = True
					matchedLinks.append(styleDex)
					if all(thisLink):
						linkOkay = True
						if styleDex >= len(links): anyBroken = True
					elif any(thisLink): splitLink = True
			if linkOkay and anyBroken:
				if options.mode != "export": warnings.append("  not broken: " + title)
				else: errors.append("  not broken: " + title)
			if linkOkay and splitLink:
				if options.mode != "export": warnings.append("  split link: " + title)
				else: errors.append("  split link: " + title)
			if not linkOkay: errors.append("  BROKEN!: " + title)
	for x in list(n for n, x in enumerate(links + brokenLinks) if n not in matchedLinks):
		if x >= len(links): warnings.append("  broken link lost")
		else: warnings.append("  link lost")
	return errors, warnings

# connect to whichever dbus interface exists
try:
	tomboy = dbus.Interface(dbus.SessionBus().get_object("org.gnome.Tomboy", "/org/gnome/Tomboy/RemoteControl"), "org.gnome.Tomboy.RemoteControl")
	app = "tomboy"
except:
	tomboy = dbus.Interface(dbus.SessionBus().get_object("org.gnome.Gnote", "/org/gnome/Gnote/RemoteControl"), "org.gnome.Gnote.RemoteControl")	
	app = "gnote"

# fetch the note list
noteList = {}
for uri in tomboy.ListAllNotes():
	title = tomboy.GetNoteTitle(uri).lower()
	if title: noteList[title] = uri
print "found", len(noteList), "note(s)"

titleList = sorted(noteList.keys(), cmp=lambda x, y: len(y) - len(x))
topLevelList = noteList.copy()
updated = []
hasErrors = []
hasWarnings = []
totalErrors = 0
totalWarnings = 0

for note in noteList:
	# for each note which should be checked
	if options.include and note.lower() not in list(x.lower() for x in options.include): continue	

	# get a list of links in the original
	fixer = etreeEditor(tomboy.GetNoteCompleteXml(noteList[note]))
	fixer.setSplitMergeFilter(lambda tag : not tag.startswith("{http://beatniksoftware.com/tomboy/link}") and not tag.startswith("{http://beatniksoftware.com/tomboy}list"))
	
	noteRange = fixer.getRanges("{http://beatniksoftware.com/tomboy}note-content")[0]
	text = fixer.getText()
	
	links = list([x[0] - noteRange[0], x[1] - noteRange[0]] for x in fixer.getRanges("{http://beatniksoftware.com/tomboy/link}internal"))
	fixer.removeAll("{http://beatniksoftware.com/tomboy/link}internal")
	brokenLinks = list([x[0] - noteRange[0], x[1] - noteRange[0]] for x in fixer.getRanges("{http://beatniksoftware.com/tomboy/link}broken"))
	fixer.removeAll("{http://beatniksoftware.com/tomboy/link}broken")
	
	# get a list of note titles found in the text
	exclusions = list([x[0] - noteRange[0], x[1] - noteRange[0]] for x in fixer.getRanges("{http://beatniksoftware.com/tomboy/link}url"))
	foundTitles = findTitles(text.lower()[noteRange[0]:noteRange[1]], titleList, note, exclusions)
	errors, warnings = checkLinks(foundTitles, links, brokenLinks)
	
	# update list of "notes which aren't linked to from other notes"
	for link in foundTitles:
		if link[0] in topLevelList: del topLevelList[link[0]]

	# update summary stats and print messages
	if options.verbose and warnings + errors:
		print note
		if warnings: print "\n".join(warnings)
		if errors: print "\n".join(errors)
	
	if errors: hasErrors.append(note)
	if warnings: hasWarnings.append(note)
	totalErrors += len(errors)
	totalWarnings += len(warnings)

	if not errors and  options.mode != "export" and not options.good: continue
	# if there's anything to fix (or we're exporting everything regardless)...
	
	# add internal links back in
	for link in foundTitles: fixer.add("{http://beatniksoftware.com/tomboy/link}internal", link[1] + noteRange[0], link[2] + noteRange[0])

	# write/update notes as required
	if options.mode == "overwrite": # write to running app's files - without making a backup!
		notefile = os.path.expanduser("~/.local/share/" + app + "/" + noteList[note].split("/")[-1] + ".note")
		assert os.path.isfile(notefile)
		print "overwriting", notefile
		open(notefile, "w").write(fixer.serialize(encoding="utf-8"))
		updated.append(note)

	elif options.mode == "export":
		notefile = note.replace("/", "-") + ".xml"
		if options.diff: # try to match output to the app-generated XML so it's easier to check diffs
			if not os.path.exists("fixed"): makedirs("fixed")
			if not os.path.exists("orig"): makedirs("orig")
			open("fixed/" + notefile, "w").write((u'<?xml version="1.0"?>\n' + fixer.serialize().replace(u'<note xmlns:link="http://beatniksoftware.com/tomboy/link" xmlns:size="http://beatniksoftware.com/tomboy/size" xmlns="http://beatniksoftware.com/tomboy" version="0.3">', u'<note version="0.3" xmlns:link="http://beatniksoftware.com/tomboy/link" xmlns:size="http://beatniksoftware.com/tomboy/size" xmlns="http://beatniksoftware.com/tomboy">').replace(u'<note-content version="0.1">', u'<note-content version="0.1" xmlns:link="http://beatniksoftware.com/tomboy/link" xmlns:size="http://beatniksoftware.com/tomboy/size">') + u"\n\n").encode("utf-8"))
			open("orig/" + notefile, "w").write(tomboy.GetNoteCompleteXml(noteList[note]).encode("utf-8").replace("&quot;", "\""))
		else:
			if options.style:
				prefix = "﻿<?xml version='1.0' encoding='utf-8'?>\n<?xml-stylesheet href='" + options.style + "' type='text/xsl'?>\n"
			else: prefix = ""
			open(notefile, "w").write(prefix + fixer.serialize(encoding="utf-8"))

	elif options.mode == "dbus":
		# only the last one of these calls seems to have any effect - and it updates the 'last changed' date in the note .. not what i wanted.  back to modifying the XML files directly :-(
		if not tomboy.SetNoteCompleteXml(uri, u'<?xml version="1.0"?>\n' + fixer.serialize()):
			print "failed to update note", note
		else: updated.append(note)
	elif options.mode == "check": updated.append(note)

# print a summary
if options.mode == "export" and not options.diff and topLevelList: open("index.html", "w").write("\n".join("<li><a href='" + x.replace("/", "-") + ".xml'>" + x for x in sorted(topLevelList.keys())))
if totalErrors: print totalErrors, "error(s) in", len(hasErrors), "note(s)"
if totalWarnings and options.verbose: print totalWarnings, "warning(s) in", len(hasWarnings), "note(s)"
if updated: print len(updated), "note(s) updated"
if options.mode == "overwrite" and updated: print "now log out to force re-reading of the files"
if options.mode != "export" and not updated: print "all clear!"
