import re
import os, sys

class FunctionDeclaration:
    def __init__(self, strLine):
        strLine = re.sub('\s\s+', ' ', strLine)
        strLine = re.sub(';\s*','', strLine).replace(' (', '(')
        result = re.search( '(.*[ *]+)([a-zA-Z0-9_]+)\((.*)\)$', strLine)
        
        if(result):
            self.ret = result.group(1)
            self.name = result.group(2)

            self.args = result.group(3).split(',')
        else:
            print('error on line:', strLine)

        # print(self.args)

def removePrefix(string):
    return re.sub('[A-Z]+_','', string)

def convertPointers(string):
    string = re.sub(r'void\s?\*', r'std::string& ', string) # void * --> std::string &
    string = re.sub(r'(\w+)\s?\*', r'\1& ', string) # int * --> int & 
    return string

class MockGenerator:
    def __init__(self, className):
        self.className = className


    def generate(self, function, tab='    '):
        f = function

        mock = f.ret + ' ' + f.name + '('
        for arg in f.args:
            if(not arg in ['void ', 'void']):
                mock += arg + ','
        
        mock += ')\n{\n'

        # POS_Func -> Func
        name = removePrefix( f.name)
        
        mock += tab
        if(not f.ret in ['void ', 'void']):
            mock += 'return '

        mock += self.className + 'Obj' + '->' + name + '('

        for arg in f.args:
            arg = re.sub('\s+$','' , arg) # remove space in the last possition
            # arg = arg.replace('*', '')
            if(not arg in ['void ', 'void']):
                mock += arg.split(' ')[-1] + ','
        mock += ');\n}\n\n'

        mock = mock.replace(',)', ')')
        return mock

class ClassGenerator:
    def __init__(self, className,  tab='    '):
        self.className = className
        self.header = f'class {className} {{\n'
        self.header += f'protected:\n'
        self.header += f'{tab}{className}({className}*);\n'
        self.header += f'public:\n'

        self.contructor =  f'{className}::{className}({className}* obj)\n'
        self.contructor += f'{{\n{tab}{self.className}Obj = obj;\n}}\n\n'

        self.headerName = f'#include \"{className}.h\"\n\n'
        
    def generateCpp(self, function, tab='    '):
        f = function

        f.ret = re.sub('\s.*EXPORT.*?\s', ' ', f.ret, flags=re.IGNORECASE)
        # POS_Func -> Func
        name = removePrefix( f.name)

        mock = f'{f.ret} {self.className}::{name}('
        for arg in f.args:
            mock += f'{convertPointers(arg)} ,'
        
        mock += ')\n{\n'

        mock += f'{tab} return'
        if(not f.ret in ['void ', 'void']):
            mock += ' 0'
        
        mock += ';\n}\n\n'

        mock = mock.replace(',)', ')')
        return mock

    def generateHeader(self, function, tab='    '):
        f = function
        f.ret = re.sub('\s.*EXPORT.*?\s', ' ', f.ret, flags=re.IGNORECASE)
        # POS_Func -> Func
        name = removePrefix( f.name)

        mock = f'virtual {f.ret} {name} ('
        for arg in f.args:
            mock += f'{convertPointers(arg)} ,'
        
        mock += ');\n'

        mock = mock.replace(',)', ')')
        return mock
    


if len(sys.argv) < 2:
    print(f'Usage:\n\t{sys.argv[0]} <inputHeaderFile> <outClassName>\n') 
    print(f'Example:\n\t{sys.argv[0]} <posplug.txt> <Posplug>\n') 
    os._exit(1)

print("opening", sys.argv[1])
fd=[]
className = sys.argv[2]

with open(sys.argv[1], 'r') as file: 
    for _,line in enumerate(file):
        fd.append( FunctionDeclaration(line))

mockGen = MockGenerator(className)
classGen = ClassGenerator(className)
with open(sys.argv[2] + '.cpp', 'w') as file: 
    file.write(classGen.headerName)
    for func in fd:
        file.write(mockGen.generate(func))

    file.write('//------------------------------------------------------------------------\n')
    file.write('//       Class method implementation                                      \n')
    file.write('//------------------------------------------------------------------------\n\n')
    file.write(classGen.contructor)
    for func in fd:
        file.write(classGen.generateCpp(func))

with open(sys.argv[2] + '.h', 'w') as file: 
    file.write(classGen.header)
    for func in fd:
        file.write(classGen.generateHeader(func))
