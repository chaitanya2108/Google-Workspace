"""
Setup verification script
Checks if everything is configured correctly
"""

import os
import sys
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_env_file():
    """Check if .env file exists and is configured"""
    if not Path('.env').exists():
        print("⚠️  .env file not found")
        print("   Create it by copying env.example: cp env.example .env")
        return False
    
    # Check required variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET']
    missing = []
    
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var).startswith('your-'):
            missing.append(var)
    
    if missing:
        print(f"⚠️  .env file exists but is not fully configured")
        print(f"   Missing or placeholder variables: {', '.join(missing)}")
        return False
    
    print("✅ .env file is configured")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import google.auth
        import flask_cors
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Install dependencies: pip install -r requirements.txt")
        return False

def check_directory_structure():
    """Check if required directories exist"""
    dirs = ['auth', 'routes']
    all_exist = True
    
    for dir_name in dirs:
        if not Path(dir_name).exists():
            print(f"❌ Directory missing: {dir_name}/")
            all_exist = False
    
    if all_exist:
        print("✅ Directory structure is correct")
    
    return all_exist

def check_files():
    """Check if required files exist"""
    required_files = [
        'app.py',
        'requirements.txt',
        'auth/auth_manager.py',
        'routes/account_routes.py',
        'routes/gmail_routes.py',
        'routes/calendar_routes.py',
        'routes/drive_routes.py',
        'routes/contacts_routes.py'
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return False
    
    print("✅ All required files are present")
    return True

def main():
    """Run all checks"""
    print("Google Workspace Flask API - Setup Check")
    print("=" * 40)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Directory Structure", check_directory_structure),
        ("Required Files", check_files),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_env_file),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            results.append(False)
            print()
    
    print("=" * 40)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All checks passed ({passed}/{total})")
        print("\nNext steps:")
        print("1. Make sure .env is configured with Google OAuth credentials")
        print("2. Run: python app.py")
        print("3. Visit: http://localhost:8080")
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("\nPlease fix the issues above before running the server")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

