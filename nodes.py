import math
import error
class NumberNode:
    def __init__(self,token):
        '''@params Token'''
        self.token = token

    def __repr__(self):
        return f"{self.token.value}"
    
class BineryOpNode:
    def __init__(self,left,op_tok,right):
        '''@params NumberNode,Token,NumberNode'''
        self.left = left
        self.right = right
        self.op_tok = op_tok

    def __repr__(self):
        return f"({self.left} {self.op_tok} {self.right})"

class UneryOpNode:
    def __init__(self,op_tok,node):
        '''@params Token,NumberNode'''
        self.op_tok = op_tok
        self.node = node

    def __repr__(self):
        return f"({'-' if self.op_tok.type == 'MIN' else '+'}{self.node})"

class VarAccessNode:
    def __init__(self,var_name):
        self.var_name = var_name

    def get_value(self,global_var_list):
        return global_var_list[self.var_name]


class Number:
    def __init__(self,value):
        self.value = value

    def __repr__(self):
        return f"{self.value}"

    def added_to(self,other):
        if isinstance(other,Number):
            self.value = self.value + other.value
            return self,None
    
    def sustract_by(self,other):
        if isinstance(other,Number):
            self.value = self.value - other.value
            return self,None

    def multipiied_by(self,other):
        if isinstance(other,Number):
            self.value = self.value * other.value
            return self,None
    
    def devied_by(self,other):
        if isinstance(other,Number):
            if other.value != 0:
                self.value = self.value / other.value
                return self,None
            else:
                return None,error.RuntimeError('Division by zero not is definded!')
    
    def rise_to(self,other):
        if isinstance(other,Number):
            self.value = math.pow(self.value,other.value)
            return self,None
