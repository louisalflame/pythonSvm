#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, json, codecs

from tracePath import Path

class LabelDictionary:
    def __init__(self):
        self._labels_action = {}
        self._labels_screen = {}

    def parseLabel(self):
        for dirName in [ 'file_manager', 'notepad', None ]:
            self.parseLabelDir( dirName )

    def parseLabelDir(self, dirName=None):
        if not dirName:
            labelPath = os.path.join( Path.Label, 'labels_action' )
            if os.path.exists( labelPath ):
                with codecs.open( labelPath, 'r', encoding='utf-8' ) as f:
                    lines = f.readlines()
                    self.parseLabelsAction(lines)

            labelPath = os.path.join( Path.Label, 'labels_screen' )
            if os.path.exists( labelPath ):
                with codecs.open( labelPath, 'r', encoding='utf-8' ) as f:
                    lines = f.readlines()
                    self.parseLabelsScreen(lines)
        else:
            labelPath = os.path.join( Path.Label, dirName, 'labels_action' )
            if os.path.exists( labelPath ):
                with codecs.open( labelPath, 'r', encoding='utf-8' ) as f:
                    lines = f.readlines()
                    self.parseLabelsAction(lines)

            labelPath = os.path.join( Path.Label, dirName, 'labels_screen' )
            if os.path.exists( labelPath ):
                with codecs.open( labelPath, 'r', encoding='utf-8' ) as f:
                    lines = f.readlines()
                    self.parseLabelsScreen(lines)

    def parseLabelsAction(self, lines):
        for i, line in enumerate(lines):
            if line.startswith('#') and i > 0:
                label = ''.join( line[1:].split() )
                key = ''.join( lines[i-1].split() )
                if key in self._labels_action:
                    self._labels_action[key].append(label)
            else:
                if line not in self._labels_action:
                    label = ''.join( line.split() )
                    self._labels_action[ label ] = [ label ]

    def parseLabelsScreen(self, lines):
        for i, line in enumerate(lines):
            if line.startswith('#') and i > 0:
                label = ''.join( line[1:].split() )
                key = ''.join( lines[i-1].split() )
                if key in self._labels_screen:
                    self._labels_screen[key].append(label)
            else:
                if line not in self._labels_screen:
                    label = ''.join(line.split() )
                    self._labels_screen[ label ] = [ label ]

    def getLabelDictionary(self):
        return { 'action' : self._labels_action,
                 'screen' : self._labels_screen }

    def resetLabels(self):
        self._labels_action = {}
        self._labels_screen = {}
