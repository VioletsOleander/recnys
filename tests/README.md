# Test Structure

`constants.py` defines constants for arrangement and assertion. `arranger.py` defines utility functions for
arrangement, `assertor.py` defines utility functions for assertion.

The tests under `tests/` should import necessary utility functions and constants under `src/recnys/testing/` to do
arrangement and assertion, and import source code under `src/recnys/` to act.
