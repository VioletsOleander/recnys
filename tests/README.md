# Test Structure

All tests share the same `recnys.yaml`, `variables.yaml` file under `tests/resources`.

`constants.py` defines constants for arrangement and assertion. `arranger.py` defines utility functions for
arrangement, `assertor.py` defines utility functions for assertion.

All tests share the utility function and constants defined in `src/recnys/testing/arranger.py`,
`src/recnys/testing/constants.py`.

The tests under `tests/` should import necessary utility functions and constants under `src/recnys/testing/` to do
arrangement and assertion, and import source code under `src/recnys/` to act.

Those resources are kind of scattered , but neither move the resources file into `testing/` nor move the code into
`tests/` are desirable. Therefore constants, assertion utilities should be manually align with the files under
`tests/resources/`). Currently I think there is no better way to improve this organization, just using split window for
editing.
