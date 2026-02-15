## [0.4.0] - 2026-02-15

### Features

- [**breaking**] Support variables (#33)
- Add more command line options (#36)

### Bug Fixes

- Issue about file under directory parsed wrong (#31)

### Refactor

- Simplify record file key to string (#34)

### Documentation

- Update README (#35)

### Testing

- Refactor by replacing most logic with hardcoded expected values (#32)

### ️ Miscellaneous Tasks

- Add pytest-cov as dev tool (#29)
- Update message for newly created file (#30)

## [0.3.0] - 2026-01-31

### Features

- Support de-duplication in task canonicalization (#27)

### Refactor

- Files with prepend policy does not require hash information (#25)

### ️ Miscellaneous Tasks

- Make workflows more clear (#24)
- Release v0.3.0 (#28)

## [0.2.1] - 2026-01-25

### Bug Fixes

- Prepend policy overwrite the original content of dest file (#20)

### ️ Miscellaneous Tasks

- Fix permission of publish workflow (#19)
- Release v0.2.1 (#21)

## [0.2.0] - 2026-01-23

### Refactor

- *(frontend)* [**breaking**] Remove .config/ structure assumption for source repository (#14)

### Testing

- Refactor task canonicalization tests with pyfakefs (#15)
- Complete most test suites (#17)

### ️ Miscellaneous Tasks

- Update changelog body and processors in cliff.toml (#16)
- Release v0.2.0 (#18)

## [0.1.1] - 2026-01-15

### Bug Fixes

- Hash inconsistency issue caused by newlines change (#12)

### ️ Miscellaneous Tasks

- Release v0.1.1 (#13)

## [0.1.0] - 2026-01-15

### Features

- *(frontend)* Add initial implementation (#2)
- *(backend)* Add initial implementation (#3)

### Bug Fixes

- *(frontend)* Parse failure issue (#5)

### Other

- Initial commit

### Testing

- *(frontend)* Add integration and unit test (#6)
- *(backend)* Add initial backend test (#7)

### ️ Miscellaneous Tasks

- Maintaince utility update (#1)
- Add workflows (#4)
- Release v0.1.0 (#9)

