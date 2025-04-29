import unittest
import sys
from io import StringIO

# Import the necessary components from your compiler
from compilation import MiniCLexer, Parser, CodeGenVisitor

class TestCompilerIntegration(unittest.TestCase):
    """Integration tests for the complete compilation process"""
    
    def compile_code(self, source_code):
        """Helper method to compile source code to assembly"""
        try:
            # Perform lexical analysis
            lexer = MiniCLexer(source_code)
            tokens = lexer.tokenize()
            
            # Parse the tokens
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Generate code
            code_gen = CodeGenVisitor()
            ast.accept(code_gen)
            
            # Return the generated assembly code
            return code_gen.get_code()
        except Exception as e:
            self.fail(f"Compilation failed: {str(e)}")
    
    def setUp(self):
        # Redirect stdout to capture print statements
        self.captured_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.captured_output
    
    def tearDown(self):
        # Restore stdout
        sys.stdout = self.original_stdout
        # Print captured output for each test
        print(f"\n=== Test: {self._testMethodName} ===\n")
        print(self.captured_output.getvalue())
        self.captured_output.close()
    
    def test_variable_declaration_and_assignment(self):
        """Test simple variable declaration and assignment"""
        source_code = """
        int x;
        x = 42;
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify that the assembly contains the correct instructions
        self.assertIn("MOVLW 0x2A", assembly, "Expected MOVLW 0x2A for loading 42")
        self.assertIn("MOVWF 0x20", assembly, "Expected MOVWF 0x20 for storing to x")
        print("Assertions Passed: MOVLW 0x2A and MOVWF 0x20 found")
    
    def test_arithmetic_operations(self):
        """Test arithmetic operations"""
        source_code = """
        int a;
        int b;
        int c;
        
        a = 10;
        b = 5;
        c = a + b;
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify variable assignments
        self.assertIn("MOVLW 0x0A", assembly, "Expected MOVLW 0x0A for a = 10")
        self.assertIn("MOVWF 0x20", assembly, "Expected MOVWF 0x20 for storing a")
        self.assertIn("MOVLW 0x05", assembly, "Expected MOVLW 0x05 for b = 5")
        self.assertIn("MOVWF 0x21", assembly, "Expected MOVWF 0x21 for storing b")
        # Verify addition
        self.assertIn("MOVF 0x20, W", assembly, "Expected MOVF 0x20, W to load a")
        self.assertIn("MOVWF 0x7F", assembly, "Expected MOVWF 0x7F to store a to temp")
        self.assertIn("MOVF 0x21, W", assembly, "Expected MOVF 0x21, W to load b")
        self.assertIn("ADDWF 0x7F, W", assembly, "Expected ADDWF 0x7F, W for addition")
        self.assertIn("MOVWF 0x22", assembly, "Expected MOVWF 0x22 for storing c")
        print("Assertions Passed: All expected instructions for addition found")
    
    def test_subtraction(self):
        """Test subtraction operation"""
        source_code = """
        int a;
        int b;
        int result;
        
        a = 15;
        b = 7;
        result = a - b;
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify variable assignments
        self.assertIn("MOVLW 0x0F", assembly, "Expected MOVLW 0x0F for a = 15")
        self.assertIn("MOVWF 0x20", assembly, "Expected MOVWF 0x20 for storing a")
        self.assertIn("MOVLW 0x07", assembly, "Expected MOVLW 0x07 for b = 7")
        self.assertIn("MOVWF 0x21", assembly, "Expected MOVWF 0x21 for storing b")
        # Verify subtraction
        self.assertIn("MOVF 0x20, W", assembly, "Expected MOVF 0x20, W to load a")
        self.assertIn("MOVWF 0x7F", assembly, "Expected MOVWF 0x7F to store a to temp")
        self.assertIn("MOVF 0x21, W", assembly, "Expected MOVF 0x21, W to load b")
        self.assertIn("SUBWF 0x7F, W", assembly, "Expected SUBWF 0x7F, W for subtraction")
        self.assertIn("MOVWF 0x22", assembly, "Expected MOVWF 0x22 for storing result")
        print("Assertions Passed: All expected instructions for subtraction found")
    
    def test_multiplication(self):
        """Test multiplication operation"""
        source_code = """
        int a;
        int b;
        int result;
        
        a = 6;
        b = 4;
        result = a * b;
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify variable assignments
        self.assertIn("MOVLW 0x06", assembly, "Expected MOVLW 0x06 for a = 6")
        self.assertIn("MOVWF 0x20", assembly, "Expected MOVWF 0x20 for storing a")
        self.assertIn("MOVLW 0x04", assembly, "Expected MOVLW 0x04 for b = 4")
        self.assertIn("MOVWF 0x21", assembly, "Expected MOVWF 0x21 for storing b")
        # Verify multiplication (not implemented)
        self.assertIn("MOVF 0x20, W", assembly, "Expected MOVF 0x20, W to load a")
        self.assertIn("MOVWF 0x7F", assembly, "Expected MOVWF 0x7F to store a to temp")
        self.assertIn("MOVF 0x21, W", assembly, "Expected MOVF 0x21, W to load b")
        self.assertIn("; MULT not implemented", assembly, "Expected MULT not implemented comment")
        self.assertIn("MOVWF 0x22", assembly, "Expected MOVWF 0x22 for storing result")
        print("Assertions Passed: Expected instructions for multiplication found (not implemented)")
    
    def test_division(self):
        """Test division operation"""
        source_code = """
        int a;
        int b;
        int result;
        
        a = 20;
        b = 5;
        result = a / b;
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify variable assignments
        self.assertIn("MOVLW 0x14", assembly, "Expected MOVLW 0x14 for a = 20")
        self.assertIn("MOVWF 0x20", assembly, "Expected MOVWF 0x20 for storing a")
        self.assertIn("MOVLW 0x05", assembly, "Expected MOVLW 0x05 for b = 5")
        self.assertIn("MOVWF 0x21", assembly, "Expected MOVWF 0x21 for storing b")
        # Verify division (not implemented)
        self.assertIn("MOVF 0x20, W", assembly, "Expected MOVF 0x20, W to load a")
        self.assertIn("MOVWF 0x7F", assembly, "Expected MOVWF 0x7F to store a to temp")
        self.assertIn("MOVF 0x21, W", assembly, "Expected MOVF 0x21, W to load b")
        self.assertIn("; DIV not implemented", assembly, "Expected DIV not implemented comment")
        self.assertIn("MOVWF 0x22", assembly, "Expected MOVWF 0x22 for storing result")
        print("Assertions Passed: Expected instructions for division found (not implemented)")
    
    def test_comparison_operations(self):
        """Test comparison operations"""
        source_code = """
        int a;
        int b;
        int result;
        
        a = 10;
        b = 5;
        
        if (a > b) {
            result = 1;
        } else {
            result = 0;
        }
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify variable assignments
        self.assertIn("MOVLW 0x0A", assembly, "Expected MOVLW 0x0A for a = 10")
        self.assertIn("MOVWF 0x20", assembly, "Expected MOVWF 0x20 for storing a")
        self.assertIn("MOVLW 0x05", assembly, "Expected MOVLW 0x05 for b = 5")
        self.assertIn("MOVWF 0x21", assembly, "Expected MOVWF 0x21 for storing b")
        # Verify comparison (not implemented)
        self.assertIn("MOVF 0x20, W", assembly, "Expected MOVF 0x20, W to load a")
        self.assertIn("MOVWF 0x7F", assembly, "Expected MOVWF 0x7F to store a to temp")
        self.assertIn("MOVF 0x21, W", assembly, "Expected MOVF 0x21, W to load b")
        self.assertIn("; op > not implemented", assembly, "Expected op > not implemented comment")
        self.assertIn("CPFSEQ W", assembly, "Expected CPFSEQ W for comparison")
        self.assertIn("GOTO else0", assembly, "Expected GOTO else0 for branching")
        self.assertIn("MOVLW 0x01", assembly, "Expected MOVLW 0x01 for result = 1")
        self.assertIn("MOVLW 0x00", assembly, "Expected MOVLW 0x00 for result = 0")
        self.assertIn("MOVWF 0x22", assembly, "Expected MOVWF 0x22 for storing result")
        print("Assertions Passed: Expected instructions for comparison found (not implemented)")
    
    def test_logical_operations(self):
        """Test logical operations (AND, OR)"""
        source_code = """
        int a;
        int b;
        int c;
        int d;
        
        a = 1;
        b = 0;
        
        if (a && b) {
            c = 1;
        } else {
            c = 0;
        }
        
        if (a || b) {
            d = 1;
        } else {
            d = 0;
        }
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify variable assignments
        self.assertIn("MOVLW 0x01", assembly, "Expected MOVLW 0x01 for a = 1")
        self.assertIn("MOVWF 0x20", assembly, "Expected MOVWF 0x20 for storing a")
        self.assertIn("MOVLW 0x00", assembly, "Expected MOVLW 0x00 for b = 0")
        self.assertIn("MOVWF 0x21", assembly, "Expected MOVWF 0x21 for storing b")
        # Verify logical operations (not implemented)
        self.assertIn("MOVF 0x20, W", assembly, "Expected MOVF 0x20, W to load a")
        self.assertIn("MOVWF 0x7F", assembly, "Expected MOVWF 0x7F to store a to temp")
        self.assertIn("MOVF 0x21, W", assembly, "Expected MOVF 0x21, W to load b")
        self.assertIn("; op && not implemented", assembly, "Expected op && not implemented comment")
        self.assertIn("; op || not implemented", assembly, "Expected op || not implemented comment")
        self.assertIn("CPFSEQ W", assembly, "Expected CPFSEQ W for comparison")
        self.assertIn("MOVWF 0x22", assembly, "Expected MOVWF 0x22 for storing c")
        self.assertIn("MOVWF 0x23", assembly, "Expected MOVWF 0x23 for storing d")
        print("Assertions Passed: Expected instructions for logical operations found (not implemented)")
    
    def test_if_statement(self):
        """Test if statement without else"""
        source_code = """
        int x;
        int y;
        
        x = 10;
        
        if (x > 5) {
            y = 1;
        }
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify variable assignment
        self.assertIn("MOVLW 0x0A", assembly, "Expected MOVLW 0x0A for x = 10")
        self.assertIn("MOVWF 0x20", assembly, "Expected MOVWF 0x20 for storing x")
        # Verify comparison (not implemented)
        self.assertIn("MOVF 0x20, W", assembly, "Expected MOVF 0x20, W to load x")
        self.assertIn("MOVWF 0x7F", assembly, "Expected MOVWF 0x7F to store x to temp")
        self.assertIn("MOVLW 0x05", assembly, "Expected MOVLW 0x05 for comparison")
        self.assertIn("; op > not implemented", assembly, "Expected op > not implemented comment")
        self.assertIn("CPFSEQ W", assembly, "Expected CPFSEQ W for comparison")
        self.assertIn("GOTO else0", assembly, "Expected GOTO else0 for branching")
        self.assertIn("MOVLW 0x01", assembly, "Expected MOVLW 0x01 for y = 1")
        self.assertIn("MOVWF 0x21", assembly, "Expected MOVWF 0x21 for storing y")
        self.assertIn("GOTO ifend1", assembly, "Expected GOTO ifend1 to skip else")
        print("Assertions Passed: Expected instructions for if statement found (not implemented)")
    
    def test_if_else_statement(self):
        """Test if-else statement"""
        source_code = """
        int x;
        int y;
        
        x = 3;
        
        if (x > 5) {
            y = 1;
        } else {
            y = 0;
        }
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify variable assignment
        self.assertIn("MOVLW 0x03", assembly, "Expected MOVLW 0x03 for x = 3")
        self.assertIn("MOVWF 0x20", assembly, "Expected MOVWF 0x20 for storing x")
        # Verify comparison and branching
        self.assertIn("MOVF 0x20, W", assembly, "Expected MOVF 0x20, W to load x")
        self.assertIn("MOVWF 0x7F", assembly, "Expected MOVWF 0x7F to store x to temp")
        self.assertIn("MOVLW 0x05", assembly, "Expected MOVLW 0x05 for comparison")
        self.assertIn("; op > not implemented", assembly, "Expected op > not implemented comment")
        self.assertIn("CPFSEQ W", assembly, "Expected CPFSEQ W for comparison")
        self.assertIn("GOTO else0", assembly, "Expected GOTO else0 for else branch")
        self.assertIn("MOVLW 0x01", assembly, "Expected MOVLW 0x01 for y = 1")
        self.assertIn("MOVLW 0x00", assembly, "Expected MOVLW 0x00 for y = 0")
        self.assertIn("MOVWF 0x21", assembly, "Expected MOVWF 0x21 for storing y")
        self.assertIn("GOTO ifend1", assembly, "Expected GOTO ifend1 to skip else")
        self.assertIn("else0:", assembly, "Expected else0 label")
        self.assertIn("ifend1:", assembly, "Expected ifend1 label")
        print("Assertions Passed: Expected instructions for if-else statement found (not implemented)")
    
    def test_while_loop(self):
        """Test while loop"""
        source_code = """
        int i;
        int sum;
        
        i = 0;
        sum = 0;
        
        while (i < 5) {
            sum = sum + i;
            i = i + 1;
        }
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify variable assignments
        self.assertIn("MOVLW 0x00", assembly, "Expected MOVLW 0x00 for i = 0 and sum = 0")
        self.assertIn("MOVWF 0x20", assembly, "Expected MOVWF 0x20 for storing i")
        self.assertIn("MOVWF 0x21", assembly, "Expected MOVWF 0x21 for storing sum")
        # Verify while loop structure
        self.assertIn("while0:", assembly, "Expected while0 label")
        self.assertIn("wend1:", assembly, "Expected wend1 label")
        # Verify comparison (not implemented)
        self.assertIn("MOVF 0x20, W", assembly, "Expected MOVF 0x20, W to load i")
        self.assertIn("MOVWF 0x7F", assembly, "Expected MOVWF 0x7F to store i to temp")
        self.assertIn("MOVLW 0x05", assembly, "Expected MOVLW 0x05 for comparison")
        self.assertIn("; op < not implemented", assembly, "Expected op < not implemented comment")
        self.assertIn("CPFSEQ W", assembly, "Expected CPFSEQ W for comparison")
        # Verify loop body
        self.assertIn("MOVF 0x21, W", assembly, "Expected MOVF 0x21, W to load sum")
        self.assertIn("ADDWF 0x7F, W", assembly, "Expected ADDWF 0x7F, W for sum += i")
        self.assertIn("MOVLW 0x01", assembly, "Expected MOVLW 0x01 for i += 1")
        self.assertIn("GOTO while0", assembly, "Expected GOTO while0 to loop back")
        print("Assertions Passed: Expected instructions for while loop found (not implemented)")
    
    def test_nested_if_statements(self):
        """Test nested if statements"""
        source_code = """
        int x;
        int y;
        int z;
        
        x = 10;
        y = 5;
        
        if (x > 5) {
            if (y < 10) {
                z = 1;
            } else {
                z = 2;
            }
        } else {
            z = 3;
        }
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify variable assignments
        self.assertIn("MOVLW 0x0A", assembly, "Expected MOVLW 0x0A for x = 10")
        self.assertIn("MOVWF 0x20", assembly, "Expected MOVWF 0x20 for storing x")
        self.assertIn("MOVLW 0x05", assembly, "Expected MOVLW 0x05 for y = 5")
        self.assertIn("MOVWF 0x21", assembly, "Expected MOVWF 0x21 for storing y")
        # Verify nested structure
        self.assertGreaterEqual(assembly.count("GOTO"), 3, "Expected at least 3 GOTO instructions")
        self.assertGreaterEqual(assembly.count("if"), 2, "Expected at least 2 if-related labels")
        self.assertGreaterEqual(assembly.count("else"), 2, "Expected at least 2 else-related labels")
        self.assertIn("MOVLW 0x01", assembly, "Expected MOVLW 0x01 for z = 1")
        self.assertIn("MOVLW 0x02", assembly, "Expected MOVLW 0x02 for z = 2")
        self.assertIn("MOVLW 0x03", assembly, "Expected MOVLW 0x03 for z = 3")
        self.assertIn("MOVWF 0x22", assembly, "Expected MOVWF 0x22 for storing z")
        print("Assertions Passed: All expected instructions for nested if statements found")
    
    def test_complex_expressions(self):
        """Test complex expressions with parentheses and operator precedence"""
        source_code = """
        int a;
        int b;
        int c;
        int result;
        
        a = 5;
        b = 3;
        c = 2;
        
        result = a + b * c;  // Should be 5 + (3 * 2) = 11
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify variable assignments
        self.assertIn("MOVLW 0x05", assembly, "Expected MOVLW 0x05 for a = 5")
        self.assertIn("MOVWF 0x20", assembly, "Expected MOVWF 0x20 for storing a")
        self.assertIn("MOVLW 0x03", assembly, "Expected MOVLW 0x03 for b = 3")
        self.assertIn("MOVWF 0x21", assembly, "Expected MOVWF 0x21 for storing b")
        self.assertIn("MOVLW 0x02", assembly, "Expected MOVLW 0x02 for c = 2")
        self.assertIn("MOVWF 0x22", assembly, "Expected MOVWF 0x22 for storing c")
        # Verify expression (multiplication not implemented)
        self.assertIn("MOVF 0x21, W", assembly, "Expected MOVF 0x21, W to load b")
        self.assertIn("MOVWF 0x7F", assembly, "Expected MOVWF 0x7F to store b to temp")
        self.assertIn("MOVF 0x22, W", assembly, "Expected MOVF 0x22, W to load c")
        self.assertIn("; MULT not implemented", assembly, "Expected MULT not implemented comment")
        self.assertIn("MOVWF 0x23", assembly, "Expected MOVWF 0x23 for storing result")
        print("Assertions Passed: Expected instructions for complex expression found (multiplication not implemented)")
    
    def test_array_operations(self):
        """Test array declarations and operations"""
        source_code = """
        int arr[5];
        
        arr[0] = 10;
        arr[1] = 20;
        arr[2] = arr[0] + arr[1];
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify assignments
        self.assertIn("MOVLW 0x0A", assembly, "Expected MOVLW 0x0A for arr[0] = 10")
        self.assertIn("MOVLW 0x14", assembly, "Expected MOVLW 0x14 for arr[1] = 20")
        self.assertIn("; array indexing not implemented", assembly, "Expected array indexing not implemented comment")
        self.assertGreaterEqual(assembly.count("MOVWF"), 3, "Expected at least 3 MOVWF instructions")
        print("Assertions Passed: Expected instructions for array operations found (indexing not implemented)")
    
    def test_main_function(self):
        """Test compilation of code in a main function"""
        source_code = """
        int main() {
            int x;
            x = 42;
        }
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify code generation
        self.assertIn("MOVLW 0x2A", assembly, "Expected MOVLW 0x2A for x = 42")
        self.assertIn("MOVWF 0x20", assembly, "Expected MOVWF 0x20 for storing x")
        print("Assertions Passed: Expected instructions for main function found")
    
    def test_full_program(self):
        """Test a complete program with multiple statements"""
        source_code = """
        int main() {
            int i;
            int sum;
            int n;
            
            n = 10;
            sum = 0;
            i = 1;
            
            while (i <= n) {
                sum = sum + i;
                i = i + 1;
            }
        }
        """
        print("Source Code:\n", source_code.strip())
        assembly = self.compile_code(source_code)
        print("Generated Assembly:\n", assembly)
        
        # Verify variable assignments
        self.assertIn("MOVLW 0x0A", assembly, "Expected MOVLW 0x0A for n = 10")
        self.assertIn("MOVWF 0x22", assembly, "Expected MOVWF 0x22 for storing n")
        self.assertIn("MOVLW 0x00", assembly, "Expected MOVLW 0x00 for sum = 0")
        self.assertIn("MOVWF 0x21", assembly, "Expected MOVWF 0x21 for storing sum")
        self.assertIn("MOVLW 0x01", assembly, "Expected MOVLW 0x01 for i = 1")
        self.assertIn("MOVWF 0x20", assembly, "Expected MOVWF 0x20 for storing i")
        # Verify while loop structure
        self.assertIn("while0:", assembly, "Expected while0 label")
        self.assertIn("wend1:", assembly, "Expected wend1 label")
        self.assertIn("MOVF 0x20, W", assembly, "Expected MOVF 0x20, W to load i")
        self.assertIn("MOVWF 0x7F", assembly, "Expected MOVWF 0x7F to store i to temp")
        self.assertIn("MOVF 0x22, W", assembly, "Expected MOVF 0x22, W to load n")
        self.assertIn("; op <= not implemented", assembly, "Expected op <= not implemented comment")
        self.assertIn("CPFSEQ W", assembly, "Expected CPFSEQ W for comparison")
        self.assertIn("GOTO while0", assembly, "Expected GOTO while0 to loop back")
        print("Assertions Passed: All expected instructions for full program found (comparison not implemented)")

if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
