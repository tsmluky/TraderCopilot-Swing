import sys
import os
import traceback

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

print("🚀 Starting Dry Run Import Test...")

try:
    # Attempt to import main
    # This triggers all top-level imports in main.py and its dependencies
    import main

    print("✅ Successfully imported 'main'")

    # Check if app exists
    if hasattr(main, "app"):
        print("✅ 'app' object found in main")
    else:
        print("⚠️ 'app' object NOT found in main (Check main.py structure)")

except ImportError as e:
    print(f"\n❌ IMPORT ERROR detected: {e}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n❌ RUNTIME ERROR during import: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 Dry Run Passed! The application should start correctly on Railway.")
