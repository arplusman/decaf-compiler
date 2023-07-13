from pprint import pprint
import re

class Class:
    classes = []

    def __init__(self, name, parentName=None):
        self.parent = parentName
        self.children = []
        self.name = name
        self.variables = []
        self.methods = []
        Class.classes.append(self)

    @staticmethod
    def handleInheritance():
        roots = []
        for cls in Class.classes:
            par = cls.parent
            if par != None:
                parObj = Class.searchClass(par)
                cls.parent = parObj
                parObj.children.append(cls)
            else:
                roots.append(cls)
        # Loop through roots to chlldren
        for root in roots:
            root.extendsParent(None)

    def extendsParent(self , parrent):
        if parrent != None:
            self.extendVariables(parrent)
            self.extendMethods(parrent)
        for child in self.children:
            child.extendsParent(self)


    # Inherit Variables an Methods from parent
    def extendVariables(self, parent):
        tmpVars = self.variables
        self.variables = []
        for var in parent.variables:
            self.variables.append(var.copy())
        for var in tmpVars:
            if not self.variableExists(var['name']):
                self.variables.append(var.copy())

    def extendMethods(self, parent):
        tmpMethods = self.methods
        self.methods = []
        for method in parent.methods:
            self.methods.append(method.copy())
        for method in tmpMethods:
            if not self.methodExists(method['name']):
                self.methods.append(method.copy())
            else:
                self.overrideMethod(method['name'])

    # Find Offset of Variables and Methods from Start Address
    def variableOffset(self, name):
        for i in range(len(self.variables)):
            if self.variables[i]['name'] == name:
                return 4*i + 4
        raise Exception("Variable ( " + name + " ) not found !!!")

    def methodOffset(self, name):
        for i in range(len(self.methods)):
            if self.methods[i]['name'] == name:
                return 4*i
        raise Exception("Method ( " + name + " ) fot found !!!")

    # Check Where a Variable or a Method Exists or not ( Search by name )
    def variableExists(self, name):
        for var in self.variables:
            if var['name'] == name:
                return True
        return False

    def methodExists(self, name):
        for method in self.methods:
            if method['name'] == name:
                return True
        return False

    # Add Variable or Method
    def addVariable(self, name, varType):
        self.variables.append({'name': name, 'type': varType})

    def getVariable(self , name):
        for var in self.variables:
            if var['name'] == name:
                return var
        raise Exception("Variable (" + name + ") not exists in Class !!!")

    def addMethod(self, name, methodType):
        self.methods.append({'name': name, 'type': methodType, 'prefix': self.name})

    def getMethod(self , name):
        for method in self.methods:
            if method['name'] == name:
                return method
        raise Exception("Method (" + name + ") not exists in Class !!!")

    def overrideMethod(self, name):
        for method in self.methods:
            if method['name'] == name:
                method['prefix'] = self.name
                return
        raise Exception("Method ( " + name + " ) not found to override !!!")

    # Search Class By Name
    @staticmethod
    def searchClass(searchKey):
        for c in Class.classes:
            if c.name == searchKey:
                return c
        return None

    # Get Vtables of Classes
    @staticmethod
    def getVtables():
        code = ''
        for c in Class.classes:
            code += c.name + "_vtable:\n"
            for method in c.methods:
                code += "\t.word " + method['prefix'] + "_" + method['name'] + "\n"
        return code

    # Get Constructors of classes
    def getConstructors():
        code = ''
        for c in Class.classes:
            size = (len(c.variables) + 1) * 4;
            code += "# Constructor for Class : " + c.name + "\n"
            code += c.name + "_Constructor:\n"
            code += "li $a0 , " + str(size) + " # Size of Object ( including Vtable address at index 0 )\n"
            code += "li $v0 , 9\n"
            code += "syscall\n"
            code += "la $t0 , " + c.name + "_vtable # Loading Vtable Address of this Class\n"
            code += "sw $t0 , 0($v0) # Storing Vtable pointer at index 0 of object\n"
            code += "jr $ra\n\n"
        return code

    # Check whether 2 classes are convertable or not
    @staticmethod
    def areConvertable(name1 , name2):
        if name1 == "null_type" or name2 == "null_type":
            return True;
        a = Class.searchClass(name1)
        b = Class.searchClass(name2)
        if a == None or b == None:
            return False
        tmpb = b
        while tmpb.parent != None:
            if tmpb.parent.name == a.name:
                return True
            tmpb = tmpb.parent
        tmpa = a
        while tmpa.parent != None:
            if tmpa.parent.name == b.name:
                return True
            tmpa = tmpa.parent
        return False
    # Log
    @staticmethod
    def log():
        for c in Class.classes:
            print("----------------- Class name : " + c.name + " ------------------")
            print("---- Variables")
            for var in c.variables:
                print("- Name : " + var['name'] + " , Type : " + var['type'])
            print("---- Methods")
            for m in c.methods:
                print("- Name : " + m['name'] + " , Type : " + m['type'])