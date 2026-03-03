#!/usr/bin/env python3
"""
Import Check Script

Verify all imports are correct in the scaffold.
"""

import os
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def check_imports():
    """Check if all imports can be resolved"""

    checks = []

    # Check repository imports
    try:
        from repositories import (
            BaseRepository,
            VectorRepository,
            SessionRepository,
            QdrantRepository,
            WeaviateRepository,
            PineconeRepository
        )
        checks.append(("repositories", "OK"))
    except ImportError as e:
        checks.append(("repositories", f"FAIL: {e}"))

    # Check service imports
    try:
        from services import ChatService, DocumentService, SessionService
        checks.append(("services", "OK"))
    except ImportError as e:
        checks.append(("services", f"FAIL: {e}"))

    # Check parser imports
    try:
        from parsers import (
            BaseDocumentParser,
            PDFParser,
            MarkdownParser,
            WordParser,
            TextParser
        )
        checks.append(("parsers", "OK"))
    except ImportError as e:
        checks.append(("parsers", f"FAIL: {e}"))

    # Check tool imports
    try:
        from tools import vector_search, search
        checks.append(("tools", "OK"))
    except ImportError as e:
        checks.append(("tools", f"FAIL: {e}"))

    # Check config imports
    try:
        from core.config import settings
        checks.append(("core.config", "OK"))
    except ImportError as e:
        checks.append(("core.config", f"FAIL: {e}"))

    # Print results
    print("\nImport Check Results:")
    print("=" * 50)
    for name, status in checks:
        print(f"{name:.<30} {status}")
    print("=" * 50)

    # Return exit code
    return all("OK" in status for _, status in checks)


if __name__ == "__main__":
    success = check_imports()
    sys.exit(0 if success else 1)
