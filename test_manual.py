#!/usr/bin/env python3
"""Manual test for empty dest bug fix."""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from recnys.canonicalize.canonicalizer import ConfigCanonicalizer


def test_empty_dest_bug():
    """Test the bug case from the issue."""
    
    # Create a temp directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create test files
        test_files = [
            "nushell/third_party/file1.txt",
            "nushell/third_party/subdir/file2.txt",
            "nushell/third_party/nu_scripts/custom-completions/git/git-completions.nu",
        ]
        
        for file in test_files:
            file_path = tmpdir_path / file
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("test content")
        
        # Change to temp directory
        import os
        old_cwd = os.getcwd()
        os.chdir(tmpdir_path)
        
        try:
            # Create the config that reproduces the bug
            loaded_config = {
                "nushell/third_party/": {"dest": {"Windows": "", "Linux": ""}},
                "nushell/third_party/nu_scripts/custom-completions/git/git-completions.nu": None,
            }
            
            # Create canonicalizer
            rendered_dir = tmpdir_path / ".rendered"
            rendered_dir.mkdir()
            canonicalizer = ConfigCanonicalizer(rendered_file_dir=rendered_dir)
            
            # Canonicalize
            result = canonicalizer.canonicalize(loaded_config=loaded_config)
            
            # Check results
            print("Canonical config keys:")
            for key in result.keys():
                print(f"  - {key}")
                print(f"    dst: {result[key].sync_spec.dst}")
            
            # Verify the explicit file is NOT in the result
            explicit_file = "nushell/third_party/nu_scripts/custom-completions/git/git-completions.nu"
            if explicit_file in result:
                print(f"\n❌ FAIL: Explicit file '{explicit_file}' should not be in result")
                return False
            
            # Verify all files in result have dst=None
            for key, value in result.items():
                if value.sync_spec.dst is not None:
                    print(f"\n❌ FAIL: File '{key}' should have dst=None but got {value.sync_spec.dst}")
                    return False
            
            print("\n✅ PASS: Empty dest specification is correctly respected")
            return True
            
        finally:
            os.chdir(old_cwd)


if __name__ == "__main__":
    success = test_empty_dest_bug()
    sys.exit(0 if success else 1)
