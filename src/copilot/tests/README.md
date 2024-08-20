# How to run

1. Open the terminal
2. Navigate to `eak-copilot/` directory (root directory)
3. Install both `src/copilot/requirements.txt` and `src/copilot/tests/requirements.txt` in your environnement
4. Type `pytest`, enter. This will run all test files stored in the tests/ directory.

# Implementation

- Tests are stored in `src/copilot/tests/`.
- Currently, there is a single file, `test_service_source.py` which implements one test on services related to Source database. To add a new test, simply create a new method in the file. It needs to have `dbsession` as parameter to interact with the database.
- Tests need to contains one or more `assert` statements for `pytest` to recognize the method as a test.
    - More information [here](https://docs.pytest.org/en/7.1.x/how-to/assert.html).
- Note that after each test, changes made are reverted
    - `transaction.rollback()` on line 64 in `test_service_source.py`
- A temporary docker container for testing purpose is created using the library `PostgresContainer`, which allows such tests on the database.
    - If you want to write test that does not require the database, it is not necessary to include the methods `engine`, `tables`, and `dbsession` in the file.
