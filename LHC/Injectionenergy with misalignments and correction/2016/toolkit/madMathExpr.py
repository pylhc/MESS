#!/usr/bin/python

# the tree is very specific to our purpose

import re

import traceback # for debugging purpose

def getTabStr(tab):
    tabStr = ""
    for i in range(0,tab):
        tabStr = tabStr + " "
    return tabStr

def removeBlanks(s):
    sNew = ""
    for c in s:
        if c != " ":
            sNew = sNew + c
    return sNew

class MathException(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MathExpr:

    def tryMatch(str,lvl=0): # returns an expression if top-down parsing succeeds, otherwise exception

        if lvl==0:
            str = removeBlanks(str)
        
        try:
            parsedExpression = ParenthesisExpr.tryMatch(str,lvl)
        except MathException:
            try:
                #print "trying to match binary expression for str="+str
                parsedExpression = BinaryExpr.tryMatch(str,lvl)
                #print "returned?"
            except MathException:
                #print "what about here?"
                try:
                    # unary expressions not used for time-being, instead relying on signs for leaf expressions
                    parsedExpression = UnaryExpr.tryMatch(str,lvl)
                except MathException:
                    try:
                        parsedExpression = LeafExpr.tryMatch(str,lvl)
                        #print "leafExpression to be returned"
                    except MathException:
                        #print "do we end-up here in the end?"
                        msg = "failed to match expression '"+str+"'"
                        raise MathException(msg)
        return parsedExpression
    tryMatch = staticmethod(tryMatch)
    
    def __init__(self):
        pass

    def simplify(self):
        raise MathException(\
            "expression simplification not implemented by base class")

    def negate(self): # change signs of the top-level terms (not propagated)
        pass

    def getXml(self,tab=0):
        return "should be implemented by concrete class"

class ParenthesisExpr(MathExpr):

    def tryMatch(str,lvl=0):
        expr = ParenthesisExpr()
        if expr.match(str,lvl):
            #print "now to return parenthesisExpression"
            return expr
        else:
            #print "failed to match parenthesized expression"
            raise MathException(\
                "failed to match parenthesized expression")
        
    tryMatch = staticmethod(tryMatch)
    
    def __init__(self):
        MathExpr.__init__(self)

    def match(self,str,lvl=0):
        #print "ParenthesisExpr:match"
        patternStr = r'^\((.+)\)$'
        match = re.match(patternStr,str)
        if match:
            subString = match.group(1)
            #print "Parenthesis match attempt for'"+subString+"'"
            try:
                self.subExpr = MathExpr.tryMatch(subString,lvl+1)
                #print "SUCCESS"
                return True
            except MathException:
                #print "ECHEC"
                return False
        else:
            #print "NO MATCH"
            return False

    def getStr(self):
        str = "("+self.subExpr.getStr()+")"
        return str

    def getXml(self,tab=0):
        tabStr = getTabStr(tab)
        xml = tabStr + "<par>\n"
        xml = xml + self.subExpr.getXml(tab+3)
        xml = xml + tabStr + "</par>\n"
        return xml

    def negate(self):
        # do nothing inside parenthesis
        pass

    def simplify(self):
        oldExpr = self.getStr()
        self = self.subExpr.simplify() # class change?
        if isinstance(self, LeafExpr):
            pass
            # print oldExpr + " has become leaf: " + self.getStr()
        return self # which has changed class
        

# following not used for time-being, as leaf expression handles signs
class UnaryExpr(MathExpr): # for time-being, no functions, only signs

    def tryMatch(str,lvl=0):
        raise MathException(\
            "unary expression not used") # rely on signs for leafs instead
            
        expr = UnaryExpression()
        if expr.match(str):
            return expr
        else:
            raise MathException(\
                "failed to match unary expression")
        
    tryMatch = staticmethod(tryMatch)
    
    def __init__(self,str):
        MathExpr.__init__(str)
        
    def match(self,str,lvl=0):
        patternStr = '^([\-\+])(.+)$'
        match = re.match(pattern,lvl)
        if match:
            self.operator = match.group(1)
            subString = match.group(2)
            try:
                self.subExpr = MathExpr.tryMatch(subString,lvl+1)
                return True
            except MathException:
                return False
        else:
            return False

    def getStr(self):
        return self.sign + self.subExpr.getStr()

    def getXml(self,tab=0):
        tabStr = getTabStr(tab)
        xml = tabStr + "<unary>"
        xml = xml + self.subExpr.getXml(tab+3)
        xml = xml + "</unary>"
        return xml

    def negate(self):
        if self.sign == '+':
            self.sign = '-'
        else:
            self.sign = '+'

    def simplify(self):
        raise MathException(\
            "do not yet know how to simplify a unary expression")

class BinaryExpr(MathExpr):

    def __init__(self):
        #MathExpr.__init__(self)
        pass
    
    def tryMatch(str,lvl=0):

        expr = BinaryExpr()

        if expr.match(str,lvl):
            #print "binary expression to be returned"
            return expr
        else:
            #print "hopefully pass here"
            raise MathException("failed to match binary expression")
        
    tryMatch = staticmethod(tryMatch)

    def match(self,strg,lvl=0):
        if lvl == 0:
            self.topLevelNode = True # useful for negation
        else:
            self.topLevelNode = False
        
        #print "BinaryExpr:match"
        # try to split strg in two parts at every possible operator, until one valid match is found
        patternStr = r'([\+\-\*/])' # capturing parenthesis => split will also return the operator
        #print patternStr
        parts = re.split(patternStr,strg)

        # now try to assemble parts at each operator
        operators = []
        stuff = []
        stuffPartsBeforeOperator = []
        stuffPartsCount = 0

        for part in parts:
            match = re.match(patternStr,part)
            if match:
                # this is an operator
                operators.append(part)
                stuffPartsBeforeOperator.append(stuffPartsCount)
            else:
                # this lies between operators
                stuff.append(part)
                stuffPartsCount = stuffPartsCount+1

            #print "PART="+part

        # if no feasible to split, then return False
        if (len(operators)==0) or (stuffPartsCount<2) or (len(parts)<2):
         #   print "about to exit"
         #   print "one last word"
            return False
        #print "so far so good"

        #print "OPERATORS="
        #for operator in operators:
        #    print operator
        #print "STUFF="
        #for entry in stuff:
        #    print entry

        # try to cut the expression in two, at every possible operator

        for i in range(0,len(operators)):
            leftPart = []
            rightPart = []
            for j in range(0,stuffPartsBeforeOperator[i]):
                # operators missing
                leftPart.append(stuff[j])
                if j < (stuffPartsBeforeOperator[i]-1):
                    leftPart.append(operators[j])
            for k in range(stuffPartsBeforeOperator[i],len(stuff)):
                # operators missing
                rightPart.append(stuff[k])
                if k< len(operators):
                    rightPart.append(operators[k])

            # right and left hand side expression strings
            rhs = ""
            lhs = ""
            for c in rightPart:
                rhs = rhs + c
            for c in leftPart:
                lhs = lhs +c
            
            
          #  print repr(i)+"/"+repr(len(operators))
            #print str(i) #+"/"+str(len(operators))+":"
            #print "now ready to evaluate '"+lhs+"'"+operators[i]+"'"+rhs+"'"

            try:
                self.leftOperand = MathExpr.tryMatch(lhs,lvl+1)
                self.operator = operators[i]
                #print "EO"
                self.rightOperand = MathExpr.tryMatch(rhs,lvl+1)
                #print "Binary match success!"

                return True
            except MathException:
                # should continue...
                pass

        return False # default???

    def getStr(self):
        str = self.leftOperand.getStr()+self.operator+self.rightOperand.getStr()
        return str

    def getXml(self,tab=0):
        tabStr = getTabStr(tab)
        xml = tabStr + "<binary>\n"
        xml = xml + tabStr + "<left>\n"\
              +self.leftOperand.getXml(tab+3)\
              + tabStr + "</left>\n"
        xml = xml + tabStr + "<operator>"\
              +self.operator+"</operator>\n"
        xml = xml + tabStr + "<right>\n"\
              +self.rightOperand.getXml(tab+3)\
              + tabStr + "</right>\n"
        xml = xml + tabStr + "</binary>\n"
        return xml
    
    def negate(self):
        # change the operator
        if self.operator == '+':
            self.operator = '-'
        elif self.operator == '-':
            self.operator = '+'
        # and change sign of the first term
        #self.leftOperand.negate()
        
        # now propagate sign change to the righ, knowing it won't go
        # through parenthesis (only if this is not the last term!!!)
        if not isinstance(self.rightOperand,LeafExpr): # if not a "leaf" node (introspection)
            self.rightOperand.negate()

        if self.topLevelNode == True:
            self.leftOperand.negate()

    def simplify(self):

        #print "A"
        simplifiedLeft = self.leftOperand.simplify()
        simplifiedRight = self.rightOperand.simplify()
        #print "B"

        if (isinstance(simplifiedLeft,MathExpr)):
            pass
            #print "valid left expression: " + simplifiedLeft.getStr()
        else:
            pass
            #print "invalid left expression: " + simplifiedLeft.getStr()
        if (isinstance(simplifiedRight,MathExpr)):
            pass
            #print "valid right expression: " + simplifiedRight.getStr()
        else:
            pass
            #print "invalid right expression: " + simplifiedRight.getStr()           

        if simplifiedLeft.getStr()=='0' and self.operator == '+':
            #print "C1"
            return simplifiedRight
        elif simplifiedLeft.getStr() == '0' and self.operator == '-':
            #  oppositeRight = 0
            #print "C2"
            raise MathException("did not implement the opposite of RHS yet")
        
        elif simplifiedRight.getStr()=='0' and (self.operator == '+' or self.operator == '-'):
            #print "C3 - should now return " + simplifiedLeft.getStr()
            return simplifiedLeft

        if self.operator == '-':

            # print "simplify - operation :" + \
            # simplifiedLeft.getStr() + "-" + simplifiedRight.getStr()

            if simplifiedLeft.getStr()==simplifiedRight.getStr():
                #print "proceed"
                leaf = LeafExpr.tryMatch('0')
                return leaf
            else:
                # leave the expression as it is
                # (at this stage, do not attempt to perform computations numerically)
                return self
        else:
            # failed to simplify
            print "FAILED TO SIMPLIFY "+ simplifiedLeft + self.operator + simplifiedRight
            return self # return the node, as originally
            
            
    
class LeafExpr(MathExpr):
    def __init__(self):
        MathExpr.__init__(self)
        self.sign = "" # no sign by default
    def tryMatch(str,lvl=0):
        expr = LeafExpr()
        if expr.match(str,lvl):
            #print "LeafExpr to return expr"
            return expr
        else:
            raise MathException("failed to match leaf expression")
        
    tryMatch = staticmethod(tryMatch)

    def match(self,str,lvl=0):
        patternStr = r'^([\+\-]?)([_\w\d\.]+)$'
        match = re.match(patternStr,str)
        if match:
            self.sign = match.group(1)
            self.value = match.group(2)
            #print "found leaf expression '"+self.value+"'"
            return True
        else:
            return False
        
    def getStr(self):
        if self.value == '0':
            return '0' # added space to match beam_four.seq
        else:
            return self.sign + self.value

    def getXml(self,tab):
        tabStr = getTabStr(tab)
        xml = tabStr + "<leaf>" + self.sign + self.value + "</leaf>\n"
        return xml

    def negate(self):
        if self.sign == '-':
            self.sign = '+'
        elif (self.sign == " ") or (self.sign == "") or (self.sign=="+"):
            self.sign = '-'

    def simplify(self):
        return self # assume already in simplistic form
    
if __name__ == "__main__": # self-test code


    str = '-x.D+y-z+12345.678*(b*(c+d))-(e+f-g)'
    #str = 'pIP1.L1+IP1OFS.B2*DS'
    
    mathExpr = MathExpr.tryMatch(str)
    originalExpr = mathExpr.getStr()
    print "original expression :" + originalExpr

    xml = mathExpr.getXml()
    xmlBefore = open ("before.xml","w")
    xmlBefore.write(xml)
    xmlBefore.close()

    mathExpr.negate()
    negatedExpr = mathExpr.getStr()
    print "negated expression  :" + negatedExpr

    xml = mathExpr.getXml()
    xmlAfter = open("after.xml","w")
    xmlAfter.write(xml)
    xmlAfter.close()

    assert negatedExpr == '+x.D-y+z-12345.678*(b*(c+d))+(e+f-g)',\
           "taking the opposite sign does not work"        

    string2 = '0.5-(0.5-(0.5))'
    mathExpr = MathExpr.tryMatch(string2)
    originalExpr = mathExpr.getStr()
    print "original expresion : " + originalExpr
    mathExpr = mathExpr.simplify() # syntax to simplify an expression
    simplifiedExpr = mathExpr.getStr()
    print "simplified expression :" + simplifiedExpr

    assert simplifiedExpr == '0.5',\
           "simplification does not work"

    string3 = "+KCO.A12B2*L.MCO"
    mathExpr = MathExpr.tryMatch(string3)
    originalExpr = mathExpr.getStr()
    print "original expression :" + originalExpr
    xml =mathExpr.getXml()
    print xml
    mathExpr.negate()
    negatedExpr = mathExpr.getStr()
    print "negated expression :" + negatedExpr

    assert negatedExpr == "-KCO.A12B2*L.MCO",\
           "negation of string 3 fails"
