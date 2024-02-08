# Phoenix Test-Bench

This project is an integration testing suite for the phoenix system. It can be used to test individual source code files as well as orchestrated tests between running components.

## Running Tests

All tests are stored in the `test-bench/tests` directory and are referred to by filename. Tests can be run individually by name, or all tests can be run sequentially. All tests and setup commands should be run from the root of the phoenix directory.

Before running any tests, configure your environment. Replace `<bracketed>` items with appropriate values.
```
$ export PHOENIX_HOME=$(pwd)
```

Run a single test:
```
python3 ./test-bench/main.py --name <test-file-name.py>
```

Run all tests:
```
python3 ./test-bench/main.py --all
```
