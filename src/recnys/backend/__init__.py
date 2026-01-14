"""Responsible for refining and executing sync tasks, also maintaining sync states.

In backend, each sync task corresponds to a single file to be synchronized, which
is different from frontend where a sync task may involve multiple files.

Such a design simplifies the abstraction and implementation of sync logic in backend.
"""
