#!/usr/bin/env python3
"""
Microsoft Money mnyob99.dll Binary Patcher

This script applies Raymond Chen's patch to fix crashes in Microsoft Money
during import of account transactions or when changing a payee of a downloaded transaction.

The patch changes 4 bytes at specific file offsets:
- File offset 003FACE8: Change 85 to 8D
- File offset 003FACED: Change 50 to 51
- File offset 003FACF0: Change FF to 85
- File offset 003FACF6: Change E8 to B9

Reference: https://devblogs.microsoft.com/oldnewthing/20121113-00/?p=6103
"""

import os
import sys
import shutil
from pathlib import Path

# Patch definitions: (offset, original_byte, new_byte)
PATCHES = [
    (0x003FACE8, 0x85, 0x8D),
    (0x003FACED, 0x50, 0x51),
    (0x003FACF0, 0xFF, 0x85),
    (0x003FACF6, 0xE8, 0xB9)
]

def validate_file(file_path):
    """Validate that the file exists and is readable."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not os.access(file_path, os.R_OK | os.W_OK):
        raise PermissionError(f"Insufficient permissions to read/write: {file_path}")
    
    # Check file size (mnyob99.dll should be reasonably large)
    file_size = os.path.getsize(file_path)
    if file_size < 1000000:  # Less than 1MB is suspicious
        print(f"Warning: File size ({file_size} bytes) seems small for mnyob99.dll")

def verify_patches(file_path):
    """Verify if patches are needed by checking current byte values."""
    patches_needed = []
    patches_already_applied = []
    
    with open(file_path, 'rb') as f:
        for i, (offset, original_byte, new_byte) in enumerate(PATCHES):
            f.seek(offset)
            current_byte = f.read(1)[0]
            
            if current_byte == original_byte:
                patches_needed.append(i)
            elif current_byte == new_byte:
                patches_already_applied.append(i)
            else:
                print(f"Warning: Patch {i+1} - Unexpected byte at offset {hex(offset)}: "
                      f"found {hex(current_byte)}, expected {hex(original_byte)} or {hex(new_byte)}")
    
    return patches_needed, patches_already_applied

def create_backup(file_path):
    """Create a backup of the original file."""
    backup_path = file_path + ".backup"
    
    # If backup already exists, create numbered backup
    counter = 1
    while os.path.exists(backup_path):
        backup_path = f"{file_path}.backup.{counter}"
        counter += 1
    
    shutil.copy2(file_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path

def apply_patches(file_path, patches_to_apply):
    """Apply the binary patches to the file."""
    with open(file_path, 'r+b') as f:
        for patch_index in patches_to_apply:
            offset, original_byte, new_byte = PATCHES[patch_index]
            
            # Verify we're at the right location
            f.seek(offset)
            current_byte = f.read(1)[0]
            
            if current_byte != original_byte:
                print(f"Error: Patch {patch_index+1} failed verification. "
                      f"Expected {hex(original_byte)} at {hex(offset)}, found {hex(current_byte)}")
                return False
            
            # Apply the patch
            f.seek(offset)
            f.write(bytes([new_byte]))
            print(f"Patch {patch_index+1}: Changed byte at {hex(offset)} from {hex(original_byte)} to {hex(new_byte)}")
    
    return True

def find_money_dll():
    """Attempt to find the mnyob99.dll file in common locations."""
    common_paths = [
        r"C:\Program Files (x86)\Microsoft Money Plus\MNYCoreFiles\mnyob99.dll",
        r"C:\Program Files\Microsoft Money Plus\MNYCoreFiles\mnyob99.dll",
        r".\mnyob99.dll"  # Current directory
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None

def main():
    """Main function to orchestrate the patching process."""
    print("Microsoft Money mnyob99.dll Patcher")
    print("=" * 40)
    
    # Determine file path
    if len(sys.argv) > 1:
        dll_path = sys.argv[1]
    else:
        dll_path = find_money_dll()
        
        if not dll_path:
            print("Error: Could not find mnyob99.dll file.")
            print("Please specify the path to mnyob99.dll as a command line argument:")
            print(f"  python {sys.argv[0]} <path_to_mnyob99.dll>")
            print("\nCommon locations:")
            print("  C:\\Program Files (x86)\\Microsoft Money Plus\\MNYCoreFiles\\mnyob99.dll")
            print("  C:\\Program Files\\Microsoft Money Plus\\MNYCoreFiles\\mnyob99.dll")
            sys.exit(1)
    
    print(f"Target file: {dll_path}")
    
    try:
        # Validate the file
        validate_file(dll_path)
        
        # Check what patches are needed
        patches_needed, patches_applied = verify_patches(dll_path)
        
        if not patches_needed and not patches_applied:
            print("Warning: File doesn't match expected patterns. This may not be the correct mnyob99.dll file.")
            response = input("Continue anyway? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                sys.exit(0)
        
        if not patches_needed:
            print("All patches already applied! No changes needed.")
            sys.exit(0)
        
        if patches_applied:
            print(f"Found {len(patches_applied)} patches already applied.")
        
        print(f"Found {len(patches_needed)} patches that need to be applied.")
        
        # Confirm before proceeding
        print("\nThis will modify the mnyob99.dll file to fix Microsoft Money crashes.")
        response = input("Continue? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
        
        # Create backup
        backup_path = create_backup(dll_path)
        
        # Apply patches
        print(f"\nApplying {len(patches_needed)} patches...")
        success = apply_patches(dll_path, patches_needed)
        
        if success:
            print("\nPatching completed successfully!")
            print("The mnyob99.dll file has been patched to fix Microsoft Money crashes.")
            print(f"Original file backed up to: {backup_path}")
        else:
            print("\nPatching failed! Restoring backup...")
            shutil.copy2(backup_path, dll_path)
            print("Original file restored.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
