"""
EV Dashboard Diagnostic Tool
Run this to find out what's wrong with your setup
"""

import os
import sys

print("="*60)
print("🔍 EV DASHBOARD DIAGNOSTIC TOOL")
print("="*60)
print()

# Check 1: Current directory
print("📁 Step 1: Checking current directory...")
current_dir = os.getcwd()
print(f"   Current directory: {current_dir}")
print()

# Check 2: Files in current directory
print("📂 Step 2: Files in current directory...")
files = os.listdir('.')
print(f"   Found {len(files)} items:")
for f in files:
    if os.path.isfile(f):
        print(f"   ✓ FILE: {f}")
    else:
        print(f"   📁 FOLDER: {f}")
print()

# Check 3: app.py exists
print("📄 Step 3: Checking for app.py...")
if os.path.exists('app.py'):
    print("   ✅ app.py found!")
else:
    print("   ❌ app.py NOT found!")
    print("   ⚠️  You need to run this from the folder containing app.py")
print()

# Check 4: elt folder exists
print("📁 Step 4: Checking for elt folder...")
if os.path.exists('elt'):
    print("   ✅ elt folder found!")
    
    # Check etl contents
    print("\n   📂 Contents of elt folder:")
    etl_files = os.listdir('elt')
    required_files = ['__init__.py', 'column_mapper.py', 'data_cleaner.py', 'mysql_uploader.py']
    
    for req_file in required_files:
        if req_file in etl_files:
            # Check if file is empty
            file_path = os.path.join('etl', req_file)
            file_size = os.path.getsize(file_path)
            if file_size > 0:
                print(f"      ✅ {req_file} (size: {file_size} bytes)")
            else:
                print(f"      ⚠️  {req_file} (EMPTY FILE - This is a problem!)")
        else:
            print(f"      ❌ {req_file} (MISSING)")
    
    # Show any extra files
    extra_files = [f for f in etl_files if f not in required_files]
    if extra_files:
        print(f"\n   Extra files in elt: {extra_files}")
else:
    print("   ❌ elt folder NOT found!")
    print("   ⚠️  You need to create the elt folder")
print()

# Check 5: Try importing
print("🐍 Step 5: Testing Python imports...")
print("   Attempting to import ETL modules...")

try:
    # Add current directory to path
    sys.path.insert(0, current_dir)
    
    from elt.column_mapper import map_columns
    print("   ✅ Successfully imported map_columns")
except ImportError as e:
    print(f"   ❌ Failed to import map_columns")
    print(f"      Error: {e}")
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")

try:
    from elt.data_cleaner import clean_data
    print("   ✅ Successfully imported clean_data")
except ImportError as e:
    print(f"   ❌ Failed to import clean_data")
    print(f"      Error: {e}")
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")

try:
    from elt.mysql_uploader import upload_to_mysql
    print("   ✅ Successfully imported upload_to_mysql")
except ImportError as e:
    print(f"   ❌ Failed to import upload_to_mysql")
    print(f"      Error: {e}")
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")

print()
print("="*60)
print("📊 DIAGNOSIS SUMMARY")
print("="*60)

# Summary
issues = []
solutions = []

if not os.path.exists('app.py'):
    issues.append("app.py not found in current directory")
    solutions.append("Navigate to the folder containing app.py")

if not os.path.exists('etl'):
    issues.append("etl folder not found")
    solutions.append("Run: python setup.py (to create etl folder)")
else:
    required = ['__init__.py', 'column_mapper.py', 'data_cleaner.py', 'mysql_uploader.py']
    missing = [f for f in required if not os.path.exists(f'elt/{f}')]
    if missing:
        issues.append(f"Missing files in elt: {', '.join(missing)}")
        solutions.append("Run: python setup.py (to create missing files)")
    
    # Check for empty files
    for req_file in required:
        if os.path.exists(f'elt/{req_file}'):
            if os.path.getsize(f'elt/{req_file}') == 0:
                issues.append(f"elt/{req_file} is empty")
                solutions.append(f"Delete elt folder and run: python setup.py")

if not issues:
    print("✅ No issues found! Your setup looks good.")
    print()
    print("🎯 Next steps:")
    print("   1. Run: streamlit run app.py")
    print("   2. Upload your CSV file")
    print("   3. Click 'Save to Database'")
    print()
    print("   You should NOT see any warnings!")
else:
    print("⚠️  Found the following issues:")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    
    print()
    print("🔧 Recommended solutions:")
    for i, solution in enumerate(set(solutions), 1):
        print(f"   {i}. {solution}")

print()
print("="*60)
print("Need more help? Check these files:")
print("- SETUP_GUIDE.md")
print("- QUICKSTART.md")
print("="*60)