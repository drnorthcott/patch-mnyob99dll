# Money mnyob99.dll Binary Patcher

This script applies Raymond Chen's patch to fix crashes in Money Plus Sunset (mnyob99.dll) during import of account transactions or when changing a payee of a downloaded transaction. If you're like me, and you can read python, you can convince yourself what this script does and feel a lot better than downloading some sketchy binary from the internet. The script is provided as-is and without warranty, use at your own risk.

## Features
- Verifies the target DLL and checks if the patch is needed
- Creates a backup before modifying the file
- Applies 4 specific byte changes at known offsets
- Reports patch status and errors

## Usage

### Requirements
- Python 3.x
- Windows (tested on Windows 10/11)

### How to Run
1. Place `patch_money_dll.py` in the same directory as `mnyob99.dll` **or** note the full path to your DLL.
2. Open a command prompt or PowerShell.
3. Run:
   ```powershell
   python patch_money_dll.py <path_to_mnyob99.dll>
   ```
   If no path is provided, the script will search common install locations and the current directory.

## What It Does
- Checks if the DLL matches expected byte patterns
- Backs up the original DLL before patching
- Applies the following changes:
  - Offset `0x003FACE8`: `0x85` → `0x8D`
  - Offset `0x003FACED`: `0x50` → `0x51`
  - Offset `0x003FACF0`: `0xFF` → `0x85`
  - Offset `0x003FACF6`: `0xE8` → `0xB9`

## Reference
- [Raymond Chen's blog post](https://devblogs.microsoft.com/oldnewthing/20121113-00/?p=6103)

## Disclaimer
Use at your own risk. Always keep backups of important files. This script is provided as-is, without warranty.
