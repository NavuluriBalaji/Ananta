#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixed GPT Engineer Runner - Handles Unicode and execution issues
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_comprehensive_env():
    """Set comprehensive environment to fix all encoding and gRPC issues"""
    # UTF-8 encoding fixes
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    
    # Console encoding fix for Windows
    try:
        subprocess.run(['chcp', '65001'], shell=True, capture_output=True, check=False)
    except:
        pass
    
    # Comprehensive gRPC fixes
    os.environ['GRPC_VERBOSITY'] = 'ERROR'
    os.environ['GRPC_TRACE'] = ''
    os.environ['GRPC_KEEPALIVE_TIME_MS'] = '30000'
    os.environ['GRPC_KEEPALIVE_TIMEOUT_MS'] = '10000'
    os.environ['GRPC_HTTP2_MAX_PINGS_WITHOUT_DATA'] = '0'
    os.environ['GRPC_HTTP2_MIN_PING_INTERVAL_WITHOUT_DATA_MS'] = '300000'
    os.environ['GRPC_SO_REUSEPORT'] = '0'
    os.environ['GRPC_POLL_STRATEGY'] = 'poll'
    
    # Disable problematic features
    os.environ['DISABLE_SYSINFO'] = '1'
    
    # Load API key from .env
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")

def run_with_subprocess_fallback(project_path):
    """Run via subprocess to completely isolate encoding issues"""
    try:
        # Create a minimal Python script to run
        script_content = f'''
import os
import sys
sys.path.insert(0, ".")

# Set up environment
os.environ["PYTHONIOENCODING"] = "utf-8" 
os.environ["PYTHONUTF8"] = "1"
os.environ["GRPC_VERBOSITY"] = "ERROR"

# Load .env
try:
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip().strip('"').strip("'")
except:
    pass

# Import and run
from gpt_engineer.applications.cli.main import app
sys.argv = ["gpte", "{project_path}", "--model", "gemini-2.0-flash", "--no_execution"]
app()
'''
        
        # Write temporary script
        temp_script = Path(__file__).parent / "temp_runner.py"
        with open(temp_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Run subprocess
        env = os.environ.copy()
        env.update({
            'PYTHONIOENCODING': 'utf-8',
            'PYTHONUTF8': '1',
            'GRPC_VERBOSITY': 'ERROR'
        })
        
        print("🔄 Running via subprocess to avoid encoding issues...")
        result = subprocess.run([sys.executable, str(temp_script)], 
                              env=env, cwd=Path(__file__).parent)
        
        # Cleanup
        try:
            temp_script.unlink()
        except:
            pass
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Subprocess method failed: {e}")
        return 1

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_simple.py <project_path>")
        print("Example: python run_simple.py analysis")
        return 1
    
    project_path = sys.argv[1]
    
    setup_comprehensive_env()
    
    # Check API key
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: No Gemini API key found in .env file")
        return 1
    
    print(f"🚀 Running GPT Engineer on: {project_path}")
    print("🔧 Using comprehensive encoding and gRPC fixes...")
    
    # Add current directory to Python path
    sys.path.insert(0, str(Path(__file__).parent))
    
    # Try direct method first, then fallback to subprocess
    try:
        print("📝 Attempting direct generation...")
        
        # Direct import and run
        from gpt_engineer.applications.cli.main import app
        
        # Generate code without execution to avoid Unicode issues
        sys.argv = ['gpte', project_path, '--model', 'gemini-2.0-flash', '--no_execution']
        
        # Run the CLI app
        app()
        
        print("✅ Code generation completed successfully!")
        print(f"📁 Generated files are in: {project_path}/")
        print("\n🔧 To run the generated code manually:")
        print(f"   cd {project_path}")
        print("   npm install")
        print("   npm start")
        return 0
        
    except UnicodeEncodeError as e:
        print(f"🔄 Unicode error detected: {e}")
        print("🔄 Switching to subprocess method...")
        return run_with_subprocess_fallback(project_path)
        
    except Exception as e:
        error_msg = str(e).lower()
        if 'grpc' in error_msg or 'timeout' in error_msg:
            print(f"⚠️  gRPC error: {e}")
            print("🔄 Trying subprocess method...")
            return run_with_subprocess_fallback(project_path)
        else:
            print(f"❌ Error: {e}")
            return 1

if __name__ == "__main__":
    exit_code = main()
    if exit_code == 0:
        print("\n🎉 Process completed successfully!")
    else:
        print("\n❌ Process failed. Check your API key and internet connection.")
    sys.exit(exit_code)
