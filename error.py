class Error:
    def __init__(self,err_name,err_desc):
        self.err_name = err_name
        self.err_desc = err_desc
    
    def as_string(self):
        return f"{self.err_name}:\t{self.err_desc}."

class SyntaxError(Error):
    def __init__(self,err_desc):
        err_name = 'Syntax Error'
        super(SyntaxError,self).__init__(err_name,err_desc)

class RuntimeError(Error):
    def __init__(self,err_desc):
        err_name = 'Runtime Error'
        super(RuntimeError, self).__init__(err_name,err_desc)