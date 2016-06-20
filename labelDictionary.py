#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, json, codecs

from tracePath import Path

class LabelDictionary:
    _labels_action = {}
    _labels_screen = {}

    @classmethod
    def parseLabel(cls):
        cls._labels_action = {}
        cls._labels_screen = {}
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
            if line.startswith('#') and i > 0:
                label = ''.join( line[1:].split() )
                key = ''.join( lines[i-1].split() )
                if key in cls._labels_action:
                    cls._labels_action[key].append(label)
            else:
                if line not in cls._labels_action:
                    label = ''.join( line.split() )
                    cls._labels_action[ label ] = [ label ]

    @classmethod
    def parseLabelsScreen(cls, lines):
        for i, line in enumerate(lines):
            if line.startswith('#') and i > 0:
                label = ''.join( line[1:].split() )
                key = ''.join( lines[i-1].split() )
                if key in cls._labels_screen:
                    cls._labels_screen[key].append(label)
            else:
                if line not in cls._labels_screen:
                    label = ''.join(line.split() )
                    cls._labels_screen[ label ] = [ label ]

    @classmethod
    def getLabelDictionary(cls):
        return { 'action' : cls._labels_action,
                 'screen' : cls._labels_screen }

    @classmethod
    def resetLabels(cls):
        cls._labels_action = {}
        cls._labels_screen = {}
