import unittest
from io import StringIO
import sys

# Import the test module - adjust the import as needed based on your actual file name
from paste import TestMiniCLexer, TestParser, TestCodeGenVisitor, TestParserProgramStyles

# Create a test suite with all the test classes
def create_test_suite():
    suite = unittest.TestSuite()
    
    # Add all tests from each test class
    suite.addTest(unittest.makeSuite(TestMiniCLexer))
    suite.addTest(unittest.makeSuite(TestParser))
    suite.addTest(unittest.makeSuite(TestCodeGenVisitor))
    suite.addTest(unittest.makeSuite(TestParserProgramStyles))
    
    return suite

if __name__ == "__main__":
    # Create the test suite
    suite = create_test_suite()
    
    # Create a test runner that will output detailed results
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run the tests
    result = runner.run(suite)
    
    # Output the summary
    print("\nSUMMARY:")
    print(f"Ran {result.testsRun} tests")
    print(f"Successes: {result.testsRun - len(result.errors) - len(result.failures)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    # If there were failures or errors, print them
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"\n{test}")
            print(traceback)
            
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"\n{test}")
            print(traceback)