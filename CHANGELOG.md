## [0.6.0] - 2026-07-24

### Summary

This release drastically refactored the whole codebase and introduces some breaking changes.

After this release, the command line arguments of `recnys` is expected to be relatively stable, but not guaranteed.

The most important changes in this release are introduce in pull request (#60). Refers to this pull request for further
details.

### Features

- Add --version option (#52)
- [**breaking**] Implement all required features (#60)
- Add ops counter (#64)

### Bug Fixes

- Resolve some issue found by real trail (#62)
- Wrong argument passed to template.render (#63)
- Non-existent sources detection (#74)

### Refactor

- Make T invariant, use ABC instead of Protocol (#56)
- Let --version lightweight (#67)
- Remove comment, rename file (#68)
- Upgrade ty and ruff, rename some func and var (#76)
- Use logger to replace arranger (#77)

### Documentation

- Add feature description (#57)
- Add configuration file specification (#58)
- Simplify delete feature, complete deduplicate feature (#59)
- Deprecate static/dynamic term (#61)
- Grammar and phrasing adjustment (#70)
- Remove wrong sentences in tests/README (#79)

### Testing

- Add exception test for scanner (#71)
- Implement primitive integration test (#78)

### Miscellaneous Tasks

- Update uv.lock (#55)
- Improve error message (#65)
- Update README and build backend version (#66)
- Update revision of some hooks (#69)
- Delete .vscode (#72)
- Sort words (#80)

## [0.5.0] - 2026-02-17

### Summary

This release mainly introduces some bug fixes.

### Features

- Add --clean command line option (#45)

### Bug Fixes

- Canonical configuration key construction issue (#44)
- Template file rendered but not correctly synced (#48)

### Miscellaneous Tasks

- Release v0.5.0 (#51)

## [0.4.0] - 2026-02-15

### Summary

This release mainly introduces variables support and some bug fixes.

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

### Miscellaneous Tasks

- Add pytest-cov as dev tool (#29)
- Update message for newly created file (#30)
- Release v0.4.0 (#37)

## [0.3.0] - 2026-01-31

### Summary

This release mainly introduces supports for de-duplication.

### Features

- Support de-duplication in task canonicalization (#27)

### Refactor

- Files with prepend policy does not require hash information (#25)

### Miscellaneous Tasks

- Make workflows more clear (#24)
- Release v0.3.0 (#28)

## [0.2.1] - 2026-01-25

### Summary

This release mainly introduces some bug fixes.

### Bug Fixes

- Prepend policy overwrite the original content of dest file (#20)

### Miscellaneous Tasks

- Fix permission of publish workflow (#19)
- Release v0.2.1 (#21)

## [0.2.0] - 2026-01-23

### Summary

This release mainly introduces better test suite.

### Refactor

- *(frontend)* [**breaking**] Remove .config/ structure assumption for source repository (#14)

### Testing

- Refactor task canonicalization tests with pyfakefs (#15)
- Complete most test suites (#17)

### Miscellaneous Tasks

- Update changelog body and processors in cliff.toml (#16)
- Release v0.2.0 (#18)

## [0.1.1] - 2026-01-15

### Summary

This release mainly introduces some bug fixes.

### Bug Fixes

- Hash inconsistency issue caused by newlines change (#12)

### Miscellaneous Tasks

- Release v0.1.1 (#13)

## [0.1.0] - 2026-01-15

### Summary

The first release, the start point.

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

### Miscellaneous Tasks

- Maintaince utility update (#1)
- Add workflows (#4)
- Release v0.1.0 (#9)

