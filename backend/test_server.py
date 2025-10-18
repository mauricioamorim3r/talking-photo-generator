"""
Quick test to verify server imports and database initialization
"""
import asyncio
import sys
import os

# Fix Windows console encoding
if sys.platform == "win32":
    os.system("chcp 65001 > nul")


async def test_database():
    """Test database initialization"""
    print("Testing database module...")
    try:
        from database import db
        await db.init_db()
        print("[OK] Database initialized successfully!")
        return True
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_imports():
    """Test all server imports"""
    print("\nTesting server imports...")
    try:
        import server
        print("[OK] Server imports successful!")
        return True
    except Exception as e:
        print(f"[ERROR] Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("=" * 50)
    print("Backend Server Test")
    print("=" * 50)

    db_ok = await test_database()
    imports_ok = await test_imports()

    print("\n" + "=" * 50)
    if db_ok and imports_ok:
        print("[OK] All tests passed! Server is ready.")
        print("=" * 50)
        print("\nTo start the server, run:")
        print("  uvicorn server:app --reload --port 8001")
        return 0
    else:
        print("[ERROR] Some tests failed. Check errors above.")
        print("=" * 50)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
