"""Tests for backend utility functions."""

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from recnys.backend.utils import get_file_hash, prompt_for_confirmation

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


class TestGetFileHash:
    """Tests for get_file_hash function."""

    def test_hash_empty_file(self, fs: FakeFilesystem) -> None:
        """Test hashing an empty file."""
        file_path = Path("/tmp/empty.txt")
        fs.create_file(file_path)
        
        hash_value = get_file_hash(file_path)
        
        # Empty file SHA256 hash
        assert hash_value == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    def test_hash_file_with_content(self, fs: FakeFilesystem) -> None:
        """Test hashing a file with content."""
        content = "Hello, World!"
        file_path = Path("/tmp/test.txt")
        fs.create_file(file_path, contents=content)
        
        hash_value = get_file_hash(file_path)
        
        # Expected SHA256 hash for "Hello, World!"
        assert hash_value == "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"

    def test_hash_large_file(self, fs: FakeFilesystem) -> None:
        """Test hashing a large file (tests chunked reading)."""
        # Create content larger than the chunk size (8192 bytes)
        content = "x" * 10000
        file_path = Path("/tmp/large.txt")
        fs.create_file(file_path, contents=content)
        
        hash_value = get_file_hash(file_path)
        
        # Hash should be consistent
        assert len(hash_value) == 64  # SHA256 produces 64 hex characters
        assert isinstance(hash_value, str)

    def test_hash_consistency(self, fs: FakeFilesystem) -> None:
        """Test that hashing the same content produces the same hash."""
        content = "Test content for consistency"
        file1 = Path("/tmp/file1.txt")
        file2 = Path("/tmp/file2.txt")
        fs.create_file(file1, contents=content)
        fs.create_file(file2, contents=content)
        
        hash1 = get_file_hash(file1)
        hash2 = get_file_hash(file2)
        
        assert hash1 == hash2

    def test_hash_different_content(self, fs: FakeFilesystem) -> None:
        """Test that different content produces different hashes."""
        file1 = Path("/tmp/file1.txt")
        file2 = Path("/tmp/file2.txt")
        fs.create_file(file1, contents="Content A")
        fs.create_file(file2, contents="Content B")
        
        hash1 = get_file_hash(file1)
        hash2 = get_file_hash(file2)
        
        assert hash1 != hash2


class TestPromptForConfirmation:
    """Tests for prompt_for_confirmation function."""

    def test_confirm_with_empty_string(self) -> None:
        """Test confirmation with empty string as confirm signal."""
        with patch("builtins.input", return_value=""):
            result = prompt_for_confirmation("Confirm?", confirm_signals=("",))
        
        assert result is True

    def test_confirm_with_yes(self) -> None:
        """Test confirmation with 'yes' as confirm signal."""
        with patch("builtins.input", return_value="yes"):
            result = prompt_for_confirmation("Confirm?", confirm_signals=("yes", "y"))
        
        assert result is True

    def test_confirm_with_y(self) -> None:
        """Test confirmation with 'y' as confirm signal."""
        with patch("builtins.input", return_value="y"):
            result = prompt_for_confirmation("Confirm?", confirm_signals=("yes", "y"))
        
        assert result is True

    def test_decline_with_no(self) -> None:
        """Test declining with 'no'."""
        with patch("builtins.input", return_value="no"):
            result = prompt_for_confirmation("Confirm?", confirm_signals=("yes", "y"))
        
        assert result is False

    def test_decline_with_arbitrary_input(self) -> None:
        """Test declining with arbitrary input."""
        with patch("builtins.input", return_value="maybe"):
            result = prompt_for_confirmation("Confirm?", confirm_signals=("yes", "y"))
        
        assert result is False

    def test_case_insensitive(self) -> None:
        """Test that input is case-insensitive."""
        with patch("builtins.input", return_value="YES"):
            result = prompt_for_confirmation("Confirm?", confirm_signals=("yes",))
        
        assert result is True

    def test_whitespace_stripping(self) -> None:
        """Test that whitespace is stripped from input."""
        with patch("builtins.input", return_value="  yes  "):
            result = prompt_for_confirmation("Confirm?", confirm_signals=("yes",))
        
        assert result is True
