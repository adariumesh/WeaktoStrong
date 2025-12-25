# Deprecated Files Archive - December 2025

## Purpose
This directory contains legacy/orphaned files that were safely removed during the codebase cleanup on December 24, 2025.

⚠️ **SAFE TO DELETE**: These files were confirmed to be unused by the active codebase.

## Archived Files

### 1. `legacy_backend/` (Originally `/backend/`)
**Reason**: Duplicate/legacy backend directory
- **Evidence**: Not referenced by docker-compose.yml or package.json scripts
- **Size**: 27 lines in main.py vs 284 lines in active backend
- **Content**: Basic FastAPI skeleton only
- **Active Backend**: `/weak-to-strong/backend/` (full implementation)

### 2. `test_docker_sandbox.py`
**Reason**: Loose test file outside organized test structure
- **Evidence**: Located in project root, not in `/backend/tests/`
- **Purpose**: Development/debugging script

### 3. `test_data_runner.py` 
**Reason**: Loose test file outside organized test structure
- **Evidence**: Located in project root, not in `/backend/tests/`
- **Purpose**: Development/debugging script

### 4. `verify_system.py`
**Reason**: Loose verification script
- **Evidence**: Development utility, not part of main codebase
- **Purpose**: System verification script

## Audit Trail

**Date**: December 24, 2025  
**Method**: Safe `mv` commands (no `rm` used)  
**Auditor**: Claude Code Assistant  
**Verification**: All files confirmed unused via grep and dependency analysis  

## Recovery Instructions

If any file is needed:
```bash
# Move back to original location
mv _deprecated_2025_archive/legacy_backend /backend
mv _deprecated_2025_archive/test_docker_sandbox.py weak-to-strong/
mv _deprecated_2025_archive/test_data_runner.py weak-to-strong/  
mv _deprecated_2025_archive/verify_system.py weak-to-strong/
```

## Cleanup Status

✅ **ACTIVE CODEBASE VERIFIED**: All references point to `/weak-to-strong/backend/`  
✅ **NO IMPORTS BROKEN**: grep confirmed no cross-dependencies  
✅ **DOCKER CONFIGS INTACT**: docker-compose.yml points to correct backend  
✅ **BUILD SCRIPTS INTACT**: package.json scripts point to correct backend  

Safe to delete this entire directory after 30 days if no issues arise.