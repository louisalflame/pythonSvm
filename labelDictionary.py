#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, json, codecs, sys

from tracePath import Path

sys.path.insert(0, Path.TaaDSrc)
from CommonSenseServer import CommonSenseAPI

class LabelDictionary:
    _labels_action = []
    _labels_screen = []

    @classmethod
    def parseLabel(cls):
        cls._labels_action = []
        cls._labels_screen = []
        labelAPI = CommonSenseAPI()
        for APPclass in labelAPI.getTotalClass()['totalClass']:
            actionLabels = labelAPI.getActionLables( APPclass['id'] )
            for i, actionLabel in enumerate( actionLabels['labels'] ):
                l = Label()
                l.setLabel( actionLabel['label'] )
                l.setInfo( actionLabel['description'] )
                l.setId( actionLabel['id'] )
                l.addTag( APPclass['className'] )

                for syn in labelAPI.getActionSynonym( actionLabel['id'] )['synonym']:
                    l.addSynonym(syn)

                cls._labels_action.append( l )

            screenLabels = labelAPI.getScreenLabels( APPclass['id'] )
            for i, screenLabel in enumerate( screenLabels['labels'] ):
                l = Label()
                l.setLabel( screenLabel['label'] )
                l.setInfo( screenLabel['description'] )
                l.setId( screenLabel['id'] )
                l.addTag( APPclass['className'] )

                for syn in labelAPI.getScreenSynonym( screenLabel['id'] )['synonym']:
                    l.addSynonym(syn)

                cls._labels_screen.append( l )

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
        self._label    = ""
        self._synonyms = []
        self._tags     = []
        self._info     = ""
        self._id       = None 

    def setLabel(self, label):
        self._label = label

    def addSynonym(self, synonym):
        self._synonyms.append( synonym )

    def addTag(self, tag):
        self._tags.append( tag )

    def setInfo(self, info):
        self._info = info

    def setId(self, Id):
        self._id = Id

    def getLabel(self):
        return self._label

    def getSynonyms(self):
        return self._synonyms

    def getTags(self):
        return self._tags

    def getInfo(self):
        return self._info

    def getId(self):
        return self._id