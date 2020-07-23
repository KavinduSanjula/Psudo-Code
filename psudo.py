from token import *
import error
import nodes
import string

DIGITS = '.0123456789'
LETTERS = string.ascii_letters
OPREROTS = {'+':'PLS','-':'MIN','*':'MUL','/':'DIV','^':'POW','(':'LPR',')':'RPR','=':'EQ'}
LETTERS_DIGITS = LETTERS + DIGITS[1:]

KEWORDS = ['var']

global_vars = {}

class Lexer:
    def __init__(self,line):
        self.__line = line
        self.__idx = -1
        self.__currunt_cha = None

    def advance(self):
        self.__idx += 1
        self.__currunt_cha = None
        if self.__idx < len(self.__line):
            self.__currunt_cha = self.__line[self.__idx]
        return self.__currunt_cha

    def make_keyword(self):
        word = ''
        while self.__currunt_cha and self.__currunt_cha in LETTERS_DIGITS + '_':
            word += self.__currunt_cha
            self.advance()
        
        self.__idx -= 1

        if word in KEWORDS:
            return Token('KWD',word)
        else:
            return Token('IDF',word)

    def make_number(self):
        dots = 0
        number = ''
        c = self.__currunt_cha
        while c and c in DIGITS:
            number += c
            if c == '.':dots += 1 
            if dots > 1: return None,None,error.SyntaxError('Unexpected "." found')
            c = self.advance()
        self.__idx -= 1
        if dots > 0:
            return float(number),None
        else:
            return int(number),None

    def make_tokens(self):
        tokens = []
        c = self.advance()
        while c: 
            if c == ' ':
                c = self.advance()
                continue
            elif c in OPREROTS:
                tokens.append(Token(OPREROTS[c]))
            elif c in LETTERS:
                token = self.make_keyword()
                tokens.append(token)
            elif c in DIGITS:
                number,err = self.make_number()
                if not err:
                    if isinstance(number,int): tokens.append(Token('INT',number))
                    elif isinstance(number,float): tokens.append(Token('INT',number))
                else:
                    return None,err
            else:
                return None,error.SyntaxError(f'Invalid Charactor "{c}"')
            c = self.advance()
        return tokens,None

class Parser:
    def __init__(self,tokens):
        self.tokens = tokens
        self.i = 0
        self.current_token = self.tokens[self.i]

    def advance(self):
        self.i += 1
        self.current_token = None
        if self.i < len(self.tokens):
            self.current_token = self.tokens[self.i]
        return self.current_token

    def parse(self):
        '''Genarate abstract syntax tree @returns BineryOpNode'''
        res, err = self.exper()
        return res,err


    def factor(self):
        '''factor (single number) - @returns NumberNode'''
        global global_vars
        token = self.current_token

        if self.current_token:
            if token.type in ('PLS','MIN'):
                self.advance()
                if self.current_token:
                    value,err = self.factor()
                    if not err:
                        return nodes.UneryOpNode(token,value),None
                    else:
                        return None,err
                else: return None,error.SyntaxError(f'No tokens after {token.type}') 

            elif token.type == 'LPR':
                self.advance()
                res,err = self.exper()
                if err: return None,err
                if self.current_token.type == 'RPR': 
                    self.advance()   
                    return res,None
                else:
                    return None,error.SyntaxError(f'Expect ")" but {self.current_tok} found')

            elif token.type in ('INT','FLOAT'):
                self.advance()
                return nodes.NumberNode(token),None
            elif token.type == 'IDF':
                var_name = token.value
                self.advance()
                if self.current_token and self.current_token.type == 'EQ':
                    self.advance()
                    value,err = self.exper()
                    global_vars[var_name] = Variable(var_name,value)
                    return None,err
                return nodes.VarAccessNode(token.value),None
            elif token.type == 'KWD':
                if token.value == 'var':
                    token = self.advance()

                    if token.type == 'IDF':
                        var_name = token.value
                        token = self.advance()

                        if token.type == 'EQ':
                            self.advance()
                            value,err = self.exper()
                            global_vars[var_name] = Variable(var_name,value)
                            return None,err
                        else:
                            return None,error.SyntaxError('Expected "=" after identifire.')
                    else:
                        return None,error.SyntaxError('Expected an identifire after var keyword.')
                else:
                    return error.Error('<Error>','NOT DEFINDED')
            else:
                return None,error.SyntaxError(f'Expect INT ot FLOAT or VAR but nothing found')
        else:
            return None, error.SyntaxError(f"There are no tokens found after {self.tokens[-1]}")
    
    def term(self):
        '''term (multiply and devide) - @returns BineryOpNode'''
        res, err = self.binery_op(self.factor,('MUL','DIV','POW'))
        return res,err
        

    def exper(self):
        '''exper (plus and minus) - @returns BineryOpNode'''
        res, err = self.binery_op(self.term,('PLS','MIN'))
        return res,err

    def binery_op(self,func,ops):
        left,err = func()
        opr = self.current_token
        while opr and opr.type in ops:
            self.advance()
            right,err = func()
            if not err:
                left = nodes.BineryOpNode(left,opr,right)
            else:
                return None,err
            
            opr = self.current_token
        return left,err

class Variable:
    def __init__(self,name,value):

        self.name = name
        self.value = value

    def __repr__(self):
        return f"{self.value}"

class Interpreter:
    def visit(self,node):
        if isinstance(node,nodes.NumberNode):
            return self.visit_NumberNode(node)
        elif isinstance(node,nodes.BineryOpNode):
            return self.visit_BineryOpNode(node)
        elif isinstance(node,nodes.UneryOpNode):
            return self.visit_UneryOpNode(node)
        elif isinstance(node,nodes.VarAccessNode):
            return self.visit_VarAccessNode(node)

    def visit_NumberNode(self,node):
        return nodes.Number(node.token.value),None

    def visit_BineryOpNode(self,node):
        left,err = self.visit(node.left)
        right,err = self.visit(node.right)
        
        if node.op_tok.type == 'PLS':
            val,err = left.added_to(right)
            return val,err
        elif node.op_tok.type == 'MIN':
            val,err = left.substract_by(right)
            return val,err
        elif node.op_tok.type == 'MUL':
            val,err = left.multipiied_by(right)
            return val,err
        elif node.op_tok.type == 'DIV':
            val,err = left.devied_by(right)
            return val,err
        elif node.op_tok.type == 'POW':
            val,err = left.rise_to(right)
            return val,err

    def visit_UneryOpNode(self,node):
        number,err = self.visit(node.node)
        if node.op_tok.type == 'MIN':
            number = number.multipiied_by(nodes.Number(-1))
        return number,err
    
    def visit_VarAccessNode(self,variable):
        node = variable.get_value(global_vars)
        number,err = self.visit(node.value)
        return number,err


while True:
    inpt = input('> ')
    if inpt == 'exit': break

    lexer = Lexer(inpt)
    tokens,err = lexer.make_tokens()
    #print('#',tokens)
    if err:
        print(err.as_string())
        continue
    parser= Parser(tokens)

    ast, err = parser.parse()
    if not ast:
        continue
    #print('#',ast)
    if err: print(err.as_string());continue
    interpreter = Interpreter()
    result,err = interpreter.visit(ast)
    if err:
        print(err.as_string())
        continue
    print(result)

exit()