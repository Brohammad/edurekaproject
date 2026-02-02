# SQLite Compatibility Fix

## Issue
ChromaDB (used by langchain-chroma) requires SQLite 3.35+ but some Linux systems have older versions, causing import errors or runtime issues.

## Solution Applied

### 1. Installed pysqlite3-binary
```bash
./venv/bin/pip install pysqlite3-binary
```

### 2. Added SQLite Module Override in rag_pipeline.py
At the top of `rag_pipeline.py`, before any other imports:
```python
# Fix for SQLite version compatibility on Linux
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
```

This ensures ChromaDB uses the pysqlite3 binary instead of the system SQLite.

## Verification

✅ **Packages Installed:**
- chromadb: 1.4.1
- langchain-chroma: 1.1.0  
- pysqlite3-binary: 0.5.4

✅ **Import Test:**
```python
from langchain_chroma import Chroma  # Works correctly
```

✅ **Module Test:**
```python
import rag_pipeline  # Imports without errors
```

## Why This Works

The fix replaces Python's built-in `sqlite3` module with `pysqlite3` (which includes a newer SQLite binary) at runtime. This happens before ChromaDB tries to import sqlite3, ensuring it uses the compatible version.

## Alternative Solutions (Not Used)

1. **System SQLite Upgrade**: Requires root access and might break system dependencies
2. **Compile SQLite from source**: Complex and time-consuming
3. **Use different vector store**: Would require rewriting code

Our solution is clean, doesn't require root access, and doesn't change system libraries.

## Impact on Other Code

✅ No changes needed to other files
✅ The fix is isolated to rag_pipeline.py
✅ Works transparently for all ChromaDB operations
✅ Compatible with all upgraded features (history, logging, etc.)

## References

- ChromaDB SQLite requirements: https://docs.trychroma.com/troubleshooting#sqlite
- pysqlite3-binary package: https://pypi.org/project/pysqlite3-binary/
