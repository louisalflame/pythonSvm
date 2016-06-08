#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, json, codecs
from automataElement import AutomataElement, TraceElement, StateElement, EdgeElement

def parseSessionAutomata( sessionFile ):
    statesList = {}
    edgesList  = {}
    tracesList = []
    taskJson = None
    edgesJson = None

    if not ( os.path.exists( sessionFile )                                                or \
             os.path.exists( os.path.join(sessionFile, 'sessionAutomata') )               or \
             os.path.exists( os.path.join(sessionFile, 'sessionAutomata', 'edges.json') )      ):
        raise Exception('Cannot find Session Automata')
    if not os.path.exists( os.path.join(sessionFile, 'traceSet') ):
        raise Exception('Cannot find Session traceSet')
    if not os.path.exists( os.path.join(sessionFile, 'task.json') ):
        raise Exception('Cannot find task.json')

    with open( os.path.join(sessionFile, 'task.json'), 'r') as f:
        taskJson = json.load(f)

    # make Automata from session edges.json
    with open( os.path.join(sessionFile, 'sessionAutomata', 'edges.json'), 'r') as f:
        edgesJson = json.load(f)

    mode = "STATE_TO_EDGE"
    for e in edgesJson['edges']:
        if mode == "STATE_TO_EDGE":
            mode = "EDGE_TO_STATE"
            stateID = e[0]
            edgeID  = e[1]

            if stateID not in statesList:
                se = StateElement()
                se.set_id( int(stateID) )
                statesList[stateID] = se
            else:
                se = statesList[stateID]

            if edgeID not in edgesList:
                ee = EdgeElement()
                ee.set_id( int(edgeID) )
                ee.set_stateFrom( se )
                edgesList[edgeID] = ee
            elif not edgesList[edgeID].get_stateFrom():
                edgesList[edgeID].set_stateFrom( se )

        elif mode == "EDGE_TO_STATE":
            mode = "STATE_TO_EDGE"
            edgeID  = e[0]
            stateID = e[1]

            if stateID not in statesList: 
                print('make new state:', stateID)
                se = StateElement()
                se.set_id( int(stateID) )
                statesList[stateID] = se
            else:
                se = statesList[stateID]

            if edgeID not in edgesList:
                print('make new edge:', edgeID)
                ee = EdgeElement()
                ee.set_id( int(edgeID) )
                ee.set_stateTo( se )
                edgesList[edgeID] = ee
            elif not edgesList[edgeID].get_stateTo():
                print('make old edge:', edgeID)
                edgesList[edgeID].set_stateTo( se )

    # make Automata from traceSet
    traceAmount = int( taskJson['traceAmount'] )
    for i in range(traceAmount):
        traceSetFile = os.path.join(sessionFile, 'traceSet', str(i+1))
        if not os.path.exists( traceSetFile ):
            raise Exception('Cannot find traceSet-',traceSetFile)

        traceTxtFile = os.path.join(sessionFile, 'traceSet', str(i+1), 'trace.txt')
        if not os.path.exists( traceSetFile ):
            raise Exception('Cannot find trace.txt : ',traceTxtFile)

        with open(traceTxtFile, 'r') as f:
            traceLines = f.readlines()

        trace = { 'states': [], 'edges': [] }
        mark = '=>'
        for line in traceLines:
            print(line)
            if mark in line:
                words = line.split(mark)
                NodeName = ''.join( words[-1].split() )
                NodeID = int( NodeName.strip('state') )
                NodeFile = ''.join( words[0].split() )

                # check if is state
                if NodeFile.endswith('.xml'):
                    if NodeID in statesList:
                        se = statesList[NodeID]
                        se.set_xml( os.path.join(sessionFile, 'traceSet', str(i), NodeFile) )
                        trace['states'].append( se )

                #check if is edge
                elif NodeFile.endswith('.json'):
                    if NodeID in edgesList:
                        ee = edgesList[NodeID]
                        ee.set_xml( os.path.join(sessionFile, 'traceSet', str(i), NodeFile) )
                        trace['edges'].append( ee )

            else:
                break
        tracesList.append(trace)

    return statesList, edgesList, tracesList