#!/usr/bin/python

'''
  this code assumes V6.5.seq format stability
'''


# should add an option to preserve beam 1 information in the output file (may be the default)

# Handling of polarities:
#
# as a rule, all magnets for which the (sole) non-zero K changes sign, should keep their
# polarity unchanged. Conversely, all magnets fo which the K coefficient changes sign
# should change their polarity sign. It is not sufficient to see if it is a quadrupole:
# one must see if it is a normal or skewed quadrupole: the former one exhibit K sign change,
# whereas the latter one does not. Therefore, the former one does not need to change its
# polarity whereas the latter one changes polarity.

# warning: some installed elements in the sequence bear the same name but are installed twice for beam 1 and beam 2.
# the reflection modifies their parameters, and should ideally be discarded.

# major different between the 'sequence' and 'layoutapertures' modes: the former reflects the beam in the main(),
# whereas the second relies on both the main() and a sequence reversal in the FSM, as a 'oneshot' action.

# 5 November 2009: -a option removes B1 elements by default, unless specified otherwise by the -p or --paste option

import time
import optparse
import copy
import shutil

try:
    import cProfile
    profiling = True
except:
    profiling = False
    pass

import re
import sys
import os
import inspect

import madMathExpr
from fsm import FSM, Transition, State



rootTypes = ('SBEND', 'RBEND', 'DIPEDGE',\
             'VKICKER', 'HKICKER', 'KICKER','TKICKER', \
             'QUADRUPOLE', 'SEXTUPOLE','OCTUPOLE','MULTIPOLE',\
             'MARKER', 'PLACEHOLDER', 'INSTRUMENT', 'MONITOR',\
             'ECOLLIMATOR','RCOLLIMATOR','RFCAVITY','SOLENOID')

global debug
global quiet
global discardB1

def printStderr(str):
    global quiet
    if not quiet:
        sys.stderr.write(str+'\n')



class ReflectorException(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Beam: # actually a sequence
    beams = {}
    def __init__(self,name):
        self.name = name
        self.sequence = []
        Beam.beams[self.name] = self
        self.done = False # dirty trick to make sure that the beam will not be processed more than once by the FSM... (reset whe cleaning the data structures)
    def reflect(self): # static/class method
        printStderr("beam "+self.name+" contains "+str(len(self.sequence))+" elements")
        for element in self.sequence:
            if element.beam == secondBeam:
                element.reflect() # apparently does not suffice for the installation
                element.reflection() # 9 september 2009 replaced the above
            else:
                pass # do not touch elements of the first beam

        # now reverse the order of the elements in the beam
        self.sequence.reverse() # in place
            
        printStderr(str(len(self.sequence)) + " elements were reflected")

    def rename(self,name): # to rename secondary beam
        # very expensive as all elements ' names suffixes must be changed and propagated to the
        # parameter keys etc...
        pattern = re.compile('^LHCB(\d)$')
        m = pattern.match(name)
        if m:
            if m.group(1)!='2' and m.group(1)!='4':
                raise ValueError("invalid beam name specified")
            suffix = '.B'+m.group(1)
        else:
            raise ValueError("invalid beam name specified")

        # (1) update the Parameter structures + (2) self.sequence:
        for e in self.sequence:
            oldName = e.name
            if not ( oldName[-3:]=='.B2' or oldName[-3:]=='.B4'):
                raise ValueError("invalid element name suffix for secondary beam")
            else:
                reflect = {}
                reflect['.B2'] = '.B4'
                reflect['.B4'] = '.B2'
                newName = oldName[:-3] + reflect[ oldName[-3:] ]
            if Parameter.elementParameters.has_key(oldName):
                Parameter.elementParameters[newName] = Parameter.elementParameters[oldName]
                # delete the old key
                del Parameter.elementParameters[oldName]
            else:
                raise ValueError("no parameters found for "+oldName)
            
            # also update the Parameter'elementParametrization structure to preserve the ordering
            # => this actually done automatically as the element did not change, only its name

        
            e.name = newName

        
        # (2) update the list of elements
        

        
        self.name = name # as when B2 is renamed as B4
        


    def getName(self):
        return self.name

    def deleteDataStructures(): # delete contents but will keep the firstBeam and secondBeam objects IS IT WHAT WE WANT => yes go through string
        for k,b in Beam.beams.iteritems():
            b.sequence = []
    deleteDataStructures = staticmethod(deleteDataStructures)


firstBeam = Beam('LHCB1') # default
secondBeam = Beam('LHCB2') # only a guess, will be renamed once actual sequences are discovered in the file

class Parameter:
    elementParametrization = [] # a list of element-names in the order their params register
    elementParameters = {} # a dictionary of parameter lists, where key is the element names
    def __init__(self,name,assignment,expression,parameterType):

        name = name.upper() # just to make sure, use capitals internally and both lower and upper cases for input and output
        
        # parameterType is either "combined" or "separated" depending on whether parameter is created
        # as part of an element instantiation or supplied separately
        if (parameterType != 'combined') and (parameterType != 'separated'):
            raise ReflectorException("parameter type should be either 'combined' or 'separated'")
        else:
            self.parameterType = parameterType

        name = name.strip() # just in case, remove heading and trailing blanks if any
        self.name = name

        expression = expression.strip() # remove heading and trailing blanks if any

        # the following parameters never change sign
        if (name == 'SLOT_ID') or (name == 'FROM') or (name == 'ASSEMBLY_ID')\
               or (name == 'APERTYPE') or (name == 'APERTURE'):
            self.expression = expression # record the expression as-is
        else:
            # format expression
            # (1) standard spacing within parenthesis
            patternStr = r'^\{(.+)\}$'
            match = re.match(patternStr,expression)
            if match:
                parenthesized = match.group(1)
                parts = parenthesized.split(',')
                nParts = len(parts)
                newExpression ='{'
                counter = 0
                for part in parts:
                    counter = counter+1
                    part = part.strip() # remove heading and trailing blanks
                    patternStr = r'^[\w\d].+$'
                    match = re.match(patternStr,part)
                    if match:
                        part = '+' + part # make the sign explicit
                    if counter < nParts:
                        newExpression = newExpression + " " + part + ","
                    else:
                        newExpression = newExpression + " " + part
                # reassemble the string
                newExpression = newExpression + '}'
                self.expression = newExpression
            else:
                patternStr = r'^[\w\d].+$'
                match = re.match(patternStr,expression)
                if match:
                    # put a plus sign in front of the expression
                    newExpression = '+' + expression
                    self.expression = newExpression
                
                # finally, record the expression as-is
                else:
                    self.expression = expression

        self.assignment = assignment # := or =

    def deleteDataStructures(): # useful for double reflection
        for parameter in Parameter.elementParameters:
            del parameter
        for parametrization in Parameter.elementParametrization:
            del parametrization
        Parameter.elementParametrization = []
        Parameter.elementParameters = {}

        printStderr("deleteDataStructures of Parameter")

        
    deleteDataStructures = staticmethod( deleteDataStructures )

    def setExpression(self,expression): # to force expressions when reflecting elements one-by-one
        self.expression = expression
 
    def registerParameters(elementName,parameterList):
        
        # check if the parameter dictionary alreay contains the elementName as key
        if Parameter.elementParameters.has_key(elementName):
            #print "WARNING parameter list not empty for elementName '"+elementName+"'"
            # the key already exists: we cannot simply assign the parameterList but expand the existing one
            existingParamList = Parameter.elementParameters[elementName]
            for parameter in parameterList:
                alreadyExists = False # default
                for existingParameter in existingParamList:
                    if existingParameter.getName() == parameter.getName():
                        alreadyExists = True
                if not alreadyExists:
                    Parameter.elementParameters[elementName].append(parameter)
        else:
            Parameter.elementParameters[elementName] = parameterList;
            Parameter.elementParametrization.append(elementName) # to retreive elements name in order
    registerParameters = staticmethod(registerParameters)
    def getName(self):
        return self.name
    def getExpression(self):
        return self.expression
    def getAssignment(self): # returns '=' or ':='
        return self.assignment

class Element: # the base class for all elements that may be affected by a sequence-reflection
    elements = []
    elementsDictionary = {} # a structure to boost the time spent to find-out if element is already known
    def __init__(self,name,template,instanceStr,beam=0): # instanceStr=0 means we instantiate without installing
        
        self.name = name
        self.parameters = []
        self.template = template
        self.reflected = False # for debug purpose only
        self.signChanged = False # only useful for magnets, to check whether POLARITY needs to be changed
        self.beam = beam

        if Element.elementsDictionary.has_key(name):
            raise ReflectorException("attempt to create element '"+name+"' twice")
        else:
            Element.elementsDictionary[name] = self # do we really need to store anything?
        
        Element.elements.append(self) # grow the list of element instances in the sequence

        # decide whether the element belongs to the first (1) or the second beam (2 or 4), depending of its suffix


        if self.name[-3:] == '.B1' and ((not beam) or (beam==firstBeam)):
            self.beam = firstBeam
            firstBeam.sequence.append(self)
        elif (self.name[-3:] == '.B2' or self.name[-3:] == '.B4') and ((not beam) or (beam==secondBeam)):
            self.beam = secondBeam
            secondBeam.sequence.append(self)
        else:
            #pattern = re.compile(r'IP\d')
            #m = pattern.match(self.name)
            #if m:
            #    pass # this is an IP for which we have no class for the time being
            #else:
            # wrong: IP is an instance of Marker
            if not beam:
                printStderr("failed to infer beam from device name '"+self.name+"' ("+self.name[-3:]+")")
            elif self.beam == firstBeam and beam == secondBeam:
                printStderr("device " + self.name + "installed on both beams!") # NEVER THE CASE as LHCB1 sequence is NOT parsed
            else:
                if debug:
                    printStderr("inherit beam from the sequence in which device "+self.name+" is installed ("+beam.name+")")
                self.beam = beam
                beam.sequence.append(self) # beam is always the second beam

    def deleteDataStructures(): # useful for double reflection
        for element in Element.elements:
            del element
        Element.elements = []
        Element.elementsDictionary = {}
    deleteDataStructures = staticmethod(deleteDataStructures)

    def factory(elementName,elementTemplateName,instanceStr,beam=0): # static/class method
        # on second run with layoutaperture we are going to invoke the following with elementTemplateName == 'marker' which is a root class
        elementTemplate = ElementTemplate.getTemplateByName(elementTemplateName)
        elementType = elementTemplate.getRootType() # not getUnderlyingType

        # in aperture layout file, types are in lower case => convert to upper case
        #elementType = elementType.upper()

        for cls in [Rbend,Sbend,\
                   Quadrupole,Sextupole,Octupole,Multipole,\
                   Kicker,VKicker,HKicker,TKicker,\
                   Solenoid,ElSeparator,Monitor,Instrument,\
                   RfCavity,\
                   RCollimator,ECollimator,\
                   Marker,PlaceHolder]:
            if elementType == (cls.__name__).upper():
                return cls(elementName,elementTemplateName,instanceStr,beam)
        printStderr( "failed to identify class for " + elementType)
        return Undefined(elementName,elementTemplateName,instanceStr)

    factory = staticmethod(factory)
    
    def getName(self):
        return self.name

    def addParameter(self,name,assignment,expresssion):
        param = Parameter(name,assignment,expression)
        self.parameters.append(param)
    def getParameters(self): # physical parameters
        return self.parameters

    def getInstantiationParameters(self): # instantiation parameters such as 'at' and 'from'
        # return self.instantiationParameters # not to be mixed with the 'physical' parameters of the element
        return self.getDefinitionParameters() # this function is now redundant with the next call
        # return Parameter.elementParameters[self.name]

    def getDefinitionParameters(self):
        return Parameter.elementParameters[self.name]

    def getTemplate(self):
        return self.template

    def getElementByName(name): # static/class method
        found = False
        for element in Element.elements:
            if element.getName() == name:
                found = True
                theElement = element
        if found == True:
            return theElement
        else:
            sys.stderr.write('WARNING, could not find element of name '+name+' for which a parameter is created\n')
    getElementByName = staticmethod(getElementByName) # the way to make a static/class method


    def getSequence(): # static/class method
        return Element.elements
    getSequence = staticmethod(getSequence)

    def getInstantiationStr(self): # the instance:type, at=..., from= statement
        # TO WORK WITH SEQUENCE, THIS FUNCTION SHOULD BE RESTORED TO WHAT IT WAS BEFORE
        # WITH ALL INSTANTICIATION PARAMETERS BEING OUTPUT - SEE IN THE CVS FOR GETBEAM
        str = self.name+":"+self.template+","
        for p in self.instantiationParameters:
            if p.getName()=='AT' or p.getName()=='FROM':
                str = str + p.getName()+p.getAssignment()+p.getExpression()
                if p == self.getInstantiationParameters()[-1]: # last in list
                    str = str + ";"
                else:
                    str = str + ","
            else:
                continue # omit this parameter
        str = "  " + str + "\n" # to reproduce formatting of reference beam_four.seq

        # apply some cosmetics for the time-being: remove all spaces to compare beam_four_aligned_clean.seq
        newStr = ""
        for c in str:
            if c!= " ":
                newStr = newStr+c
        str = newStr
        return str

    # for layoutaperture processing only
    def getDefinitionStr(self):
        str = self.name+": "+self.template+","
        for i,p in enumerate(self.getInstantiationParameters()):
            if p.getName()=='AT' or p.getName()=='FROM':
                continue # omit this one
            else:
                # post-processing for the output line to look like the original
                pattern = re.compile(r'^[\s\t]*\{(.+)\}[\s\t]*$')
                m = pattern.match(p.getExpression())
                if m:
                    expr = "{"
                    parts = m.group(1).split(',')
                    for part in parts:
                        s = part.strip() # remove leading / trailing blanks
                        if s[0]=='+':
                            expr += s[1:] # remove leading +
                        else:
                            expr += s
                        if part != parts[-1]: # not the last one
                            expr +=", "
                    expr += "}"
                else:
                    expr = p.getExpression()
                    if expr[0] == '+':
                        expr = expr[1:]# remove leading +
                    expr = " "+expr # leading space: same discrepancy between simple and array parameters!!
                    pass # not an accolade
                str += " "+p.getName().lower()+p.getAssignment()+ expr + "," # in layoutaperture file names are lower cases
        # replace last , by ;
        str = str[:-1]
        str += ";"
        str += "\n"
        return str

    # for layoutaperture processing only
    def getInstallationStr(self):
        installationStr = "install, element = "+self.name+","
        str = ""  # will stay empty if the element has no AT and FROM attributes
        for i,p in enumerate(self.getInstantiationParameters()):
            if not (p.getName()=='AT' or p.getName()=='FROM'):
                continue # omit this one
            if p.getName()=='FROM': # the first one
                str += ","
            # remove leading +, as in the original file to ease comparison
            if p.getExpression()[0]=='+':
                expr = p.getExpression()[1:]
            else:
                expr = p.getExpression()
            str = str + " " + p.getName().lower()+"="+" "+expr
            # in layoutaperture files, 'at' and 'from' are in lower cases => lower()
        if str != '':
            installationStr += str
            installationStr += ';\n'
            return installationStr
        else:
            return '' # empty string

    def getInstallationStrAsInSequence(self,frontSpace): # in V6.5.seq, first character is either left-aligned or after a space
        sp = ''
        for i in range(0,frontSpace):
            sp += ' '
        installationStr = sp + self.name+":"+self.template+','
        tabs = ''
        for i in range(0,26-len(installationStr)):
            tabs += ' '
        installationStr += tabs
        str = ''
        for i,p in enumerate(self.getInstantiationParameters()):
            if p.getName() not in ['AT','FROM','ASSEMBLY_ID','SLOT_ID','MECH_SEP','TILT']:
                # should not show up
                continue
            if p.getName()!='AT': # the first one
                str += ","            
            if p.getName()=='FROM': # in the input V6.5.seq, there are some tabulations we must retain
                fromTabs = ''
                for i in range(0,94-len(str)):
                    fromTabs += ' '
                str += fromTabs
            # remove leading +, as in the original file to ease comparison
            if p.getExpression()[0]=='+' and p.getName() != 'TILT': # tilt keeps positive sign
                expr = p.getExpression()[1:]
            else:
                expr = p.getExpression()
            str = str + " " + p.getName().lower()+"="+" "+expr
            # in layoutaperture files, 'at' and 'from' are in lower cases => lower()
        if str != '':
            installationStr += str
            installationStr += ';\n'
            return installationStr
        else:
            return '' # empty string        
    
    

    def reflection(self):
        
        # specific handling of IP elements:
        patternStrIP = '^IP([1-8])(\.L1)?$'
        patternIP = re.compile(patternStrIP)
        match = patternIP.match(self.name)
        if match:
            indexIP = match.group(1)
            isIP = True
        else:
            isIP = False # most probable case

        if not Parameter.elementParameters.has_key(self.name):
            raise ValueError("error: element "+self.name+" has no parameter.")
        
        # change the location parameters (instantiation parameters)
        for p in Parameter.elementParameters[self.name]:         
            #if param.getName() == "slot_id":
            #    print "SLOT_ID still here" # never the case -> can remove this test
            if p.getName() == "AT":
                #print("reflect location")
                expr = p.getExpression()
                # change sign of the numeric / symbolic expression
                # for this we ideally need a simple mathematical expression parser
                # as a shortcut, let's simply change the sign of all expressions
                # except those that are parenthesized
                # NO NEED TO REMOVE BLANKS: THIS IS DONE INTERNALLY BY madMathExpr
                # expr = madMathExpr.removeBlanks(expr) # utility function should be relocated elsewhere
                # print "try to match '"+expr+"'"                

                if isIP:
                    lStr = "LHCLENGTH"
                    if expr.find(lStr)>=0: # already reflected once
                        mathExpr = madMathExpr.MathExpr.tryMatch(expr[expr.find(lStr)+len(lStr):]) # part after LHCLENGTH
                        mathExpr.negate()
                        negatedExpr = mathExpr.getStr()                        
                        p.setExpression(negatedExpr)
                    else:
                        mathExpr = madMathExpr.MathExpr.tryMatch(expr)
                        mathExpr.negate()
                        negatedExpr = mathExpr.getStr()
                        lhcLengthComplement = lStr + negatedExpr
                        p.setExpression(lhcLengthComplement)
                else:
                    mathExpr = madMathExpr.MathExpr.tryMatch(expr)
                    mathExpr.negate()
                    negatedExpr = mathExpr.getStr()                    
                    p.setExpression(negatedExpr)

                
                break # exit for-loop



    def parseDeclaration(self,declStr):
        printStderr('parseDeclaration() should be implemented by the magnet''s derived class')


    def oppositeParameter(self,paramName):
        # returns 'True' if takes effects, 'False' otherwise, which is useful for magnets
        # to record whether or not their K changed sign, and in turn, whether or not they
        # should change polarity
        parameters = Parameter.elementParameters[self.name] # list of parameters of this element
        for parameter in parameters:
            if parameter.getName() == paramName:           
                # this is the parameter for which we need to take the opposite of the expression
                expr = parameter.getExpression()

                try:
                    mathExpr = madMathExpr.MathExpr.tryMatch(expr)
                    mathExpr.negate()
                    newExpr = mathExpr.getStr()
                    parameter.setExpression(newExpr)
                    return True
                except madMathExpr.MathException, e: # from Python 2.6, should end with "as e" instead
                    raise ReflectorException("MathException caught when trying to negate expression '"+expr+\
                                             "' of parameter " + paramName)
                
        return False # the looked-for parameter does not even exist

    def swapParameters(self,paramName1,paramName2):
        parameters = Parameter.elementParameters[self.name] # list of parameters of this element
        found1 = False
        found2 = False
        for parameter in parameters:
            if parameter.getName() == paramName1:
                param1 = parameter
                found1 = True
            if parameter.getName() == paramName2:
                param2 = parameter
                found2 = True
        if found1 and found2:
            expr1 = param1.getExpression()
            expr2 = param2.getExpression()
            param1.setExpression(expr2)
            param2.setExpression(expr1)
        else:
            if (not found1) and (not found2):
                pass
            elif found1: # and not found2
                # replace parameter 1 by parameter 2
                param1.setName(paramName2)
                # and keep the expression
            elif found2: # and not found1
                # replace parameter 2 by parameter 1               
                param2.setName(paramName1)
                # and keep the expression             
            else:
                raise ReflectorException("should never end-up here")

    def kChangeSign(self):
        self.signChanged = True
    def kChangedSign(self):
        return self.signChanged
    

class Rbend(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
        pass
    def reflect(self):
        # as Sbend
        self.oppositeParameter('MECH_SEP')        
        self.oppositeParameter('TILT')
        if self.oppositeParameter('K0S'):
            self.kChangeSign()
        self.oppositeParameter('E1')
        self.oppositeParameter('E2')
        self.oppositeParameter('K1')            
        self.oppositeParameter('K2')
        self.swapParameters('FINT','FINTX')
        self.swapParameters('E1','E2')
        self.swapParameters('H1','H2')
        if not self.kChangedSign():
            self.oppositeParameter('POLARITY') # all upper-cases

class Sbend(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
        pass
    def reflect(self):
        # as Rbend
        self.oppositeParameter('MECH_SEP')        
        self.oppositeParameter('TILT')
        if self.oppositeParameter('K0S'):
            self.kChangeSign()
        self.oppositeParameter('E1')
        self.oppositeParameter('E2')
        self.oppositeParameter('K1')
        self.oppositeParameter('K2')
        self.swapParameters('FINT','FINTX')
        self.swapParameters('E1','E2')
        self.swapParameters('H1','H2')
        if not self.kChangedSign():
            self.oppositeParameter('POLARITY') # all upper-cases

class Quadrupole(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam) # should be Super.__init__ ...
    def reflect(self):
        self.oppositeParameter('MECH_SEP')        
        if self.oppositeParameter('K1'): # iff sign-change is effective, polarity changes, otherwise this is a skew quad
            self.kChangeSign()
        self.oppositeParameter('TILT')
        if not self.kChangedSign():
            self.oppositeParameter('POLARITY')

class Sextupole(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
    def reflect(self):
        self.oppositeParameter('MECH_SEP')        
        if self.oppositeParameter('K2S'):
            self.kChangeSign()
        self.oppositeParameter('TILT')
        if not self.kChangedSign():
            self.oppositeParameter('POLARITY')

class Octupole(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
    def reflect(self):
        self.oppositeParameter('MECH_SEP')        
        if self.oppositeParameter('K3'):
            self.kChangeSign()
        self.oppositeParameter('TILT')
        if self.kChangedSign():
            self.oppositeParameter('POLARITY')

class Multipole(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
    def reflect(self):
        self.oppositeParameter('MECH_SEP')        
        self.oppositeParameter('TILT')
        try:
            parameters = Parameter.elementParameters[self.name]
        except madMathExpression.MathException, e: # from Python 2.6, should end with "as e" instead
            raise ReflectorException("Caught MathException: "+ str(e))

        for parameter in parameters:

            if parameter.getName() == 'KNL':
                # put minus sign in front of even multipoles
                expr = parameter.getExpression()
                   
                withoutAccolades = re.sub(r'\{(.+)\}',r'\1',expr)

                kExpressions = withoutAccolades.split(',')
                even = True
                kNewExpressions = []
                for kExpr in kExpressions:
                    kExpr = kExpr.strip()

                    if not even:
                        mathExpr = madMathExpr.MathExpr.tryMatch( kExpr )
                        mathExpr.negate()
                        negatedExpr = mathExpr.getStr()
                        kNewExpressions.append( negatedExpr )
                    else:
                        kNewExpressions.append(kExpr)
                    even = not even
                # now reassemble the parameter's expression and store it
                newExpr = "{"
                counter = 0
                for kNewExpr in kNewExpressions:
                    counter = counter+1
                    newExpr = newExpr + " " + kNewExpr
                    if counter != len(kNewExpressions):
                        newExpr = newExpr + "," # current focus
                newExpr = newExpr + "}"
                parameter.setExpression(newExpr)
              
            if parameter.getName() == 'KSL':
                # put minus sign in front of odd skew multipoles
                expr = parameter.getExpression()
                # remove heading and traling spaces
                expr = expr.strip()          
                withoutAccolades = re.sub(r'\{(.+)\}',r'\1',expr)          
                kExpressions = withoutAccolades.split(',')
                even = True
                kNewExpressions = []
                for kExpr in kExpressions:
                #    print "k-expression="+kExpr
                    kExpr = kExpr.strip()
                    if even:
                        mathExpr = madMathExpr.MathExpr.tryMatch( kExpr )
                        mathExpr.negate()
                        negatedExpr = mathExpr.getStr()
                        kNewExpressions.append( negatedExpr )
                    else:
                        kNewExpressions.append(kExpr)
                    even = not even
                # now reassemble the parameter's expression and store it
                newExpr = "{"
                counter = 0
                for kNewExpr in kNewExpressions:
                    counter = counter+1
                    newExpr = newExpr + " " + kNewExpr
                    if counter != len(kNewExpressions):
                        newExpr = newExpr + ","
                newExpr = newExpr + "}"
                parameter.setExpression(newExpr)               

class Kicker(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
    def reflect(self):
        self.oppositeParameter('MECH_SEP')        
        self.oppositeParameter('TILT')
        #self.oppositeParameter('KICK') 30.09.2009 - assume no such parameter for a KICK
        self.oppositeParameter('VKICK')
        # HKICK left as is (parameter exists but is kept unchanged by the reflection)

class VKicker(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
    def reflect(self):
        self.oppositeParameter('MECH_SEP')        
        self.oppositeParameter('TILT')
        self.oppositeParameter('KICK')
        #self.oppositeParameter('VKICK') 30.09.2009 - assume no such parameter for a VKICK
        # HKICK left as is

class HKicker(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
    def reflect(self):
        self.oppositeParameter('MECH_SEP')        
        self.oppositeParameter('TILT')
        # KICK left as is
        #self.oppositeParameter('KICK') # 30.09.2009 - assume no such parameter for a HKICK
        # HKICK left as is

class TKicker(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
    def reflect(self):
        self.oppositeParameter('MECH_SEP')       
        # apply the same rules as for a Kicker
        self.oppositeParameter('TILT')
        # HKICK left untouched
        self.oppositeParameter('VKICK')

class Solenoid(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
    def reflect(self):
        self.oppositeParameter('MECH_SEP')        
        self.oppositeParameter('KS')
        self.oppositeParameter('KSI')

class ElSeparator(Element): # electrostatic separator
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
    def reflect(self):
        self.oppositeParameter('MECH_SEP')        
        self.oppositeParameter('TILT')
        self.oppositeParameter('EX')

class RfCavity(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
    def reflect(self):
        self.oppositeParameter('MECH_SEP')        
        if self.reflected == True:
            raise ReflectorException("element "+self.name+" to be reflected for the second time!")
        if self.reflected == False:
            self.reflected = True

        # 20 january: the following should become obsolete as all physical parameters
        # are now associated to the instance (after installed) instead of to the template
        # Thys supposed to ask Pascal Leroux to associated the RFCAVITY parameters to the
        # the installed element instead of to its class...
        
        try:
            parameters = Parameter.elementParameters[self.name]
        except:
            printStderr("warning RF cavity " + self.name +\
                                     " has no instance parameter")
            return

        for parameter in parameters:
            if parameter.getName() == 'LAG':
                expr = parameter.getExpression()
                newExpr = "0.5-("+expr+")"
                
                # try to simplify the expression (no numerical computations performed)
                mathExpr = madMathExpr.MathExpr.tryMatch(newExpr)
                mathExpr = mathExpr.simplify() # would get rid of terms such as 0.5-(0.5)...
                newExpr = mathExpr.getStr()

                # as simplification of mathematical expressions is not implemented yet, let's take a shortcut that works with the current file:
                pattern = re.compile('^\+?0.5-\(\+?0.5-\((.+)\)\)$')
                m = pattern.match(newExpr)
                if m:
                    newExpr = m.group(1)
                
                # explicit sign '+'
                patternStr = r'^[\w\d].+$'
                match = re.match(patternStr,newExpr)
                if match:
                    newExpr = '+' + newExpr
                parameter.setExpression(newExpr)

class Monitor(Element): # for beam-position monitors (BPM)
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
        pass
    def reflect(self):
        self.oppositeParameter('MECH_SEP')        
        pass # assume nothing to do for a BPM

class RCollimator(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
    def reflect(self):
        self.oppositeParameter('MECH_SEP')        
        pass

class ECollimator(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
    def reflect(self):
        self.oppositeParameter('MECH_SEP')        
        pass

class Instrument(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
    def reflect(self):
        self.oppositeParameter('MECH_SEP')        
        pass    

class PlaceHolder(Element): # handled in the same fashion as a Marker
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
    def reflect(self): # reflect MECH_SEP if such parameter exists for this instance
        if self.name in Parameter.elementParameters:
            for p in Parameter.elementParameters[self.name]:
                if p.getName() == 'MECH_SEP':
                    self.oppositeParameter('MECH_SEP')
                    sys.stderr.write('SOFARSOGOOD\n')
        
class Marker(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
        pass
    def reflect(self): # reflect MECH_SEP if such parameter exists for this instance
        if Parameter.elementParameters.has_key(self.name):
            for p in Parameter.elementParameters[self.name]:
                if p.getName() == 'MECH_SEP':
                    self.oppositeParameter('MECH_SEP')
                  
            
class Undefined(Element):
    def __init__(self,name,type,instanceStr,beam=0):
        Element.__init__(self,name,type,instanceStr,beam)
        pass
    def reflect(self):
        printStderr("Undefined '"+self.getName()+"' asked to mirror its features")



# element template
class ElementTemplate:
    templates = []

    def deleteDataStructures(): # useful for double reflection
        for template in ElementTemplate.templates:
            del template
        ElementTemplate.templates = []
    deleteDataStructures = staticmethod(deleteDataStructures)

    def __init__(self,name,underlyingType,templateDefinitionStr):
        self.name = name
        self.underlyingType = underlyingType
        # now look for the original root type
        # check whether the template is a root type or an intermediate type
        # move up the creation hierarchy to find-out the original type of the element
        rootTypeFound = False
        #intermediateTemplate = self
        typeName = self.underlyingType
        depth = 0
        while not rootTypeFound:

            for rootType in rootTypes:
                if typeName == rootType:
                    rootTypeFound = True
                    self.rootType = typeName

            if not rootTypeFound:
                depth = depth + 1
                type = ElementTemplate.getTemplateByName(typeName)
                typeName = type.getUnderlyingType()
                # move up in the type creation history/hierarchy
            else:
                pass

        self.templateDefinitionStr = templateDefinitionStr
        # parse template definition string to fill-in template definition parameters
        # (as in Element, except no 'at',...'from')
        self.definitionParameters = [] # a list of definition-paramaters

        # note the following code should be replicated elsewhere in the program instead of relying on the PARENTHESIZED processing

        patternStr = r'[\s\t]*([\w\d\.]+)[\s\t]*=[\s\t]*(\{?[\w\d\.,\s\t]+\}?)[\s\t]*[,;]' # note cannot cope with nested parentheses
        l = re.findall(patternStr,self.templateDefinitionStr) # findall for all iterations

        #if len(l)==0:
        #    raise ValueError("no parameter parsed by ElementTemplate constructor")
        
        for match in l:
            parameterName = match[0]
            parameterExpr = match[1]
            newDefinitionParameter = Parameter(parameterName,'=',parameterExpr,'combined')
            self.definitionParameters.append(newDefinitionParameter) # temporary structure                
                
        # make sure the template is not created twice (this code should be removed eventually)
        # should now register the parameters list for the name of the element-template (instead of elname)
        Parameter.registerParameters(self.name,self.definitionParameters) # sole use of self.definitionParameters
        for template in ElementTemplate.templates:
            if template.getName() == name:
                raise ReflectorException("attempt to create template '"+name+"' twice")
        ElementTemplate.templates.append(self)

    def getName(self):
        return self.name

    def getTemplateByName(name): # static/class method
        for template in ElementTemplate.templates:
            if template.name == name:
                return template
        raise ReflectorException("Failed to find template with name '"+\
                                 name+\
                                 "' using option -e or --expanded_types might solve this problem.")
    getTemplateByName = staticmethod(getTemplateByName)

    def getUnderlyingType(self): # first level in the template's creation history
        return self.underlyingType

    def getRootType(self): # last level in the template's creation history
        return self.rootType

    def parseDeclaration(self,declStr): # invoked only if not implemented in concrete class
        printStderr('parsing not implemented for this template type')

# elements (positionned on curvilign abciss and forming the actual sequence)

class SequenceFile:

        def __init__(self,name):
            # for some reason, files from the database may contain a mixture of DOS and Unix style end of lines
            # to fix this, always convert the file to a local copy with Unix format
            printStderr('input filename='+name)
            parts = name.split('/')
            tempFileName = parts[-1]+'.temp'
            shutil.copy(name,tempFileName)
            printStderr('filename='+tempFileName)
            os.system('dos2unix '+tempFileName)  
            self.name = name
            self.fileHandle = open(tempFileName)
            self.fileListing = self.fileHandle.readlines()
            printStderr("sequence-file now contains " + str(len(self.fileListing)) + " lines")            
            self.fileHandle.close()
            os.remove(tempFileName)
            self.index=0

        def setContents(self, hugeString):
            # warning \n\n should still capture the empty line
            def multipleLineReplacement(match):
                nLines =  len(match.group(1))
                #printStderr('found '+str(nLines)+' successives carriage returns')
                return '\n|'+str(nLines)+'|\n'
            
            pattern = re.compile(r'(\n{2,10})')
            hugeString = re.sub(pattern,multipleLineReplacement,hugeString)

            lines = hugeString.split('\n')
            
            self.fileListing = [] # reset
            for line in lines:
                patternMultipleLineFeed = re.compile(r'^\|(\d+)\|$')
                m = patternMultipleLineFeed.match(line)
                if m:
                    for i in range(0,int(m.group(1))-1):
                        self.fileListing.append('\n')
                else:
                    self.fileListing.append(line) # second time (for double reflection)
            printStderr("sequence-file now contains " + str(len(self.fileListing)) + " lines")
                
        def close(self):
            self.fileHandle.write("return;\n")
            self.fileHandle.close()


def outputMagnetConstants(memory): # for sequence processing
    fullStr = ''
    for n in memory:
        out = '  ' + n + ","
        tabs = ''
        for i in range(0,29-len(out)):
            tabs += ' '
        out += tabs
        for p in Parameter.elementParameters[n]:
            if p.getName() not in ['AT','FROM','MECH_SEP','ASSEMBLY_ID','SLOT_ID','KMAX','KMIN','TILT']:
                if p.getName()=='POLARITY': 
                    pName = p.getName().lower() # as in input V6.5.seq, expressions are lower case
                else:
                    pName = p.getName()
                if p.getAssignment() == ':=':
                    pAssignment = ' := ' # add parentheses to retain V6.5.seq formatting
                else:
                    pAssignment = '='
                if p.getExpression()[0]=='{':
                    # convert '{ x...' into '{x...'
                    pExpression = p.getExpression()[0]+p.getExpression()[2:]
                    # remove + signs from parenthesized expression
                    pExpression = pExpression.replace(', +',', ')
                elif p.getExpression()[0] == '+' and p.getName()!='POLARITY':
                    pExpression = p.getExpression()[1:]
                elif p.getExpression() == '0' and p.getName()=='KICK':
                    # in V6.5.seq this shows as 'KICK :=0' with missing space on the rhs
                    pExpression = p.getExpression()
                    pAssignment = ' :=' # overwrite!
                else:
                    pExpression = p.getExpression()
                out += pName + pAssignment + pExpression + ', '

        out = out.rstrip(', ') + ';\n' # replace last ', ' by ';'
        # reflect some anomaly in the input V6.5.seq
        out = out.replace(', -kcd',',-kcd')
        fullStr += out
    return fullStr

def outputAcscaConstants(memory):
    fullStr = ''
    for n in memory:
        out = '  ' + n + ', '
        for p in Parameter.elementParameters[n]:
            if p.getName() in ['VOLT','LAG']:
                if p.getExpression()[0]=='+':
                    pExpression = p.getExpression()[1:]
                else:
                    pExpression = p.getExpression()
                out += p.getName() + ' '+p.getAssignment() + ' '+pExpression + ', '
        out = out.rstrip(', ') + ';\n'
        fullStr += out
    return fullStr


def collectMagnetConstants(lineStr,memory): # for sequence processing
    # in this case, memory will store the name of the element

    patternParamStr = r'^[\s\t]*([_\w\d\.]+),[\s\t]+(.+);$'               
    patternParam = re.compile(patternParamStr)

    match = patternParam.match(lineStr)

    # september 3rd 2009: all the following could be optimized with the re.findall()

    if match:
        elementName = match.group(1)
        expressionsPart = match.group(2)
        # split the expression part
        # by ',', except is the ',' is part of a '{,,,}' sequence, in which
        # case such sequence should not be broken apart => (1) do a replacement
        # (2) do the split (3) re-replace
        
        #LIMITATION: assume only one parenthesized expression in the parameter list...
        patternStr = r'\{([_\w\d\.\+\-\*\s\t,]+)\}'
        pattern = re.compile(patternStr)
        #--- remember {} contents
        matchParenthesis = pattern.search(expressionsPart)
        if matchParenthesis:
            #    parenthesis = True
            inParentheses = matchParenthesis.group(1)
            expressionsPart = pattern.sub('PARENTHESIZED',expressionsPart) # overwrite
        #else:
        #    parenthesis = False
        #---
        parts = expressionsPart.split(',') # only expression-separating ',' should be left-over
        parametersList = []
        
        patternParenthesisStr = r'PARENTHESIZED'
        patternParenthesis = re.compile(patternParenthesisStr)

        for part in parts:
            # is it the parameter which is parenthesized?
            matchAccolades = patternParenthesis.search(part)
            if matchAccolades:
                parenthesis = True
            else:
                parenthesis = False

            patternStr = r'^[\s\t]*([_\w\d\.]+)[\s\t]*(:?=)[\s\t]*(.+)$'
            pattern = re.compile(patternStr)
            matchPart = pattern.match(part)
            # we are sure it should match
            if matchPart:
                parameterName = matchPart.group(1)
                parameterAssignment = matchPart.group(2)
                parameterExpr = matchPart.group(3)
                if parenthesis:
                    # actually not all parameters should undergo this process. Actually assuming only ONE
                    patternStr = 'PARENTHESIZED'
                    pattern = re.compile(patternStr)
                    parameterExpr = '{'+pattern.sub(inParentheses,parameterExpr)+'}'
                newParameter = Parameter(parameterName, \
                                         parameterAssignment, parameterExpr, 'separated')
                parametersList.append(newParameter)

            else: # IF MATCH PART
                printStderr("BAD PARAM '"+part+"'")
                
        Parameter.registerParameters(elementName,parametersList); # FOR PART IN PARTS
        memory.append(elementName)

    else:
        raise ValueError("fail to match function '"+inspect.currentframe().f_code.co_name+"' when encountering '"+lineStr+"'")

def collectB2MagnetConstants(lineStr,memory):
    pattern = re.compile(r'B1[\s\t,=:]')
    if pattern.search(lineStr):
        return # skip this line
    else:
        collectMagnetConstants(lineStr,memory)
    

def lookForMarkerDeclarations(lineStr,memory): # memory stores the marker class name
    
    pattern = re.compile(r'^[\s\t]*([\w\d\.]+):[\s\t]*[Mm][Aa][Rr][Kk][Ee][Rr][\s\t]*,[\s\t]*(.+)$')    
    m = pattern.match(lineStr) # marker and MARKER will be matched                   
    if m:
        elementTemplateName = m.group(1)
        elementType = 'MARKER'
        templateDefinitionStr = m.group(2) # with current implementation, let's discard this
        newElementTemplate = ElementTemplate(elementTemplateName,elementType,templateDefinitionStr)
        memory.append(elementTemplateName)
    else:
        raise ValueError("fail to match function '"+inspect.currentframe().f_code.co_name+"' when encountering '"+lineStr+"'")    

def lookForMarkerInstallations(lineStr,state,memory):
    # marker installation
    # new parameter: state used to find-out what is the current sequence and thus whether or not to reverse order    
    pattern = re.compile(r'^[Ii][Nn][Ss][Tt][Aa][Ll][Ll], [Ee][Ll][Ee][Mm][Ee][Nn][Tt] = ([\w\d\.]+), [Aa][Tt]=(.+), [Ff][Rr][Oo][Mm]= ([\w\d\.]+);$')
    # file previoulsy converted to upper case
    m = pattern.match(lineStr)
    if m:
        success = True
        elementName = m.group(1)
        
        # add two new parameters AT, FROM to this marker                        
        pAt = Parameter('AT','=',m.group(2),'separated')
        pFrom = Parameter('FROM','=',m.group(3),'separated')
        for p in [pAt,pFrom]:
            if Parameter.elementParameters.has_key(elementName):
                pList = Parameter.elementParameters[elementName]
                pList.append(p)
            else:
                Parameter.elementParameters[elementName] = p

        if state.name == 'seq1':
            beam = firstBeam
        elif state.name == 'seq2':
            beam = secondBeam
        else:
            raise ValueError("when looking for instance installations, expect the state of the FSM to be either 'seq1' or 'seq2'")

        memory.append(elementName)
            
    else:  
        raise ValueError("fail to match function '"+inspect.currentframe().f_code.co_name+"' when encountering '"+lineStr+"'")

def lookForClassDeclarations(lineStr,memory): # for sequence processing
    global debug
    lineStr = lineStr.strip('\n') # really useful?
    patternStr = r'^[\s\t]*([_\w\d\.]+)[\s\t]*:[\s\t]*' + r'([_\w\d\.]+)' + r'(.+)$'
    pattern = re.compile(patternStr)
    match = pattern.match(lineStr)

    if match:
        success = True
        elementTemplateName = match.group(1)
        elementType = match.group(2)
        if elementType != 'SEQUENCE':
            # create object for each element-type, with instantiation parameters (litteral expressions)
            templateDefinitionStr = match.group(3)
            newElementTemplate = ElementTemplate(elementTemplateName,elementType,templateDefinitionStr)
            memory.append(lineStr) # in this case memory the input text line for subsequent output upon replay 
            if debug:
                sys.stderr.write('class '+elementTemplateName+' created\n')           
        else: # skip
            pass
    else:
        raise ValueError("fail to match function '"+inspect.currentframe().f_code.co_name+"' when encountering '"+lineStr+"'")
    
def lookForInstanceInstallations(lineStr,state,memory): # for sequence processing
    #  the state of the FSM is used to find out which is the current sequence
    lineStr = lineStr.strip('\n') # really useful? yes in this case
    patternStr =  r'^([\s\t]*)([_\w\d\.]+)[\s\t]*:[\s\t]*([_\w\d\.]+),[\s\t]*(.+)?;$'
    # in the above should also account for the from
    # moreover IP1,...IP8 should not be processed as elements... 
    pattern = re.compile(patternStr)
    match = pattern.match(lineStr)
    if match:
        success = True
        frontSpace = len(match.group(1))
        elementName = match.group(2)
        elementType = match.group(3)
        instanciationStr = lineStr # for time-being, copy line that instanciates the element

        # collect parameters of the element
        parts = match.group(4).split(',')
        parametersList = []
        for p in parts:
            [pName,pExpr] = p.split('=')
            parameterName = pName.strip()
            parameterExpr = pExpr.strip()

            parameterAssignment = '='

            newParameter = Parameter(parameterName, \
                                     parameterAssignment, parameterExpr, 'separated')
            parametersList.append(newParameter)

        
        if state.name == 'seq1':
            beam = firstBeam
        elif state.name == 'seq2':
            beam = secondBeam
        else:
            raise ValueError("when looking for instance installations, expect the state of the FSM to be either 'seq1' or 'seq2'")
                
        newElement = Element.factory(elementName,elementType,instanciationStr,beam)
        Parameter.registerParameters(elementName,parametersList);        
        memory.append([elementName, frontSpace]) # memorize front space to retain input formatting of V6.5.seq   
    else:
        raise ValueError("fail to match function '"+inspect.currentframe().f_code.co_name+"' when encountering '"+lineStr+"'")

# for sequence processing
def lookForMarkerDefinitions(lineStr,memory): # memory stores the marker instance name
    pattern = re.compile(r'([\w\d\.]+)[\s\t]*:[\s\t]*([\w\d\.]+)[\s\t]*,(.+);')
    m = pattern.match(lineStr)
    if m:
        success = True
        elementName = m.group(1)
        elementType = m.group(2)
        instanciationStr = lineStr

        newElement = Element.factory(elementName,elementType,instanciationStr)
 
        expressionsPart = m.group(3)
        # split the expression part
        # by ',', except is the ',' is part of a '{,,,}' sequence, in which
        # case such sequence should not be broken apart => (1) do a replacement
        # (2) do the split (3) re-replace
        
        #LIMITATION: assume only one parenthesized expression in the parameter list...
        patternStr = r'\{([_\w\d\.\+\-\*\s\t,]+)\}'
        pattern = re.compile(patternStr)
        #--- remember {} contents
        matchParenthesis = pattern.search(expressionsPart)
        if matchParenthesis:
            inParentheses = matchParenthesis.group(1)
            expressionsPart = pattern.sub('PARENTHESIZED',expressionsPart) # overwrite
            parts = expressionsPart.split(',') # only expression-separating ',' should be left-over
            parametersList = []

            patternParenthesisStr = r'PARENTHESIZED'
            patternParenthesis = re.compile(patternParenthesisStr)

            for part in parts:
                # is it the parameter which is parenthesized?
                matchAccolades = patternParenthesis.search(part)
                if matchAccolades:
                    parenthesis = True
                else:
                    parenthesis = False

                patternStr = r'^[\s\t]*([_\w\d\.]+)[\s\t]*(:?=)[\s\t]*(.+)$'
                pattern = re.compile(patternStr)
                matchPart = pattern.match(part)
                # we are sure it should match
                if matchPart:
                    parameterName = matchPart.group(1)
                    parameterAssignment = matchPart.group(2)
                    parameterExpr = matchPart.group(3)
                    if parenthesis:
                        # actually not all parameters should undergo this process. Actually assuming only ONE
                        patternStr = 'PARENTHESIZED'
                        pattern = re.compile(patternStr)
                        parameterExpr = '{'+pattern.sub(inParentheses,parameterExpr)+'}'
                        # print "create parameter " + parameterName +" with expression "+parameterExpr
                    newParameter = Parameter(parameterName, \
                                             parameterAssignment, parameterExpr, 'separated')
                    parametersList.append(newParameter)

                else:
                    printStderr("BAD PARAM '"+part+"'")

        Parameter.registerParameters(elementName,parametersList);

        memory.append(elementName)    
    else:
        raise ValueError("fail to match function '"+inspect.currentframe().f_code.co_name+"' when encountering '"+lineStr+"'")

def collectNonB1RelatedLines(lineStr,memory):
    pattern = re.compile('\.B1[\s\t=:,]')
    if pattern.search(lineStr):
        return
    else:
        memory.append(lineStr)
    
def main():

    global mode
    global debug
    global quiet
    global discardB1

    usage = '%prog [options] >! file\n\n'+\
            '\t where output is redirected to a user-specified file.'

    parser = optparse.OptionParser(usage)


    parser.add_option('-s','--sequence',help='reflects the sequence. This is the default mode.',action='store_true')

    parser.add_option('-a','--aperture',help='reflects the layout aperture to convert it into a beam 4 reference system.'+\
                      'the sole parameter to change is mech_sep -> -mech_sep.',action='store_true')
    
    parser.add_option('-f','--filename',help='specifies an input file different from the default one.',\
                      dest='filename',metavar='FILE')

    parser.add_option('-r','--repeat',help='number of times the reflection should be applied from 0 to 2. '+\
                      'Setting reflection to 2 should recover the original file which may help debugging.', dest='repeat')
    
    parser.add_option('-b','--rename_b2_b4',help='swap .B2 and .B4 element suffixes upon reflection.', action='store_true')
    
    parser.add_option('-d','--debug',help='display messages useful for debugging this script.', action='store_true')

    parser.add_option('-q','--quiet',help='do not output any message on stdout or stderr',action='store_true')

    parser.add_option('-p','--paste',help='paste beam 1 and beam 2 information (required for double reflection)',action='store_true')

    parser.add_option('-e','--expanded_types',help='allow instanciation and installation of base elements by treating base classes as concrete types.',action='store_true')
    
    (options, args) = parser.parse_args()

    assert(len(args)==0)

    debug =  options.debug
    rename_b2_b4 = options.rename_b2_b4
    quiet = options.quiet

    if options.repeat:
        repeat = int(options.repeat)
        if not (repeat>=0 and repeat<=2):
            raise ValueError("expect repeat to be 0, 1 or 2, instead of "+str(repeat))
        if repeat>1 and not options.paste:
            raise ValueError("expect option -p or --paste for double reflection")
    else:
        repeat = 1 # default


    discardB1 = not options.paste

    if options.sequence or not options.aperture: # sequence is default mode
        mode = 'sequence'
        # reflect the sequence, as before
        if options.filename:
            filename = options.filename
            filename = os.path.expanduser(filename) # expand ~ if any
        else:
            filename = "/afs/cern.ch/eng/lhc/optics/V6.503/V6.5.seq"   
    elif options.aperture:
        mode = 'layoutaperture'
        # reflects the aperture file
        if options.filename:
            filename = options.filename
            filename = os.path.expanduser(filename) # expand ~ if any
        else:
            filename = "/afs/cern.ch/eng/lhc/optics/V6.503/aperture/layoutapertures.madx"
    else:
        raise ValueError("incorrect option settings.")

    baseClassesAsImplicitTypes = options.expanded_types

    run(filename,repeat,rename_b2_b4,quiet,mode,debug,discardB1,baseClassesAsImplicitTypes) # warning 'mode' also declared as a global!

def run(filename,repeat,rename_b2_b4,quietFlag=True,modeFlag='sequence',debugFlag=False,discardB1=False,baseClassesAsImplicitTypes=False):

    global debug
    global mode
    global quiet

    quiet = quietFlag
    mode = modeFlag
    debug = debugFlag
    
    startTime = time.time()
    

    sequenceFile = SequenceFile(filename)

    reflectFlag = (repeat>0) # i.e. reflect for both "b4" and "b2_twice"

    outstream = ""

    fsm = FSM()
    # lists to be filled in by the FSM for further output

    # for layoutaperture processing only
    def outputTypeDeclarations(memory): # in this case memory contains element templates names
        global debug
        if debug:
            sys.stderr.write('memory is now '+str(memory)+"\n")
        outstream = ''
        for n in memory:
            t = ElementTemplate.getTemplateByName(n)
            outstream += n +": "+t.getUnderlyingType().lower()+", " # lower case for type
            if Parameter.elementParameters.has_key(t.getName()):
                for p in Parameter.elementParameters[t.getName()]:
                    outstream += p.getName().lower()+"= "+p.getExpression()
                    if p==Parameter.elementParameters[t.getName()][-1]: # last paremter
                        outstream += ';'
                    else:
                        outstream += ', '
                outstream += '\n'
        return outstream

    def outputDefinitions(memory): # in this case state's memory contains element names
        printStderr('now to define '+str(len(memory))+' elements')        
        outstream =  ''
        for n in memory:
            if n in Element.elementsDictionary:
                e = Element.elementsDictionary[n]
                outstream += e.getDefinitionStr()
            else:
                printStderr('element '+n+' probably defined but not installed')
        return outstream

    def outputMarkerInstallations(memory,state): # in this case state's memory contains a list of elements' names
        # may be should check that all elements belong to the same beam
        outstream = ''
        if state.name == 'seq1': # in this case, could also forget about the parser's memory content and simply loop over e in firstBeam.sequence
            printStderr('now to install '+str(len(memory))+ " " +firstBeam.name+ ' markers')            
            for n in memory:
                e = Element.elementsDictionary[n]
                outstream += e.getInstallationStr()
        elif state.name == 'seq2': # flush all info => all inserted blank lines and comments will be gathered at the end...
            if not secondBeam.done: # to avoid output of seq2 several times in case the parsing was disrupted by inserted blank lines and comments
                # even if the memory contains a subset due to comments and blank lines
                # let's output the full sequence 2
                printStderr("now to install "+str(len(secondBeam.sequence))+" " +secondBeam.name + " markers in one go (commentaries and blank lines skipped)")
                # actually beam 2 has been reflected in between => forget about the parser's memory and instead read the reflected beam's sequence

                # 6/10/2009: rearrange the sequence so that elements are ordered in the order they are installed rather than
                # in the order they are defined (constructed)

                # memory is properly ordered, not like secondBeam.sequence...
                installationSequence = []
                # printStderr("when entering outputMarkerInstallation for seq2, memory has length "+str(len(memory)))
                for n in memory:
                    installationSequence.append(Element.elementsDictionary[n])

                # time-consuming
                def byInstallationOrder(a,b): # return -1 if a<b, 0 if a==b, +1 if a>b
                    #try:
                    #    if not a in installationSequence:
                    #        printStderr("warning: "+a.name+" not in installation sequence")
                    #    if not b in installationSequence:
                    #        printStderr("warning: "+b.name+" not in installation sequence")
                        ia = installationSequence.index(a)
                        ib = installationSequence.index(b)
                        if (ib-ia)>0:
                            return 1
                        elif (ib-ia)<0:
                            return -1
                        else:
                            return 0
                    #except:
                    #    raise ValueError("fail to order elements "+a.name+" and "+b.name+" in order of installation")

                # first remove from the sequence all elements which have been created but not installed
                #seq = []
                
                #for e in secondBeam.sequence:         
                #    if e in installationSequence:
                #        seq.append(e)
                            
                #seq.sort(byInstallationOrder) # in place

                installationSequence.reverse()
                
                for e in installationSequence:
                    outstream += e.getInstallationStr() # for time being forget about the formatting
                    
                secondBeam.done = True # could rely on oneshot instead
            else:
                return ''
        else:
            raise ValueError("expect state.name to be either 'seq1' or 'seq2")
            
        return outstream

    def outputInstanceInstallations(memory): # in this case, the state's memory contains a list of element names
        # THIS NOW BREAKS IN CASE OF INSERTED LINE OR COMMENTARY => THE SEQUENCE WILL BE OUPTPUT FOR EACH CHUNK OF MEMORY
        # same as for layout aperture apart that the string is formatted differently
        # may be should check that all elements belong to the same beam
        if secondBeam.done:
            return ''
        
        printStderr('now to install '+str(len(secondBeam.sequence))+' elements')
        outstream = ''
        '''
        for [n,frontSpace] in memory:
            e = Element.elementsDictionary[n]
            outstream += e.getInstallationStrAsInSequence(frontSpace)
        '''
        # FOLLOWING FRAGILE: in case of an inserted blank line or comment, the full sequence will be output several times
        # actually beam 2 has been reflected in between => forget about the parser's memory and instead read the reflected beam's sequence
        
        for e in secondBeam.sequence:
            outstream += e.getInstallationStrAsInSequence(0) # for time being forget about the formatting
        secondBeam.done = True
        
        return outstream        
        

    # for both

    def skip(x):
        pass

    def skipReplay(memory):
        return ""

    def record(x,memory): # memory can't be a string or it would be immutable. a list is mutable
        memory.append(x) #
        
    def output(memory):
        # remove comments line by line as a transition only captured one
        out = ""
        for line in memory:
                out = out + line.strip('\n')+'\n'
        return out
    

    
    for iteration in range(1,repeat+1): # performed only once for "b2" and "b4" targets

        passes=['no-processing pass', 'first pass','second pass']
        printStderr(passes[iteration])

        firstBeam.done = False # dirty trick
        secondBeam.done = False # dirty trick

        if iteration==2:
            # second time in loop: we must reinitialize the contents of the sequenceFile
            sequenceFile.setContents(outstream)
            outstream = "" # reset the output data
            # reset the data-structures that accomodates templates, elements and parameters
            Element.deleteDataStructures()
            Parameter.deleteDataStructures()
            ElementTemplate.deleteDataStructures()
            Beam.deleteDataStructures()
            fsm.deleteDataStructures()

        if baseClassesAsImplicitTypes:
            for cls in  [Rbend,Sbend,\
                         Quadrupole,Sextupole,Octupole,Multipole,\
                         Kicker,VKicker,HKicker,TKicker,\
                         Solenoid,Monitor,Instrument,\
                         RfCavity,\
                         RCollimator,ECollimator,\
                         Marker,PlaceHolder]:
                sys.stderr.write("treating "+cls.__name__.upper()+" as a concrete type as well as a base class\n")
                ElementTemplate(cls.__name__.upper(),cls.__name__.upper(),'') # start to fill in the element types

        if mode == 'layoutaperture': # MUST ALSO REINIT THE FSM WHEN ITERATING

            if discardB1:
                seq1Action = skip
                seq1ActionReplay = skipReplay
                startSeq1TransitionReplay = skipReplay
            else:
                seq1Action = lookForMarkerInstallations
                seq1ActionReplay = outputMarkerInstallations # only beam 1 elements names collected in memory
                startSeq1TransitionReplay = output

            # reminder: with re.match, patterns are implictly anchored on the left and right (different from re.search
        
            init = State('start',initial=1)
            header = State('header',action = record, replay = output)
            # states
            declarations = State('decl', action = lookForMarkerDeclarations, replay = outputTypeDeclarations )
            tolerances = State('tol',action= record, replay = output )
            definitions = State('defs',action=lookForMarkerDefinitions, replay = outputDefinitions )
            seq1 = State('seq1',action=seq1Action, replay = seq1ActionReplay ) # beam 1 elements' names collected in memory
            seq2 = State('seq2',action=lookForMarkerInstallations, replay = outputMarkerInstallations, oneshot = True )
            # beam 2 elements' names collected in memory
            # 'oneshot' concatenates memory chunck at replay, which is run in one go.

            end = State('end', final=1)
            
            # transitions
            t0 = Transition('t0',re.compile(r'^.*$'), init,header,consume=False)
            t1 = Transition('t1',re.compile(r'^!\-+DECLARATION\-+[\s\t]*$'),header,declarations,action = record, replay = output) # straightOutput
            t2 = Transition('t2',re.compile(r'^!\-+[\s\t]*TOLERANCE[\s\t]*\-+[\s\t]*$'),declarations,tolerances,action= record, replay = output)
            t3 = Transition('t3',re.compile(r'^.+aper_tol:=.+mech_sep=.+$'),tolerances,definitions,action=skip,consume=False)
            t4 = Transition('t4',re.compile(r'^(.*)SEQUENCE, BEAM 1(.*)$'),definitions,seq1,action = record, replay = startSeq1TransitionReplay) 
            t5 = Transition('t5',re.compile(r'^(.*)SEQUENCE, BEAM 2(.*)$'),seq1,seq2, action = record, replay = output)
            t6 = Transition('t6',re.compile(r'^return;.*$'),seq2, end, action = record, replay = output, consume = True )
            fsm.addStates([init,header,declarations,definitions,seq1,seq2,end])
            fsm.addTransitions([t0,t1,t2,t3,t4,t5,t6])

            # add a set of transitions to accomodate for blank lines occuring when processing each state
            # additional state to accomodate for blank lines
            blankTransitions = []
            for i,s in enumerate(fsm.states):
                tBlank = Transition('b',re.compile(r'^[\s\t]*\n?$'),s,s,action=record,replay=output,consume=True)
                fsm.addTransition(tBlank)

            # now handle arbitrary comments in the same fashion
            commentTransitions = []
            for i,s in enumerate(fsm.states):
                if not discardB1 or not s == seq1: # for processing of sequence 1, do not bother about the special transitions
                    tComment = Transition('c',re.compile(r'^!.+$'),s,s,action=record,replay=output,consume=True)
                fsm.addTransition(tComment)

            # some transitions to match well known patterns
            for s in fsm.states:
                if not discardB1 or not s == seq1: # for processing of sequence 1, do not bother about the special transitions
                    tCustom = Transition('k',re.compile(r'^(select|seqedit|remove|endedit).*$'),\
                                         s,s, action = record, replay = output, consume=True)
                fsm.addTransition(tCustom)

        elif mode == 'sequence':

            if discardB1:
                seq1Action = skip
                seq1Replay = skipReplay
                startseq1Action = skip
                startseq1Replay = skipReplay
                endseq1Action = skip
                endseq1Replay = skipReplay
                seq1CtesReplay = skipReplay
                kminkmaxAction = collectNonB1RelatedLines
                kminkmaxReplay = output
                acscaAction = collectB2MagnetConstants
            else:
                seq1Action = record
                seq1Replay = output
                startseq1Action = record
                startseq1Replay = output
                endseq1Action = record
                endseq1Replay = output
                seq1CtesReplay = output
                kminkmaxAction = record
                kminkmaxReplay = output
                acscaAction = collectMagnetConstants # actually with B1
            
            # states
            init = State('start',initial=1)
            header = State('header',action=record, replay=output)
            params = State('params',action=record, replay=output)
            classes = State('classes',action=lookForClassDeclarations, replay=output) # replay as such
            seq1 = State('seq1',action=seq1Action, replay=seq1Replay) # also avoid instantiating shared elements twice, for the first and second beam!
            endseq1 = State('endseq1',action=record, replay=output)
            seq2 = State('seq2',action=lookForInstanceInstallations, replay=outputInstanceInstallations)      
            seq1Ctes = State('seq1Ctes',action=record, replay=seq1CtesReplay) # leave magnet-constants for beam 1 untouched
            seq2Ctes = State('seq2Ctes',action=collectB2MagnetConstants, replay=outputMagnetConstants) # skip for the time-being
            kminkmax = State('kminkmax',action=kminkmaxAction, replay=kminkmaxReplay) # do not need to modify these parameters
            acsca = State('acsca',action=acscaAction,replay=outputMagnetConstants) # specific output for specific formatting
            end = State('end',action=record, replay=output) # SHOULD ADD TEST THAT IF END REACHED AND INPUT TEXT DATA LEFT SHOULD RAISE AN EXCEPTION
            
            #transitions
            t0 = Transition('t0',re.compile(r'^.*$'),init,header,consume=False) # comments will consume
            t1 = Transition('t1',re.compile(r'^/\*[\s\t]+GEOMETRY[\s\t]+\*/.*$'),header,params,action=record, replay=output, consume=True)
            t2 = Transition('t2',re.compile(r'^.+ CLASSES DEFINITION .+$'),params,classes, action=record, replay = output, consume = True)
            t3 = Transition('t3',re.compile(r'^LHCB1 : SEQUENCE.+'),classes,seq1,action=startseq1Action,replay=startseq1Replay,consume=True)
            t4 = Transition('t4',re.compile(r'^ENDSEQUENCE;$'),seq1,endseq1,action=endseq1Action,replay=endseq1Replay,consume=True)
            t5 = Transition('t5',re.compile(r'^LHCB2 : SEQUENCE.+$'),endseq1,seq2,action=record,replay=output,consume=True)
            t6 = Transition('t6',re.compile(r'^/.+ MAGNET-CONSTANT LHC SEQUENCE %B1.+$'),seq2,seq1Ctes,action=record,replay=output,consume=True)
            t7 = Transition('t7',re.compile(r'^/.+ MAGNET-CONSTANT LHC SEQUENCE %B2.+$'),seq1Ctes,seq2Ctes,action=record,replay=output,consume=True)
            t8 = Transition('t8',re.compile(r'^/\*[\s\t]+Kmax at 4.5K[\s\t]+\*/.*$'),seq2Ctes,kminkmax,action=record,replay=output,consume=True)
            t9 = Transition('t9',re.compile(r'^/\*[\s\t]+ACSCA CAVITIES[\s\t]+\*/.*$'),kminkmax,acsca,action=record,replay=output,consume=True)
            t10 = Transition('t10',re.compile(r'^return;$'),acsca,end,action=record,replay=output,consume=True)

            fsm.addStates([init,header,params,classes,seq1,endseq1,seq2,seq1Ctes,seq2Ctes,kminkmax,acsca, end]) # need endseq1 but no need for endseq2
            fsm.addTransitions([t0,t1,t2,t3,t4,t5,t6,t7,t8,t9])

            # following code could be shared
            blankTransitions = []
            for i,s in enumerate(fsm.states):
                tBlank = Transition('b',re.compile(r'^[\s\t]*\n?$'),s,s,action=record,replay=output,consume=True)
                fsm.addTransition(tBlank)

            # now handle arbitrary comments in the same fashion
            commentTransitions = []
            for i,s in enumerate(fsm.states):
                tComment = Transition('c',re.compile(r'^(/\*+/.*)|(/\*.+\*/)|(//.+)$'),s,s,action=record,replay=output,consume=True)
                fsm.addTransition(tComment)
            # V6.5.seq also contains comments starting with //
                

            # some transitions to match well known patterns
            for s in fsm.states:
                tCustom = Transition('k',re.compile(r'^(select|seqedit|remove|endedit|return|ENDSEQUENCE).+$'),\
                                     s,s, action = record, replay = output, consume=True)
                fsm.addTransition(tCustom)

            
            pass
        
            printStderr("now about to process the file line by line to create elements")

        fsm.init() # force switch to initial state
        for fileLine in sequenceFile.fileListing:
            fsm.step(fileLine)
        if not fsm.current.name == 'end':
            printStderr('ERROR - analysis of the input file failed!')
        printStderr('FSM final state: '+fsm.current.name)

        if reflectFlag:
            printStderr("now about to reflect sequence (only applies to elements of the second beam)")
            
            secondBeam.reflect()
            
            if rename_b2_b4:
                reflect = {}
                reflect['LHCB2']='LHCB4'
                reflect['LHCB4']='LHCB2'                
                secondBeam.rename(reflect[secondBeam.getName()]) # time consuming as information is propagated to all related structures

        outstream = fsm.replay() # will now go through the recorded history / trajectory FSM, invoking the replayActions instead of the actions

        if iteration==repeat and not quiet: # send output to stdout (redirected to output file, only print if this is the last iteration)
            print outstream,  # comma prevents the last \n which is otherwise automatically appended by print

    elapsedTime = time.time() - startTime    
    printStderr('elapsed time = '+ str(elapsedTime) + ' seconds')
        

if __name__ == '__main__':
    
    try: 
         main()
    except ReflectorException, e: # from Python 2.6, should end with "as e" instead
         printStderr("Reflector Exception caught :" + str(e))
        # following only available form Python 2.6, while SLC4 features a deprecated version!
        #finally:
        #    print "Unknown exception!"


