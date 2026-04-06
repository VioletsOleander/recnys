"""Contain modules related to parsing the scanned configuration data.

The parsing stage transforms the scanned configuration into `ParsedConfig`, performing deconfliction and
default value population.

The parsing stage does not involve any filesystem IO operations.
"""
