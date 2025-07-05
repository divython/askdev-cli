from askdev.core.parser import parse_stack_trace

def test_parse_java_stack_trace():
    log_content = '''
Exception in thread "main" java.lang.NullPointerException: Cannot invoke "String.length()" because "s" is null
	at com.example.MyClass.main(MyClass.java:10)
'''
    parsed_error = parse_stack_trace(log_content)
    assert parsed_error is not None
    assert parsed_error["thread"] == "main"
    assert parsed_error["exception"] == "java.lang.NullPointerException"
    assert parsed_error["message"] == 'Cannot invoke "String.length()" because "s" is null'
    assert parsed_error["file_path"] == "MyClass.java"
    assert parsed_error["line_number"] == 10

def test_parse_kotlin_stack_trace():
    log_content = '''
Exception in thread "main" kotlin.KotlinNullPointerException
	at com.example.MyKtClass.main(MyKtClass.kt:12)
'''
    parsed_error = parse_stack_trace(log_content)
    assert parsed_error is not None
    assert parsed_error["thread"] == "main"
    assert parsed_error["exception"] == "kotlin.KotlinNullPointerException"
    assert parsed_error["message"] == ""
    assert parsed_error["file_path"] == "MyKtClass.kt"
    assert parsed_error["line_number"] == 12