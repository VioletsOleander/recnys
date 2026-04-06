"""Contain modules related to canonicalizing the parsed configuration data.

The canonicalization stage transforms the parsed configuration into `CanonicalConfig`, performing

- Path construction: Constructing absolute paths for source and destination paths.
- Directory expansion: Expanding directory entries with copy policy into file entries.
"""
