# Backend Architecture

**Migration Date:** 2025-01-22
**Pattern:** Feature-based (Vertical Slices)

## Structure

```
app/
├── catalog/              # Public fabric/color browsing
│   ├── router.py         # GET /catalog
│   ├── schemas.py        # Pydantic models
│   └── service.py        # Load from fabrics.json
│
├── generation/           # AI image generation
│   ├── router.py         # POST /generate, GET /jobs/{id}
│   ├── schemas.py        # Request/Response models
│   ├── models.py         # GenerationJob ORM
│   ├── generator.py      # SdxlTurboGenerator (main SDXL logic)
│   ├── generator_config.py    # Environment variables
│   ├── generator_mock.py      # MockGenerator (testing)
│   ├── storage.py        # LocalStorage, R2Storage
│   └── watermark.py      # Watermark application
│
├── admin/                # Admin management
│   ├── fabrics/          # Fabric CRUD
│   │   ├── fabrics_router.py
│   │   ├── colors_router.py
│   │   ├── models.py     # FabricFamily, Color ORM
│   │   └── schemas.py
│   ├── generations/      # Generation history
│   │   ├── router.py
│   │   └── schemas.py
│   ├── auth.py           # JWT authentication
│   └── dependencies.py   # FastAPI dependencies
│
├── core/                 # Shared infrastructure
│   ├── config.py         # Pydantic settings
│   └── database.py       # SQLAlchemy session
│
└── main.py               # FastAPI app initialization
```

## Key Changes

**Before (Layer-based):**
- `routers/` → All endpoints
- `models/` → All Pydantic schemas
- `services/` → All business logic (giant generator.py: 2100 lines)
- `admin/` → Mixed pattern

**After (Feature-based):**
- Each feature is self-contained in its own folder
- Related code stays together (router + schemas + logic)
- `generator.py` split into smaller, focused files

## Benefits

1. **Findability:** All catalog code in `catalog/`, all generation code in `generation/`
2. **Scalability:** Adding features = add new folder (no giant files)
3. **Maintainability:** Clear boundaries between features
4. **Consistency:** Same pattern across all modules

## Migration Notes

- **No breaking changes** to API endpoints
- All imports updated from old paths to new structure
- Old files kept temporarily for safety (can delete after testing)
