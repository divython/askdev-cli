from askdev.core.engine import ErrorDatabase

def test_error_database_loads_default_db():
    db = ErrorDatabase(db_paths=[])
    assert db.get_error_message("404") == "Not Found - The requested resource could not be found."

def test_error_database_loads_custom_db(tmp_path):
    custom_db_path = tmp_path / "custom_db.json"
    custom_db_path.write_text('{"CUSTOM_ERROR": "This is a custom error."}')
    db = ErrorDatabase(db_paths=[custom_db_path])
    assert db.get_error_message("custom_error") == "This is a custom error."
