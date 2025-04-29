import unittest
from io import StringIO
import sys

# Import the compiler components from your main code
# If these were in a separate module, you'd import them differently
# For our test, we'll assume they're imported directly

# Since we're working with the code from the notebook, let's make sure our tests will work with those classes
from compilation import MiniCLexer, Token, Parser, CodeGenVisitor
from compilation import Program, Block, Declaration, AssignmentStatement, IfStatement, WhileStatement
from compilation import BinaryOp, UnaryOp, Literal, Identifier, Parenthesized, ParsingException

class TestMiniCLexer(unittest.TestCase):
    """Test cases for the lexical analyzer"""
    
    def test_empty_input(self):
        """Test that empty input produces no tokens"""
        lexer = MiniCLexer("")
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 0)
    
    def test_whitespace_and_comments(self):
        """Test that whitespace and comments are ignored"""
        code = """
        // This is a comment
        /* This is a 
           multiline comment */
           
        int x;  // Another comment
        """
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        # We should have 3 tokens: KW_INT, IDENT, SEMICOLON
        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[0].type, "KW_INT")
        self.assertEqual(tokens[1].type, "IDENT")
        self.assertEqual(tokens[1].value, "x")
        self.assertEqual(tokens[2].type, "SEMICOLON")
    
    def test_keywords(self):
        """Test recognition of keywords"""
        code = "int float bool char if else while main"
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 8)
        expected_types = [
            "KW_INT", "KW_FLOAT", "KW_BOOL", "KW_CHAR", 
            "KW_IF", "KW_ELSE", "KW_WHILE", "KW_MAIN"
        ]
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)
    
    def test_identifiers(self):
        """Test recognition of identifiers"""
        code = "x y1 _z count2 MAX_SIZE"
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 5)
        for token in tokens:
            self.assertEqual(token.type, "IDENT")
        self.assertEqual(tokens[0].value, "x")
        self.assertEqual(tokens[1].value, "y1")
        self.assertEqual(tokens[2].value, "_z")
        self.assertEqual(tokens[3].value, "count2")
        self.assertEqual(tokens[4].value, "MAX_SIZE")
    
    def test_literals(self):
        """Test recognition of integer literals"""
        code = "0 42 123 9999"
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 4)
        for token in tokens:
            self.assertEqual(token.type, "INT_LITERAL")
        self.assertEqual(tokens[0].value, "0")
        self.assertEqual(tokens[1].value, "42")
        self.assertEqual(tokens[2].value, "123")
        self.assertEqual(tokens[3].value, "9999")
    
    def test_operators(self):
        """Test recognition of operators"""
        code = "+ - * / < > <= >= == != = && || !"
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 14)
        expected_types = [
            "PLUS", "MINUS", "MULT", "DIV",
            "LT", "GT", "LTE", "GTE",
            "EQ", "NEQ", "ASSIGN",
            "AND", "OR", "NOT"
        ]
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)
    
    def test_delimiters(self):
        """Test recognition of delimiters"""
        code = "( ) { } [ ] ; ,"
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 8)
        expected_types = [
            "LPAREN", "RPAREN", "LBRACE", "RBRACE",
            "LBRACKET", "RBRACKET", "SEMICOLON", "COMMA"
        ]
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)
    
    def test_complete_program(self):
        """Test tokenization of a complete program"""
        code = """
        int main() {
            int x;
            x = 10;
            if (x > 5) {
                x = x - 1;
            }
        }
        """
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        # Count the expected tokens: 'int', 'main', '(', ')', '{', 'int', 'x', ';',
        # 'x', '=', '10', ';', 'if', '(', 'x', '>', '5', ')', '{',
        # 'x', '=', 'x', '-', '1', ';', '}', '}'
        self.assertEqual(len(tokens), 27)
        # Check a few specific tokens
        self.assertEqual(tokens[0].type, "KW_INT")
        self.assertEqual(tokens[1].type, "KW_MAIN")
        self.assertEqual(tokens[5].type, "KW_INT")
        self.assertEqual(tokens[6].type, "IDENT")
        self.assertEqual(tokens[6].value, "x")
        self.assertEqual(tokens[10].type, "INT_LITERAL")
        self.assertEqual(tokens[10].value, "10")
        self.assertEqual(tokens[12].type, "KW_IF")


class TestParser(unittest.TestCase):
    """Test cases for the parser"""
    
    def test_parse_simple_declaration(self):
        """Test parsing a simple variable declaration"""
        code = "int x;"
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        self.assertEqual(len(program.declarations), 1)
        self.assertEqual(len(program.statements), 0)
        
        decl = program.declarations[0]
        self.assertEqual(decl.var_type, "int")
        self.assertEqual(decl.name, "x")
        self.assertIsNone(decl.array_size)
    
    def test_parse_array_declaration(self):
        """Test parsing an array declaration"""
        code = "int arr[10];"
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        self.assertEqual(len(program.declarations), 1)
        decl = program.declarations[0]
        self.assertEqual(decl.var_type, "int")
        self.assertEqual(decl.name, "arr")
        self.assertEqual(decl.array_size, 10)
    
    def test_parse_assignment(self):
        """Test parsing a simple assignment statement"""
        code = "int x; x = 42;"
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        self.assertEqual(len(program.declarations), 1)
        self.assertEqual(len(program.statements), 1)
        
        stmt = program.statements[0]
        self.assertIsInstance(stmt, AssignmentStatement)
        self.assertEqual(stmt.name, "x")
        self.assertIsNone(stmt.index_expr)
        self.assertIsInstance(stmt.rhs, Literal)
        self.assertEqual(stmt.rhs.value, 42)
    
    def test_parse_array_assignment(self):
        """Test parsing an array element assignment"""
        code = "int arr[10]; arr[5] = 42;"
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        self.assertEqual(len(program.declarations), 1)
        self.assertEqual(len(program.statements), 1)
        
        stmt = program.statements[0]
        self.assertIsInstance(stmt, AssignmentStatement)
        self.assertEqual(stmt.name, "arr")
        self.assertIsInstance(stmt.index_expr, Literal)
        self.assertEqual(stmt.index_expr.value, 5)
        self.assertIsInstance(stmt.rhs, Literal)
        self.assertEqual(stmt.rhs.value, 42)
    
    def test_parse_if_statement(self):
        """Test parsing an if statement"""
        code = """
        int x;
        x = 10;
        if (x > 5) {
            x = 0;
        }
        """
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        self.assertEqual(len(program.declarations), 1)
        self.assertEqual(len(program.statements), 2)
        
        if_stmt = program.statements[1]
        self.assertIsInstance(if_stmt, IfStatement)
        self.assertIsInstance(if_stmt.condition, BinaryOp)
        self.assertEqual(if_stmt.condition.op, ">")
        self.assertIsInstance(if_stmt.then_block, Block)
        self.assertIsNone(if_stmt.else_block)
        
        # Check the condition
        self.assertIsInstance(if_stmt.condition.left, Identifier)
        self.assertEqual(if_stmt.condition.left.name, "x")
        self.assertIsInstance(if_stmt.condition.right, Literal)
        self.assertEqual(if_stmt.condition.right.value, 5)
        
        # Check the then block
        self.assertEqual(len(if_stmt.then_block.declarations), 0)
        self.assertEqual(len(if_stmt.then_block.statements), 1)
        self.assertIsInstance(if_stmt.then_block.statements[0], AssignmentStatement)
        self.assertEqual(if_stmt.then_block.statements[0].name, "x")
        self.assertEqual(if_stmt.then_block.statements[0].rhs.value, 0)
    
    def test_parse_if_else_statement(self):
        """Test parsing an if-else statement"""
        code = """
        int x;
        x = 10;
        if (x > 5) {
            x = 0;
        } else {
            x = 1;
        }
        """
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        if_stmt = program.statements[1]
        self.assertIsInstance(if_stmt, IfStatement)
        self.assertIsNotNone(if_stmt.else_block)
        
        # Check the else block
        self.assertEqual(len(if_stmt.else_block.declarations), 0)
        self.assertEqual(len(if_stmt.else_block.statements), 1)
        self.assertIsInstance(if_stmt.else_block.statements[0], AssignmentStatement)
        self.assertEqual(if_stmt.else_block.statements[0].name, "x")
        self.assertEqual(if_stmt.else_block.statements[0].rhs.value, 1)
    
    def test_parse_while_statement(self):
        """Test parsing a while statement"""
        code = """
        int i;
        i = 0;
        while (i < 10) {
            i = i + 1;
        }
        """
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        while_stmt = program.statements[1]
        self.assertIsInstance(while_stmt, WhileStatement)
        self.assertIsInstance(while_stmt.condition, BinaryOp)
        self.assertEqual(while_stmt.condition.op, "<")
        self.assertIsInstance(while_stmt.body, Block)
        
        # Check the condition
        self.assertIsInstance(while_stmt.condition.left, Identifier)
        self.assertEqual(while_stmt.condition.left.name, "i")
        self.assertIsInstance(while_stmt.condition.right, Literal)
        self.assertEqual(while_stmt.condition.right.value, 10)
        
        # Check the body
        self.assertEqual(len(while_stmt.body.declarations), 0)
        self.assertEqual(len(while_stmt.body.statements), 1)
        self.assertIsInstance(while_stmt.body.statements[0], AssignmentStatement)
        self.assertEqual(while_stmt.body.statements[0].name, "i")
        self.assertIsInstance(while_stmt.body.statements[0].rhs, BinaryOp)
        self.assertEqual(while_stmt.body.statements[0].rhs.op, "+")
    
    def test_parse_nested_expression(self):
        """Test parsing a nested expression"""
        code = "int x; x = (2 + 3) * 4;"
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        assign_stmt = program.statements[0]
        self.assertIsInstance(assign_stmt, AssignmentStatement)
        self.assertIsInstance(assign_stmt.rhs, BinaryOp)
        self.assertEqual(assign_stmt.rhs.op, "*")
        
        # Check left side of multiplication (should be the parenthesized expression)
        self.assertIsInstance(assign_stmt.rhs.left, Parenthesized)
        self.assertIsInstance(assign_stmt.rhs.left.expr, BinaryOp)
        self.assertEqual(assign_stmt.rhs.left.expr.op, "+")
        self.assertEqual(assign_stmt.rhs.left.expr.left.value, 2)
        self.assertEqual(assign_stmt.rhs.left.expr.right.value, 3)
        
        # Check right side of multiplication
        self.assertEqual(assign_stmt.rhs.right.value, 4)
    
    def test_parse_main_function(self):
        """Test parsing a program with main function"""
        code = """
        int main() {
            int x;
            x = 42;
        }
        """
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        self.assertEqual(len(program.declarations), 1)
        self.assertEqual(len(program.statements), 1)


class TestCodeGenVisitor(unittest.TestCase):
    """Test cases for the code generator"""
    
    def test_empty_program(self):
        """Test code generation for an empty program"""
        program = Program([], [])
        visitor = CodeGenVisitor()
        program.accept(visitor)
        code = visitor.get_code()
        self.assertEqual(code, "")
    
    def test_simple_declaration(self):
        """Test code generation for a simple declaration"""
        decl = Declaration("int", "x")
        program = Program([decl], [])
        visitor = CodeGenVisitor()
        program.accept(visitor)
        self.assertEqual(visitor.var_map["x"], "0x20")
        self.assertEqual(visitor.next_addr, 0x21)
        
    def test_simple_assignment(self):
        """Test code generation for a simple assignment"""
        decl = Declaration("int", "x")
        assign = AssignmentStatement("x", None, Literal(42))
        program = Program([decl], [assign])
        visitor = CodeGenVisitor()
        program.accept(visitor)
        code = visitor.get_code()
        expected_code = "MOVLW 0x2A\nMOVWF 0x20"
        self.assertEqual(code, expected_code)
    
    def test_binary_operation(self):
        """Test code generation for a binary operation"""
        decl = Declaration("int", "x")
        # x = 5 + 3
        expr = BinaryOp("+", Literal(5), Literal(3))
        assign = AssignmentStatement("x", None, expr)
        program = Program([decl], [assign])
        visitor = CodeGenVisitor()
        program.accept(visitor)
        code = visitor.get_code()
        expected_code = "MOVLW 0x05\nMOVWF 0x7F\nMOVLW 0x03\nADDWF 0x7F, W\nMOVWF 0x20"
        self.assertEqual(code, expected_code)
    
    def test_if_statement(self):
        """Test code generation for an if statement"""
        decl = Declaration("int", "x")
        # x = 10
        assign1 = AssignmentStatement("x", None, Literal(10))
        # if (x == 10) { x = 20; }
        cond = BinaryOp("==", Identifier("x"), Literal(10))
        then_assign = AssignmentStatement("x", None, Literal(20))
        then_block = Block([], [then_assign])
        if_stmt = IfStatement(cond, then_block)
        program = Program([decl], [assign1, if_stmt])
        visitor = CodeGenVisitor()
        program.accept(visitor)
        code = visitor.get_code()
        
        # Check that the code contains the labels and conditional branches
        self.assertIn("GOTO else0", code)
        self.assertIn("GOTO ifend1", code)
        self.assertIn("else0:", code)
        self.assertIn("ifend1:", code)
    
    def test_while_statement(self):
        """Test code generation for a while statement"""
        decl = Declaration("int", "i")
        # i = 0
        assign1 = AssignmentStatement("i", None, Literal(0))
        # while (i < 5) { i = i + 1; }
        cond = BinaryOp("<", Identifier("i"), Literal(5))
        body_assign = AssignmentStatement("i", None, BinaryOp("+", Identifier("i"), Literal(1)))
        body_block = Block([], [body_assign])
        while_stmt = WhileStatement(cond, body_block)
        program = Program([decl], [assign1, while_stmt])
        visitor = CodeGenVisitor()
        program.accept(visitor)
        code = visitor.get_code()
        
        # Check that the code contains the labels and conditional branches
        self.assertIn("while0:", code)
        self.assertIn("GOTO wend1", code)
        self.assertIn("GOTO while0", code)
        self.assertIn("wend1:", code)


# Additional test to make sure our parser handles both program styles
class TestParserProgramStyles(unittest.TestCase):
    """Test the parser's ability to handle different program styles"""
    
    def test_standalone_code(self):
        """Test parsing standalone code without main function"""
        code = """
        int x;
        x = 42;
        """
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        self.assertEqual(len(program.declarations), 1)
        self.assertEqual(len(program.statements), 1)
        self.assertEqual(program.declarations[0].name, "x")
        self.assertIsInstance(program.statements[0], AssignmentStatement)
    
    def test_main_function(self):
        """Test parsing code with main function"""
        code = """
        int main() {
            int x;
            x = 42;
        }
        """
        lexer = MiniCLexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        self.assertEqual(len(program.declarations), 1)
        self.assertEqual(len(program.statements), 1)
        self.assertEqual(program.declarations[0].name, "x")
        self.assertIsInstance(program.statements[0], AssignmentStatement)


if __name__ == "__main__":
    unittest.main()