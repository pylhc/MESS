#!/usr/bin/python

import time

import re
import sys
import os
import inspect

class State:
    states = {}
    def __init__(self,name,initial=0,final=0,action=0,replay=0,oneshot=0):
        if not State.states.has_key(self):
            self.name = name
            self.inputTransitions = []
            self.outputTransitions = []            
            self.initial = initial
            self.final = final
            State.states[self] = self
            self.action = action # a function
            self.replay = replay
            
            self.oneshot = oneshot
            if oneshot:
                self.done = False
            
            # add local storage to pass information from the actions to the replayActions
            self.store = [[]] # nested list
            
        else:
            raise "attempt to create state '"+ name + "' twice"
        
    def __hash__(self):
        return hash(str(self)) 

class Transition:
    transitions = []
    def __init__(self,name,condition,incomingState,outcomingState, action = 0, replay = 0,consume = True):
        self.name = name
        self.consume = consume # means the transition transmits the line of text to the next state
        if incomingState.__class__.__name__ != 'State' or outcomingState.__class__.__name__ != 'State':
            raise("incorrect type for passed State parameters")
        if State.states.has_key(incomingState) and State.states.has_key(outcomingState):
            self.incomingState = incomingState
            self.outcomingState = outcomingState
            self.condition = condition # a regex pattern
            self.action = action # usually a print instruction, but could be a function
            self.replay = replay

            # propagate transition information to the states
            self.incomingState.outputTransitions.append(self)
            self.outcomingState.inputTransitions.append(self)

            # add local storage to pass information from the actions to the replayActions
            # if a transition is crossed several times, each time a new store is created
            # to ease user point of view
            self.store = [[]] # nested list
            
        else:
            raise("failed to create transition due to missing incoming or outcoming state")
    def accept(self,line):
        return self.condition.match(line)

class FSM:

    debug = False
    
    def __init__(self):
        self.states = []
        self.transitions = []
        self.current = 0
        self.trajectory = [] # the history of states and transitions

    def init(self): # force switch to initial state
        for s in self.states:
            if s.initial:
                self.current = s
                self.trajectory.append(s)
                return
        raise("no initial state declared for this FSM")

    def addState(self,state):
        if not state in self.states:
            self.states.append(state)
            if state.initial:
                self.current = state
        else:
            raise("already existing state")

    def addStates(self,states):
        for s in states:
            self.addState(s)
            
    def addTransition(self,transition):
        if not transition in self.transitions:
            self.transitions.append(transition)

    def addTransitions(self,transitions):
        for t in transitions:
            self.addTransition(t)

    def step(self,context): # context is currently processed line
        #sys.stderr.write("line="+context+"\n")
        #if context == '':
        #    sys.stderr.write('HERE IS THE PROBLEM\n')
        # try to cross a transition (implicit event, possibly guard condition)

        context = context.rstrip('\n')
        
        if self.current == 0:
            raise("no initial state set")
        else:
            if len(self.current.outputTransitions)==0:
                raise('FSM reached a dead end on state ')

            for t in self.current.outputTransitions:
                #sys.stderr.write('now scanning transition '+t.name+' while input is"'+context+'"\n')
                if t.accept(context):
                    if t.action != 0:
                        (args,varargs,varkw,defaults) = inspect.getargspec(t.action) # will change in Python 2.6
                        if len(args)==0:
                            t.action()
                        elif len(args)==1:
                            t.action(context) # transmit the line of text                            
                        elif len(args)==2:
                            t.action(context,t.store[len(t.store)-1]) # also pass memory object of the Transition object
                            #sys.stderr.write('LEN(T.STORE)='+str(len(t.store[len(t.store)-1]))+"\n")                         
                            t.store.append([]) # a new empty list that will be passed next time the transition is called
                        else:
                            raise("action associated to transition expects too many arguments")
                    self.trajectory.append(t)
                    self.current = t.outcomingState
                    if FSM.debug:
                        sys.stderr.write('Transition '+t.name+' crossed\n')
                    if not t.consume:
                        self.step(context) # forward to the new state
                    #sys.stderr.write("done with "+context+"\n")
                    return
            # sys.stderr.write('all transitions from '+ self.current.name+' scanned\n')

            # record running the current state, if not already in this state
            # REMOVE THIS EXTRA TEST AND WE GET AS MANY HISTORY MARKERS AS THEY ARE LINES THAT MATCH THE PATTERN
            alreadyEncountered = False
            for o in self.trajectory:
                if (o == self.current) and ( o != self.trajectory[len(self.trajectory)-1]):
                    alreadyEncountered = True
            # already activated this state in the past, but we are not already here
            if alreadyEncountered: # want to do it only once o==self.current, not many times
                    self.current.store.append([]) # a new empty list that will be passed next time the state is called
            if (self.current != self.trajectory[len(self.trajectory)-1]):
                self.trajectory.append(self.current)
                
            # execute the state, if no transition crossed

            if self.current.final:
                #sys.stderr.write("reached final state\n")
                raise("reached final state before having consumed all lines ("+\
                      context+")") # had the chance to cross transition to eat-up all end blank lines and comments for instance
            
            if self.current.action != 0:
                # sys.stderr.write('execute state action\n')
                (args,varargs,varkw,defaults) = inspect.getargspec(self.current.action)
                if len(args)==0:
                    self.current.action()
                elif len(args)==1:
                    self.current.action(context) # transmit the line of text
                elif len(args)==2:
                    self.current.action(context,self.current.store[len(self.current.store)-1]) # also pass memory object of the State object
                elif len(args)==3:
                    self.current.action(context,self.current,self.current.store[len(self.current.store)-1]) # also pass the CURRENT state
                    #sys.stderr.write('self.current.store[len(self.current.store)-1]='+str(self.current.store[len(self.current.store)-1])+'\n')
                    #sys.stderr.write('self.current.store='+str(self.current.store)+'\n')
                    
                else:
                    raise("action associated to transition expects too many arguments")

    def replay(self): # go through the pre-recorded trajectory and invoke output instead of input actions
        outstream = ''
        for step in self.trajectory:
            if step.__class__.__name__ == 'Transition':
                t = step
                if t.replay != 0:
                    (args,varargs,varkw,defaults) = inspect.getargspec(t.replay)
                    if len(args)==0:
                        outstream += t.replay()
                    elif len(args)==1:
                        if FSM.debug:
                            sys.stderr.write("now to replay transition "+t.name+", which has memory: "+str(t.store[0])+\
                                             " and replay action "+ t.replay.__name__+"\n")
                        #sys.stderr.write("transition store is now "+str(t.store)+" (contains memory for all transitions)\n")                        
                        outstream += t.replay(t.store[0]) # transmit transition's store
                        t.store = t.store[1:] # next time, we'll pick up the next store in the list corresponding to the following occurence of the same transition instance
                        #sys.stderr.write("transition store is now "+str(t.store)+"\n")
                    else:
                        raise("replay function '"+t.replay.__name__+"' associated to transition expects too many arguments ("+str(len(args))+")")
                    
            elif step.__class__.__name__ == 'State':
                s = step
                if s.replay != 0:
                    (args,varargs,varkw,defaults) = inspect.getargspec(s.replay)
                    if len(args)==0:
                        if FSM.debug:
                            sys.stderr.write("now to replay state '"+s.name+"', with no memory\n")
                        outstream += s.replay()
                    elif len(args)==1:
                        if FSM.debug:
                            sys.stderr.write("now to replay state '"+s.name+"' with memory of length : "+str(len(s.store[0]))+"\n")
                        #sys.stderr.write("state store is now "+str(s.store)+"\n")
                        # sys.exit()
                        outstream += s.replay(s.store[0]) # transmit states' store
                        s.store = s.store[1:] # next time, we'll pick up the next store corresponding to the following occurence of the same state's instance
                    elif len(args)==2 and s.oneshot == False:
                        if FSM.debug:
                            sys.stderr.write("now to replay state '"+s.name+"' with memory of length : "+str(len(s.store[0]))+"\n")
                        outstream += s.replay(s.store[0],s) # transmit state's store, AS WELL AS THE CURRENT STATE
                        s.store = s.store[1:] # next time, we'll pick up the next store corresponding to the following occurence of the same state's instance
                    elif len(args)==2 and s.oneshot == True: # assemble memory chunks together and process in one go
                        if not s.done: # for oneshot only
                            # concatenate the memory store:
                            concatenation = []
                            for chunck in s.store:
                                concatenation.extend(chunck)
                            outstream += s.replay(concatenation,s)
                            s.done = True
                    else:
                        raise("replay function '"+s.replay.__name__+"' associated to state expects too many arguments")
            else:
                raise("should never end-up here")
        return outstream

    def deleteDataStructures(self):

        self.current = 0
        self.trajectory = []

        self.states = []
        for s in self.states:
            del s
        self.transitions = []
        for t in self.transitions:
            del t
        for s in State.states.iteritems():
            del s
        for t in Transition.transitions:
            del t
        State.states = {}
        Transition.transitions = []

        
