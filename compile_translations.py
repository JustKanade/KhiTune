#!/usr/bin/env python3
# coding:utf-8
"""
Compile Qt translation files (.ts) to binary format (.qm)
"""
import os
import subprocess
import sys
from pathlib import Path


def find_lrelease():
    """Find lrelease executable"""
    possible_paths = [
        Path(sys.prefix) / "Lib/site-packages/qt5_applications/Qt/bin/lrelease.exe",
        Path(sys.prefix) / "Lib/site-packages/PyQt5/Qt5/bin/lrelease.exe",
        "lrelease",
    ]
    
    for path in possible_paths:
        try:
            if isinstance(path, Path) and path.exists():
                return str(path)
            elif isinstance(path, str):
                result = subprocess.run([path, "-version"], capture_output=True)
                if result.returncode == 0:
                    return path
        except:
            continue
    
    return None


def compile_ts_files():
    """Compile all .ts files to .qm files"""
    lrelease = find_lrelease()
    
    if not lrelease:
        print("Error: 'lrelease' command not found")
        print("\nPlease install pyqt5-tools:")
        print("  pip install pyqt5-tools")
        return False
    
    print(f"Using lrelease: {lrelease}\n")
    
    i18n_dir = Path("app/resource/i18n")
    
    if not i18n_dir.exists():
        print(f"Error: Directory {i18n_dir} not found")
        return False
    
    ts_files = list(i18n_dir.glob("*.ts"))
    
    if not ts_files:
        print(f"No .ts files found in {i18n_dir}")
        return False
    
    print(f"Found {len(ts_files)} translation file(s)")
    
    success_count = 0
    for ts_file in ts_files:
        qm_file = ts_file.with_suffix(".qm")
        print(f"\nCompiling: {ts_file.name} -> {qm_file.name}")
        
        try:
            result = subprocess.run(
                [lrelease, str(ts_file), "-qm", str(qm_file)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                print(f"Success: {qm_file.name}")
                success_count += 1
            else:
                print(f"Failed: {result.stderr}")
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    print(f"\n{'='*50}")
    print(f"Compilation complete: {success_count}/{len(ts_files)} successful")
    return success_count == len(ts_files)


if __name__ == "__main__":
    success = compile_ts_files()
    sys.exit(0 if success else 1)

