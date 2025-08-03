#!/usr/bin/env python3
"""
GPT Engineer Cleanup Script
Removes documentation, examples, and unnecessary files while preserving core functionality
"""

import os
import shutil
import sys
from pathlib import Path

def cleanup_gpt_engineer():
    """Remove unnecessary files and folders from GPT Engineer"""
    
    # Get the base directory
    base_dir = Path(__file__).parent
    print(f"🧹 Cleaning up GPT Engineer in: {base_dir}")
    
    # Files to remove (documentation, configuration, etc.)
    files_to_remove = [
        # Documentation files
        "README.md",
        "README_GEMINI.md", 
        "WINDOWS_README.md",
        "ROADMAP.md",
        "Acknowledgements.md",
        "DISCLAIMER.md",
        "GOVERNANCE.md",
        "TERMS_OF_USE.md",
        "GEMINI_README.md",
        
        # Configuration files for development
        ".pre-commit-config.yaml",
        ".readthedocs.yaml",
        "citation.cff",
        "sweep.yaml",
        "tox.ini",
        "Makefile",
        
        # Docker files (if you don't need them)
        "docker-compose.yml",
        ".dockerignore",
        
        # Test and development files
        "test_gemini_integration.py",
        
        # Diagram files
        "gpt_engineer_complete_flow.mmd",
        "gpt_engineer_improvements.mmd",
        
        # Multiple env templates (keep only one)
        ".env.example",
        ".env.local", 
        ".env.template",
        ".env.windows",
    ]
    
    # Directories to remove
    dirs_to_remove = [
        "docs",           # Documentation
        ".github",        # GitHub workflows
        "docker",         # Docker files
        "scripts",        # Development scripts
        "tests",          # Test files
        "projects/example",         # Example projects
        "projects/example-improve", 
        "projects/example-vision",
        "projects/lovable-competitor",
        "projects/project_20250802_183443",
        "projects/SAMPLETEST",
        "projects/test_runnable",
    ]
    
    # Files to keep (essential files)
    essential_files = [
        "pyproject.toml",
        "poetry.lock",
        "LICENSE",
        "MANIFEST.in",
        ".gitignore",
        ".env",
        ".env.gemini",
        "run_gemini_safe.py",
        "run_gemini.bat", 
        "run_with_gemini.py",
        "run_any_file.py",
    ]
    
    # Directories to keep (core functionality)
    essential_dirs = [
        "gpt_engineer",   # Core package
        "analysis",       # Your project
        ".gpteng",        # Generated metadata
    ]
    
    removed_files = []
    removed_dirs = []
    kept_files = []
    errors = []
    
    # Remove files
    for file_name in files_to_remove:
        file_path = base_dir / file_name
        if file_path.exists():
            try:
                file_path.unlink()
                removed_files.append(file_name)
                print(f"🗑️  Removed file: {file_name}")
            except Exception as e:
                errors.append(f"Failed to remove {file_name}: {e}")
                print(f"❌ Error removing {file_name}: {e}")
    
    # Remove directories
    for dir_name in dirs_to_remove:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                removed_dirs.append(dir_name)
                print(f"🗑️  Removed directory: {dir_name}")
            except Exception as e:
                errors.append(f"Failed to remove {dir_name}: {e}")
                print(f"❌ Error removing {dir_name}: {e}")
    
    # Clean up projects directory (remove examples but keep structure)
    projects_dir = base_dir / "projects"
    if projects_dir.exists():
        for item in projects_dir.iterdir():
            if item.is_dir() and item.name != "analysis":  # Keep only analysis
                try:
                    shutil.rmtree(item)
                    removed_dirs.append(f"projects/{item.name}")
                    print(f"🗑️  Removed example project: projects/{item.name}")
                except Exception as e:
                    errors.append(f"Failed to remove projects/{item.name}: {e}")
    
    # Count remaining essential files
    for file_name in essential_files:
        file_path = base_dir / file_name
        if file_path.exists():
            kept_files.append(file_name)
    
    # Clean up __pycache__ directories
    print("🧹 Cleaning __pycache__ directories...")
    for root, dirs, files in os.walk(base_dir):
        if '__pycache__' in dirs:
            pycache_path = Path(root) / '__pycache__'
            try:
                shutil.rmtree(pycache_path)
                print(f"🗑️  Removed: {pycache_path.relative_to(base_dir)}")
            except Exception as e:
                print(f"❌ Error removing {pycache_path}: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("🎉 CLEANUP SUMMARY")
    print("="*50)
    print(f"📁 Removed {len(removed_dirs)} directories")
    print(f"📄 Removed {len(removed_files)} files")
    print(f"✅ Kept {len(kept_files)} essential files")
    print(f"❌ {len(errors)} errors occurred")
    
    if errors:
        print("\n⚠️  ERRORS:")
        for error in errors:
            print(f"   {error}")
    
    print(f"\n📊 Estimated space saved: Removed documentation, examples, and dev files")
    print(f"🔧 Core GPT Engineer functionality preserved")
    print(f"🚀 Your analysis project is safe in: projects/analysis/")
    
    return len(errors) == 0

if __name__ == "__main__":
    print("GPT Engineer Cleanup Tool")
    print("=" * 40)
    print("This will remove:")
    print("- Documentation files (README, docs/)")
    print("- Example projects") 
    print("- Development tools (tests, scripts)")
    print("- Docker files")
    print("- GitHub workflows")
    print("")
    print("This will KEEP:")
    print("- Core gpt_engineer package")
    print("- Your analysis project")
    print("- Essential configuration files")
    print("- Gemini runner scripts")
    print("")
    
    response = input("Continue with cleanup? (y/N): ").lower().strip()
    
    if response in ['y', 'yes']:
        success = cleanup_gpt_engineer()
        if success:
            print("\n✅ Cleanup completed successfully!")
        else:
            print("\n⚠️  Cleanup completed with some errors.")
        sys.exit(0 if success else 1)
    else:
        print("❌ Cleanup cancelled.")
        sys.exit(0)
