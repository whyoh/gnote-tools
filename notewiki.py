#!/usr/bin/python
# -*- coding: utf-8 -*-

import dbus
from lxml import etree
from os import makedirs
from os.path import exists

tomboy = dbus.Interface(dbus.SessionBus().get_object("org.gnome.Gnote", "/org/gnome/Gnote/RemoteControl"), "org.gnome.Gnote.RemoteControl")  
for uri in tomboy.ListAllNotes() :
	title = tomboy.GetNoteTitle(uri)
	if "/" in title:
		folder = "/".join(title.split("/")[:-1])
		if not exists(folder): makedirs(folder)
	open(title + ".xml", "w").write("﻿<?xml version='1.0' encoding='utf-8'?>\n<?xml-stylesheet href='note-html.xsl' type='text/xsl'?>\n" + 
etree.tostring(etree.fromstring(tomboy.GetNoteCompleteXml(uri))))
