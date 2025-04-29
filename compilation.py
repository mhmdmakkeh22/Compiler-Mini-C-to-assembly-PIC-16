# %% [markdown]
# ## **Mini-C to PIC16 Compiler in a Jupyter Notebook**
# 
# This notebook demonstrates:
# 
# 1. A **Lexer** for a subset of C-like syntax (with tokens for `int`, `if`, `while`, etc.).  
# 2. An **AST** (Abstract Syntax Tree) definition (classes).  
# 3. A **Parser** (recursive descent) that produces the AST.  
# 4. A **CodeGenVisitor** that outputs simplified PIC16-like assembly instructions.
# 
# We’ll compile a small code snippet at the end.
# 

# %%
import re
import argparse
import sys
import unittest

# %%
# 1) Lexer definitions
token_specification = [
    (r"\s+",              None),
    (r"//.*",             None),
    (r"/\*[\s\S]*?\*/",   None),
    (r"\bint\b",          'KW_INT'),
    (r"\bfloat\b",        'KW_FLOAT'),
    (r"\bbool\b",         'KW_BOOL'),
    (r"\bchar\b",         'KW_CHAR'),
    (r"\bif\b",           'KW_IF'),
    (r"\belse\b",         'KW_ELSE'),
    (r"\bwhile\b",        'KW_WHILE'),
    (r"\bmain\b",         'KW_MAIN'),
    (r"\d+",              'INT_LITERAL'),
    (r"[A-Za-z_]\w*",     'IDENT'),
    (r"\(",               'LPAREN'),
    (r"\)",               'RPAREN'),
    (r"\{",               'LBRACE'),
    (r"\}",               'RBRACE'),
    (r"\[",               'LBRACKET'),
    (r"\]",               'RBRACKET'),
    (r";",                'SEMICOLON'),
    (r",",                'COMMA'),
    (r"\|\|",             'OR'),
    (r"&&",               'AND'),
    (r"==",               'EQ'),
    (r"!=",               'NEQ'),
    (r"<=",               'LTE'),
    (r">=",               'GTE'),
    (r"<",                'LT'),
    (r">",                'GT'),
    (r"=",                'ASSIGN'),
    (r"\+",               'PLUS'),
    (r"-",                'MINUS'),
    (r"\*",               'MULT'),
    (r"/",                'DIV'),
    (r"!",                'NOT'),
]

class Token:
    def __init__(self, type_, value, line, col):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col
    def __repr__(self):
        return f"Token({self.type}, {self.value}, line={self.line}, col={self.col})"

class MiniCLexer:
    def __init__(self, code):
        self.code = code
        parts = []
        for idx, (pattern, name) in enumerate(token_specification):
            group = name or f"SKIP_{idx}"
            parts.append(f"(?P<{group}>{pattern})")
        self.big_regex = re.compile('|'.join(parts))

    def tokenize(self):
        tokens = []
        line, col = 1, 1
        for match in self.big_regex.finditer(self.code):
            kind = match.lastgroup
            text = match.group()
            # Skip whitespace/comments
            if kind and kind.startswith('SKIP'):
                for ch in text:
                    if ch == '\n': line += 1; col = 1
                    else: col += 1
                continue
            tokens.append(Token(kind, text, line, col))
            for ch in text:
                if ch == '\n': line += 1; col = 1
                else: col += 1
        return tokens


# %%
# 2) AST Node Classes
class ASTNode:
    def accept(self, visitor):
        raise NotImplementedError

class Program(ASTNode):
    def __init__(self, declarations, statements):
        self.declarations = declarations
        self.statements = statements
    def accept(self, visitor): return visitor.visitProgram(self)
    def __repr__(self): return f"Program(decls={self.declarations}, stmts={self.statements})"

class Block(ASTNode):
    def __init__(self, declarations, statements):
        self.declarations = declarations
        self.statements = statements
    def accept(self, visitor): return visitor.visitBlock(self)
    def __repr__(self): return f"Block(decls={self.declarations}, stmts={self.statements})"

class Declaration(ASTNode):
    def __init__(self, var_type, name, array_size=None):
        self.var_type = var_type
        self.name = name
        self.array_size = array_size
    def accept(self, visitor): return visitor.visitDeclaration(self)
    def __repr__(self): return f"Declaration({self.var_type}, {self.name}, array={self.array_size})"

class Statement(ASTNode): pass

class AssignmentStatement(Statement):
    def __init__(self, name, index_expr, rhs):
        self.name = name; self.index_expr = index_expr; self.rhs = rhs
    def accept(self, visitor): return visitor.visitAssignment(self)
    def __repr__(self): return f"Assign({self.name}, idx={self.index_expr}, rhs={self.rhs})"

class IfStatement(Statement):
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition; self.then_block = then_block; self.else_block = else_block
    def accept(self, visitor): return visitor.visitIf(self)
    def __repr__(self): return f"If({self.condition}, then={self.then_block}, else={self.else_block})"

class WhileStatement(Statement):
    def __init__(self, condition, body):
        self.condition = condition; self.body = body
    def accept(self, visitor): return visitor.visitWhile(self)
    def __repr__(self): return f"While({self.condition}, body={self.body})"

class Expression(ASTNode): pass

class BinaryOp(Expression):
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
    def accept(self, visitor): return visitor.visitBinaryOp(self)
    def __repr__(self): return f"BinaryOp({self.op}, {self.left}, {self.right})"

class UnaryOp(Expression):
    def __init__(self, op, expr): self.op = op; self.expr = expr
    def accept(self, visitor): return visitor.visitUnaryOp(self)
    def __repr__(self): return f"UnaryOp({self.op}, {self.expr})"

class Literal(Expression):
    def __init__(self, value): self.value = value
    def accept(self, visitor): return visitor.visitLiteral(self)
    def __repr__(self): return f"Literal({self.value})"

class Identifier(Expression):
    def __init__(self, name, index_expr=None): self.name = name; self.index_expr = index_expr
    def accept(self, visitor): return visitor.visitIdentifier(self)
    def __repr__(self): return f"Identifier({self.name}, idx={self.index_expr})"

class Parenthesized(Expression):
    def __init__(self, expr): self.expr = expr
    def accept(self, visitor): return visitor.visitParenthesized(self)
    def __repr__(self): return f"Paren({self.expr})"

# %%
# === Modified Parser implementation ===
class ParsingException(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def peek(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def peek_type(self):
        tk = self.peek()
        return tk.type if tk else None

    def accept(self, expected=None):
        tk = self.peek()
        if not tk:
            raise ParsingException(f"Unexpected end, wanted {expected}")
        if expected and tk.type != expected:
            raise ParsingException(f"Expected {expected}, got {tk.type}")
        self.index += 1
        return tk

    def expect(self, t):
        return self.accept(t)

    def finished(self):
        return self.index >= len(self.tokens)

    def error(self, msg):
        tk = self.peek()
        if tk:
            raise ParsingException(
                f"Syntax error at line {tk.line}, col {tk.col}: {msg}, "
                f"found {tk.type} -> '{tk.value}'"
            )
        else:
            raise ParsingException(f"Syntax error at end of input: {msg}")

    # Top-level entry point
    def parse(self):
        program = self.parse_program()
        if not self.finished():
            self.error("Extra tokens after parsing complete.")
        return program

    # Modified program parsing to handle both main() and standalone code
    # program → (int main() { declaration* statement* }) | (declaration* statement*)
    def parse_program(self):
        # Check if the program starts with the main function
        if (self.peek_type() == 'KW_INT' and 
            len(self.tokens) > self.index + 1 and 
            self.tokens[self.index + 1].type == 'KW_MAIN'):
            # Parse as traditional main function
            self.expect('KW_INT')
            self.expect('KW_MAIN')
            self.expect('LPAREN')
            self.expect('RPAREN')
            self.expect('LBRACE')

            decls = []
            while self.peek_type() in ('KW_INT','KW_FLOAT','KW_BOOL','KW_CHAR'):
                decls.append(self.parse_declaration())

            stmts = []
            while self.peek_type() not in (None,'RBRACE'):
                stmts.append(self.parse_statement())

            self.expect('RBRACE')
        else:
            # Parse as standalone code without main function
            decls = []
            while self.peek_type() in ('KW_INT','KW_FLOAT','KW_BOOL','KW_CHAR'):
                decls.append(self.parse_declaration())

            stmts = []
            while self.peek_type() not in (None,):
                stmts.append(self.parse_statement())

        return Program(decls, stmts)

    def parse_declaration(self):
        var_type = self.parse_type()
        name = self.accept('IDENT').value

        array_size = None
        if self.peek_type() == 'LBRACKET':
            self.accept('LBRACKET')
            array_size = int(self.accept('INT_LITERAL').value)
            self.expect('RBRACKET')

        self.expect('SEMICOLON')
        return Declaration(var_type, name, array_size)

    def parse_type(self):
        t = self.peek_type()
        if t not in ('KW_INT','KW_FLOAT','KW_BOOL','KW_CHAR'):
            self.error(f"Expected type, got {t}")
        # consume the keyword and map to a string
        mapping = {
            'KW_INT':'int', 'KW_FLOAT':'float',
            'KW_BOOL':'bool','KW_CHAR':'char'
        }
        return mapping[self.accept(t).type]

    def parse_statement(self):
        pt = self.peek_type()
        if   pt == 'IDENT':
            return self.parse_assignment()
        elif pt == 'KW_IF':
            return self.parse_if()
        elif pt == 'KW_WHILE':
            return self.parse_while()
        elif pt == 'LBRACE':
            return self.parse_block()
        else:
            self.error(f"Expected statement, got {pt}")

    def parse_assignment(self):
        name = self.accept('IDENT').value

        idx = None
        if self.peek_type() == 'LBRACKET':
            self.accept('LBRACKET')
            idx = self.parse_expression()
            self.expect('RBRACKET')

        self.expect('ASSIGN')
        expr = self.parse_expression()
        self.expect('SEMICOLON')
        return AssignmentStatement(name, idx, expr)

    def parse_if(self):
        self.accept('KW_IF'); self.accept('LPAREN')
        cond = self.parse_expression()
        self.expect('RPAREN')
        then_blk = self.parse_block()

        else_blk = None
        if self.peek_type() == 'KW_ELSE':
            self.accept('KW_ELSE')
            else_blk = self.parse_block()

        return IfStatement(cond, then_blk, else_blk)

    def parse_while(self):
        self.accept('KW_WHILE'); self.accept('LPAREN')
        cond = self.parse_expression()
        self.expect('RPAREN')
        body = self.parse_block()
        return WhileStatement(cond, body)

    def parse_block(self):
        self.accept('LBRACE')
        decls = []
        while self.peek_type() in ('KW_INT','KW_FLOAT','KW_BOOL','KW_CHAR'):
            decls.append(self.parse_declaration())
        stmts = []
        while self.peek_type() not in (None,'RBRACE'):
            stmts.append(self.parse_statement())
        self.expect('RBRACE')
        return Block(decls, stmts)

    # Expression grammar with correct precedence
    def parse_expression(self):
        return self.parse_or()
    def parse_or(self):
        left = self.parse_and()
        while self.peek_type() == 'OR':
            op    = self.accept().value
            right = self.parse_and()
            left  = BinaryOp(op, left, right)
        return left
    def parse_and(self):
        left = self.parse_equality()
        while self.peek_type() == 'AND':
            op    = self.accept().value
            right = self.parse_equality()
            left  = BinaryOp(op, left, right)
        return left
    def parse_equality(self):
        left = self.parse_relational()
        while self.peek_type() in ('EQ','NEQ'):
            op    = self.accept().value
            right = self.parse_relational()
            left  = BinaryOp(op, left, right)
        return left
    def parse_relational(self):
        left = self.parse_additive()
        while self.peek_type() in ('LT','GT','LTE','GTE'):
            op    = self.accept().value
            right = self.parse_additive()
            left  = BinaryOp(op, left, right)
        return left
    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.peek_type() in ('PLUS','MINUS'):
            op    = self.accept().value
            right = self.parse_multiplicative()
            left  = BinaryOp(op, left, right)
        return left
    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.peek_type() in ('MULT','DIV'):
            op    = self.accept().value
            right = self.parse_unary()
            left  = BinaryOp(op, left, right)
        return left
    def parse_unary(self):
        if self.peek_type() in ('MINUS','NOT'):
            op   = self.accept().value
            expr = self.parse_unary()
            return UnaryOp(op, expr)
        return self.parse_primary()
    def parse_primary(self):
        pt = self.peek_type()
        if pt == 'IDENT':
            tok = self.accept('IDENT')
            idx = None
            if self.peek_type() == 'LBRACKET':
                self.accept('LBRACKET')
                idx = self.parse_expression()
                self.expect('RBRACKET')
            return Identifier(tok.value, idx)
        elif pt == 'INT_LITERAL':
            tok = self.accept('INT_LITERAL')
            return Literal(int(tok.value))
        elif pt == 'LPAREN':
            self.accept('LPAREN')
            expr = self.parse_expression()
            self.expect('RPAREN')
            return Parenthesized(expr)
        else:
            self.error(f"Unexpected primary {pt}")

# %%
# 4) Code generator
class Visitor: pass
class CodeGenVisitor(Visitor):
    def __init__(self):
        self.code = []
        self.var_map = {}
        self.next_addr = 0x20
        self.label_counter = 0
    def emit(self, line): self.code.append(line)
    def make_label(self,prefix="lbl"): lbl=f"{prefix}{self.label_counter}"; self.label_counter+=1; return lbl
    def get_code(self): return "\n".join(self.code)
    def alloc_var(self,name):
        if name not in self.var_map:
            addr = self.next_addr; self.var_map[name] = f"0x{addr:02X}"; self.next_addr+=1
        return self.var_map[name]
    def visitProgram(self,node):
        for d in node.declarations: d.accept(self)
        for s in node.statements: s.accept(self)
    def visitBlock(self,node):
        for d in node.declarations: d.accept(self)
        for s in node.statements: s.accept(self)
    def visitDeclaration(self,node): self.alloc_var(node.name)
    def visitAssignment(self,node):
        node.rhs.accept(self)
        addr=self.alloc_var(node.name)
        if node.index_expr: self.emit("; array indexing not implemented")
        self.emit(f"MOVWF {addr}")
    def visitIf(self,node):
        else_lbl=self.make_label("else")
        end_lbl=self.make_label("ifend")
        node.condition.accept(self)
        self.emit("CPFSEQ W")
        self.emit(f"GOTO {else_lbl}")
        node.then_block.accept(self)
        self.emit(f"GOTO {end_lbl}")
        self.emit(f"{else_lbl}:")
        if node.else_block: node.else_block.accept(self)
        self.emit(f"{end_lbl}:")
    def visitWhile(self,node):
        top_lbl=self.make_label("while")
        end_lbl=self.make_label("wend")
        self.emit(f"{top_lbl}:")
        node.condition.accept(self)
        self.emit("CPFSEQ W")
        self.emit(f"GOTO {end_lbl}")
        node.body.accept(self)
        self.emit(f"GOTO {top_lbl}")
        self.emit(f"{end_lbl}:")
    def visitBinaryOp(self,node):
        node.left.accept(self)
        self.emit("MOVWF 0x7F")
        node.right.accept(self)
        if node.op == "+": self.emit("ADDWF 0x7F, W")
        elif node.op == "-": self.emit("SUBWF 0x7F, W")
        elif node.op == "*": self.emit("; MULT not implemented")
        elif node.op == "/": self.emit("; DIV not implemented")
        else: self.emit(f"; op {node.op} not implemented")
    def visitUnaryOp(self,node):
        node.expr.accept(self)
        if node.op == "-": self.emit("; unary minus not implemented")
        elif node.op == "!": self.emit("; logical not not implemented")
    def visitLiteral(self,node):
        val=node.value & 0xFF; self.emit(f"MOVLW 0x{val:02X}")
    def visitIdentifier(self,node): self.emit(f"MOVF {self.alloc_var(node.name)}, W")
    def visitParenthesized(self,node): node.expr.accept(self)

# %%
def test_modified_parser():
    examples = [
        ("Simple assignment", "int x; x = 42;"),
        ("Arithmetic", "int a; a = (2 + 3) * 4;"),
        ("If-Else + Loop", """
            int n;
            n = 0;
            while (n < 3) {
              if (n == 1) { n = n + 10; }
              n = n + 1;
            }
        """),
        # Test with main function still works
        ("With main function", """
            int main() {
                int z;
                z = 100;
                if (z > 50) {
                    z = z - 25;
                }
            }
        """)
    ]

    for title, code in examples:
        print(f"\n=== Example: {title} ===")
        print(code.strip(), "\n")
        try:
            # Initialize lexer and tokenize
            lexer = MiniCLexer(code)
            tokens = lexer.tokenize()
            
            # Use the modified parser
            parser = Parser(tokens)
            program = parser.parse()
            
            # Generate code
            cg = CodeGenVisitor()
            program.accept(cg)
            result = cg.get_code()
            print(result)
        except Exception as e:
            print("ERROR:", e)

# Run this function instead of the original main()
if __name__ == "__main__":
    test_modified_parser()

# %%



