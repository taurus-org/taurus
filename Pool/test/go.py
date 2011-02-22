
import poolunittest
import pool
import HTMLTestRunner

def go(test_output):
    test_output_file = file(test_output, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
                stream=test_output_file,
                title='Device Pool Unit Test',
                description='Device Pool Unit Test package',
                verbosity=2)   
    
    super_suite = poolunittest.PoolTestSuite()
    super_suite.addTest(pool.suite())
    runner.run(super_suite)
        
if __name__ == "__main__":
    test_output = "test_result.html"
    go(test_output)