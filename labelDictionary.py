#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, json, codecs

from tracePath import Path

class LabelDictionary:
    _labels_action = []
    _labels_screen = []

    @classmethod
    def parseLabel(cls):
        cls._labels_action = []
        cls._labels_screen = []
        for dirName in [ 'file_manager', 'notepad', 'nothing_demo', None ]:
            cls.parseLabelDir( dirName )

    @classmethod
    def parseLabelDir(cls, dirName=None):
        if not dirName:
            labelPath = os.path.join( Path.Label, 'labels_action' )
            if os.path.exists( labelPath ):
                with codecs.open( labelPath, 'r', encoding='utf-8' ) as f:
                    lines = f.readlines()
                    cls.parseLabelsAction(lines)

            labelPath = os.path.join( Path.Label, 'labels_screen' )
            if os.path.exists( labelPath ):
                with codecs.open( labelPath, 'r', encoding='utf-8' ) as f:
                    lines = f.readlines()
                    cls.parseLabelsScreen(lines)
        else:
            labelPath = os.path.join( Path.Label, dirName, 'labels_action' )
            if os.path.exists( labelPath ):
                with codecs.open( labelPath, 'r', encoding='utf-8' ) as f:
                    lines = f.readlines()
                    cls.parseLabelsAction(lines)

            labelPath = os.path.join( Path.Label, dirName, 'labels_screen' )
            if os.path.exists( labelPath ):
                with codecs.open( labelPath, 'r', encoding='utf-8' ) as f:
                    lines = f.readlines()
                    cls.parseLabelsScreen(lines)

    @classmethod
    def parseLabelsAction(cls, lines):
        for i, line in enumerate(lines):
            if not line.startswith('#'):
                key = ''.join( line.split() )
                info = ''.join( lines[i+1][1:].split() )
                label = Label()
                label.setLabel(key)
                label.setInfo(info)
                cls._labels_action.append( label )

    @classmethod
    def parseLabelsScreen(cls, lines):
        for i, line in enumerate(lines):
            if not line.startswith('#'):
                key = ''.join( line.split() )
                info = ''.join( lines[i+1][1:].split() )
                label = Label()
                label.setLabel(key)
                label.setInfo(info)
                cls._labels_screen.append( label )

    @classmethod
    def getLabelDictionary(cls):
        return { 'action' : cls._labels_action,
                 'screen' : cls._labels_screen }

    @classmethod
    def resetLabels(cls):
        cls._labels_action = []
        cls._labels_screen = []

class Label:
    def __init__(self):
        self._label   = ""
        self._synonyms = []
        self._tags    = []
        self._info    = ""

    def setLabel(self, label):
        self._label = label

    def addSynonym(self, synonym):
        self._synonyms.append( synonym )

    def addTag(self, tag):
        self._tags.append( tag )

    def setInfo(self, info):
        self._info = info

    def getLabel(self):
        return self._label

    def getSynonyms(self):
        return self._synonyms

    def getTags(self):
        return self._tags

    def getInfo(self):
        return self._info