# Admin UI Redesign - Luxury Experience Documentation

**Last Updated:** 2025-10-30
**Status:** Phase 1 Complete (Backend + Foundation), Phase 2 In Progress (UI Components)
**Design Inspiration:** [Harris & Frank](https://harrisandfrank.com) - Luxury menswear brand aesthetic

---

## 📋 Table of Contents

1. [Vision & Design Philosophy](#vision--design-philosophy)
2. [Backend Architecture](#backend-architecture)
3. [Frontend Design System](#frontend-design-system)
4. [Implementation Progress](#implementation-progress)
5. [API Reference](#api-reference)
6. [Component Specifications](#component-specifications)
7. [User Flows](#user-flows)
8. [Next Steps](#next-steps)

---

## Vision & Design Philosophy

### Design Goals
- **Image-First Approach**: Prioritize fabric swatch images over color hex codes
- **Luxury Brand Feel**: Sophisticated, elegant, minimalist aesthetic inspired by Harris & Frank
- **Intuitive Management**: Easy drag-drop color organization and status toggling
- **Tablet/Desktop Focus**: Responsive but optimized for larger screens
- **Professional Polish**: Generous white space, subtle animations, premium typography

### Key Principles
1. **Visual Hierarchy**: Large swatch images as primary content
2. **Minimal Friction**: Quick actions (toggle, move, delete) without excessive modals
3. **Elegant Motion**: Subtle 280ms transitions with cubic-bezier easing
4. **Neutral Sophistication**: Muted color palette (#1c1d1d, #f9f9f9) with strategic color accents
5. **Typographic Refinement**: Figtree (headers) + Jost (body) with elegant letter-spacing

### Harris & Frank Design Analysis

**Color Palette:**
- Primary Text: `#1c1d1d` (near-black)
- Background: `#f9f9f9` (soft white)
- Accents: `#222` (charcoal)
- Borders: `#e5e5e5` (subtle gray)

**Typography:**
- **Figtree 400/500/600** - Headers with 0.2em letter-spacing for elegant elongation
- **Jost 400/600** - Body text at 14px with 1.6 line-height for readability

**Layout:**
- Max-width: 1200px
- Column gaps: 64px (desktop)
- Card padding: 24px
- Border radius: 3px (sharp, not rounded)

**Interactions:**
- Hover elevation: `translateY(-3px)`
- Transition: `280ms cubic-bezier(0.2, 0.7, 0.2, 1)`
- Shadows: Subtle `0 4px 12px rgba(0,0,0,0.08)`

---

## Backend Architecture

### Database Schema Changes

**Migration:** `d5e8f4a3b2c9_add_color_status_and_timestamps.py`

#### New Fields Added:

**`colors` table:**
```sql
- status: VARCHAR NOT NULL DEFAULT 'active'  -- Individual color activation
- created_at: DATETIME NOT NULL DEFAULT NOW()
- updated_at: DATETIME NOT NULL DEFAULT NOW()
```

**`fabric_families` table:**
```sql
- created_at: DATETIME NOT NULL DEFAULT NOW()
- updated_at: DATETIME NOT NULL DEFAULT NOW()
```

**Indexes:**
```sql
CREATE INDEX ix_colors_status ON colors(status);
```

### API Architecture

**New Routers:**
1. `app/admin/colors_router.py` - Individual color management
2. `app/admin/generations_router.py` - Generated images gallery
3. `app/admin/router.py` - Enhanced fabric family management

**Key Improvements:**
- ✅ Fixed missing `/admin/fabrics/{id}/status` endpoint (was causing frontend errors)
- ✅ Added granular color control (move, toggle, delete)
- ✅ Generation job tracking with analytics
- ✅ Full CRUD for both families and individual colors

---

## Frontend Design System

### Typography System

**Font Configuration:** `src/lib/fonts.ts`

```typescript
import { Figtree, Jost } from "next/font/google";

// Headers - Elegant with letter-spacing
export const figtree = Figtree({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-figtree",
});

// Body - Refined readability
export const jost = Jost({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-jost",
});
```

**Usage:**
```tsx
<h1 className="font-header tracking-[0.2em]">Familias de Telas</h1>
<p className="font-body">Body text with refined readability</p>
```

### Color System

**CSS Custom Properties:** `src/app/globals.css`

```css
:root {
  /* Primary Colors */
  --color-dark: #1c1d1d;           /* Text */
  --color-charcoal: #222222;       /* Accents */
  --color-bg-light: #f9f9f9;       /* Background */
  --color-white: #ffffff;
  --color-border: #e5e5e5;

  /* Status Colors */
  --color-active: #10b981;         /* Green */
  --color-inactive: #6b7280;       /* Gray */
  --color-danger: #ef4444;         /* Red */

  /* Shadows */
  --shadow-subtle: 0 1px 3px rgba(0,0,0,0.08);
  --shadow-elevated: 0 4px 12px rgba(0,0,0,0.08);

  /* Transitions */
  --transition-smooth: transform 0.28s cubic-bezier(0.2, 0.7, 0.2, 1);
}
```

### Layout System

**Grid Structure:**
```css
.admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Responsive Breakpoints */
/* Mobile: 1 column (default) */
/* Tablet: 2 columns @ 768px */
/* Desktop: 3 columns @ 1024px */
```

### Component Patterns

**Luxury Button:**
```css
.btn-luxury {
  background: var(--color-dark);
  color: var(--color-white);
  padding: 12px 24px;
  border-radius: 3px;
  transition: var(--transition-smooth);
}

.btn-luxury:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-elevated);
}
```

**Card Style:**
```css
.luxury-card {
  background: white;
  padding: 24px;
  border-radius: 3px;
  box-shadow: var(--shadow-subtle);
  transition: var(--transition-smooth);
}

.luxury-card:hover {
  box-shadow: var(--shadow-elevated);
}
```

---

## Implementation Progress

### ✅ Phase 1: Backend Foundation (100%)

**Database & Models:**
- [x] Migration for color status and timestamps
- [x] Updated `FabricFamily` model with timestamps
- [x] Updated `Color` model with status + timestamps
- [x] Created `GenerationJobRead` schema

**API Endpoints:**
- [x] Fixed `/admin/fabrics/{id}/status` (PATCH)
- [x] `/admin/colors` (GET) - List/search colors
- [x] `/admin/colors/{id}` (PATCH) - Update color
- [x] `/admin/colors/{id}/status` (PATCH) - Toggle status
- [x] `/admin/colors/{id}/move` (POST) - Move between families
- [x] `/admin/generations` (GET) - List generation jobs
- [x] `/admin/generations/stats` (GET) - Analytics
- [x] `/admin/generations/by-fabric/{family}/{color}` (GET)

**Commit:** `b2c087b` - "feat: enhance admin API with color management and generation tracking"

### ✅ Phase 2: Frontend Foundation (90%)

**Type System:**
- [x] Updated `ColorRead` with status, timestamps, fabric_family_id
- [x] Created `ColorUpdate` type for PATCH operations
- [x] Created `GenerationJobRead` type
- [x] Updated `FabricRead` with timestamps

**API Client:**
- [x] Added `listColors()` with filters
- [x] Added `setColorStatus()`
- [x] Added `moveColorToFamily()`
- [x] Added `listGenerations()`, `getGenerationStats()`
- [x] Extended `adminApi.ts` with all new endpoints

**Design System:**
- [x] Configured Figtree & Jost fonts via next/font
- [x] Updated root layout with luxury fonts
- [x] Created comprehensive CSS custom properties
- [x] Defined luxury component styles (.btn-luxury, etc.)

### 🚧 Phase 3: UI Components (0%)

**Planned Components:**
- [ ] `StatusToggle.tsx` - iOS-style switch
- [ ] `FabricCard.tsx` - Image-first card with fallback
- [ ] `ColorCard.tsx` - Swatch preview with quick actions
- [ ] `LuxuryButton.tsx` - Primary/secondary variants
- [ ] `SearchBar.tsx` - Elegant search with icon
- [ ] `MoveColorModal.tsx` - Drag-drop interface
- [ ] `ImageGallery.tsx` - Masonry grid for generations

### 🚧 Phase 4: Admin Pages (0%)

**Planned Pages:**
- [ ] `/admin` - Main navigation with tabs
- [ ] `/admin/fabrics` - Redesigned with image-first cards
- [ ] `/admin/generations` - Generated images gallery

---

## API Reference

### Fabric Family Endpoints

**List Fabrics:**
```http
GET /admin/fabrics?q=search&status_filter=active&limit=50
Response: FabricRead[]
```

**Toggle Fabric Status:**
```http
PATCH /admin/fabrics/{id}/status
Body: { "status": "active" | "inactive" }
Response: FabricRead
```

### Color Management Endpoints

**List Colors (Cross-Family):**
```http
GET /admin/colors?q=095T-0121&family_id=azules&status_filter=active
Response: ColorRead[]
```

**Update Color:**
```http
PATCH /admin/colors/{id}
Body: ColorUpdate (partial)
Response: ColorRead
```

**Toggle Color Status:**
```http
PATCH /admin/colors/{id}/status
Body: { "status": "active" | "inactive" }
Response: ColorRead
```

**Move Color to Different Family:**
```http
POST /admin/colors/{id}/move
Body: { "fabric_family_id": 123 }
Response: ColorRead
```

### Generated Images Endpoints

**List Generations:**
```http
GET /admin/generations?family_id=azules&color_id=az-095T-0121&status_filter=completed
Response: GenerationJobRead[]
```

**Get Analytics:**
```http
GET /admin/generations/stats
Response: {
  total_generations: number,
  by_status: { completed: 42, failed: 3, ... },
  by_family: [{ family_id: "azules", count: 18 }, ...],
  last_24_hours: number
}
```

**Get Images for Specific Fabric:**
```http
GET /admin/generations/by-fabric/{family_id}/{color_id}?limit=20
Response: GenerationJobRead[]
```

---

## Component Specifications

### StatusToggle Component

**Design:**
- iOS-style animated switch
- Green (active) / Gray (inactive)
- Label: "Activo" / "Inactivo"
- Smooth transition (150ms)

**Props:**
```typescript
interface StatusToggleProps {
  value: "active" | "inactive";
  onChange: (status: "active" | "inactive") => void;
  disabled?: boolean;
  label?: string;
}
```

**Visual States:**
- Active: Green background (#10b981), white circle on right
- Inactive: Gray background (#6b7280), white circle on left
- Hover: Slight brightness increase
- Disabled: Opacity 0.5, no hover effects

### FabricCard Component

**Design:**
- White card with subtle shadow
- 4:3 aspect ratio image container
- Image-first with color hex fallback
- Overlay with family name on hover
- Status badge (top-right corner)
- Quick actions dropdown (bottom)

**Layout:**
```
┌─────────────────────┐
│  [Status Badge]     │
│                     │
│   [Swatch Image]    │
│   or Color Hex      │
│                     │
│─────────────────────│
│ Family Name         │
│ X colors            │
│ [Actions ⋮]         │
└─────────────────────┘
```

**Props:**
```typescript
interface FabricCardProps {
  fabric: FabricRead;
  onStatusToggle: (id: number) => void;
  onEdit: (fabric: FabricRead) => void;
  onDelete: (id: number) => void;
}
```

### ImageGallery Component

**Design:**
- Masonry grid (Pinterest-style)
- Lazy loading with intersection observer
- Lightbox modal on click
- Filter bar at top
- Infinite scroll or "Load More" button

**Grid Behavior:**
- 4 columns @ 1200px+
- 3 columns @ 992px-1199px
- 2 columns @ 768px-991px
- 1 column @ <768px

---

## User Flows

### Flow 1: Toggle Fabric Family Status

1. Admin views fabric families grid
2. Clicks status toggle switch on card
3. Switch animates from green→gray (or vice versa)
4. API call: `PATCH /admin/fabrics/{id}/status`
5. Card updates without page reload
6. Success toast notification (optional)

**Implementation:**
```typescript
const handleToggle = async (fabricId: number) => {
  const newStatus = fabric.status === "active" ? "inactive" : "active";
  await setFabricStatus(fabricId, newStatus);
  refetch(); // Refresh data
};
```

### Flow 2: Move Color Between Families

1. Admin drags color card to different family section
2. Drop zone highlights on hover
3. Confirmation modal: "Move 095T-0121 from Azules to Grises?"
4. User confirms
5. API call: `POST /admin/colors/{id}/move`
6. Color card animates to new position
7. Both family cards update color counts

**Alternative (No Drag-Drop):**
1. Click "Move" button on color card
2. Dropdown shows available families
3. Select target family
4. API call executed
5. UI updates

### Flow 3: View Generated Images

1. Admin clicks "Ver Imágenes Generadas" button
2. Navigate to `/admin/generations`
3. See analytics cards at top (total, by family, recent)
4. Masonry grid loads with filters
5. Filter by family/color/date
6. Click image → Lightbox with metadata
7. Option to delete generation

---

## Next Steps

### Immediate (Week 1)

1. **Create Core Components** (`frontend/src/components/admin/`):
   ```
   StatusToggle.tsx
   FabricCard.tsx
   ColorCard.tsx
   LuxuryButton.tsx
   SearchBar.tsx
   ```

2. **Redesign Admin Fabrics Page** (`frontend/src/app/admin/page.tsx`):
   - Replace table with card grid
   - Add status toggles
   - Implement search with luxury styling

3. **Build Generated Images Gallery** (`frontend/src/app/admin/generations/page.tsx`):
   - Analytics dashboard
   - Masonry grid
   - Lightbox modal

### Short-term (Week 2)

4. **Add Drag-Drop Color Management**:
   - Install `@dnd-kit/core`
   - Implement drag handlers
   - Create drop zones
   - Add visual feedback

5. **Enhance Interactions**:
   - Loading skeletons
   - Toast notifications
   - Confirmation modals
   - Error boundaries

6. **Polish & Responsive**:
   - Test on tablet/desktop
   - Add keyboard shortcuts (Escape, Enter)
   - Performance optimization
   - Accessibility audit

### Long-term (Month 1)

7. **Advanced Features**:
   - Bulk operations (select multiple → move/toggle)
   - Export catalog data
   - Color organization analytics
   - Generation usage trends

8. **Deploy & Test**:
   - Run database migration on production
   - Deploy frontend to Vercel
   - User acceptance testing
   - Gather feedback

---

## Technical Decisions

### Why Image-First?

**Problem:** Previous UI relied on hex color chips, which don't represent fabric textures, patterns, or true appearance.

**Solution:** Display actual R2 swatch images with color hex as fallback only.

**Benefits:**
- Visual accuracy for fabrics with patterns/textures
- Faster recognition by sales staff
- More professional appearance
- Better matches customer experience

### Why No Separate Colors Page?

**Decision:** Manage colors inline within fabric family cards using expand/collapse.

**Rationale:**
- Reduces navigation complexity
- Keeps context (which family a color belongs to) visible
- Drag-drop between families is more intuitive
- Follows e-commerce admin patterns (Shopify, etc.)

### Why Luxury Aesthetic?

**Goal:** Match Harris & Frank brand identity.

**Execution:**
- Premium typography (Figtree + Jost)
- Muted neutral palette
- Generous white space
- Subtle animations
- Sharp borders (3px, not rounded)

**Result:** Admin panel feels like extension of brand, not generic CRUD interface.

---

## File Structure

### Backend
```
backend/
├── alembic/versions/
│   └── d5e8f4a3b2c9_add_color_status_and_timestamps.py
├── app/admin/
│   ├── models.py                    # Updated with timestamps
│   ├── schemas.py                   # New schemas (ColorUpdate, GenerationJobRead)
│   ├── router.py                    # Fixed /status endpoint
│   ├── colors_router.py             # NEW: Color management
│   └── generations_router.py        # NEW: Image gallery
└── app/main.py                      # Registered new routers
```

### Frontend
```
frontend/src/
├── lib/
│   ├── fonts.ts                     # NEW: Luxury fonts config
│   └── adminApi.ts                  # Extended with new endpoints
├── types/
│   └── admin.ts                     # Updated types
├── app/
│   ├── layout.tsx                   # Updated with luxury fonts
│   ├── globals.css                  # NEW: Design system
│   └── admin/
│       ├── page.tsx                 # TO BE REDESIGNED
│       ├── generations/
│       │   └── page.tsx             # TO BE CREATED
│       └── components/              # TO BE CREATED
│           ├── StatusToggle.tsx
│           ├── FabricCard.tsx
│           └── ImageGallery.tsx
```

---

## Resources

### Design Inspiration
- **Harris & Frank Website:** https://harrisandfrank.com
  - Color palette analysis
  - Typography reference
  - Layout patterns
  - Interaction design

### Technical References
- **Next.js 15:** https://nextjs.org/docs
- **Tailwind CSS:** https://tailwindcss.com/docs
- **React 19:** https://react.dev
- **FastAPI:** https://fastapi.tiangolo.com

### Design Tools
- **Figma** - UI mockups (optional)
- **ColorHunt** - Palette refinement
- **Google Fonts** - Figtree & Jost specimens

---

## Changelog

### 2025-10-30 - Phase 1 Complete
- ✅ Created database migration with color status & timestamps
- ✅ Implemented 3 new API routers (fabrics, colors, generations)
- ✅ Fixed missing `/admin/fabrics/{id}/status` endpoint
- ✅ Added 12 new API endpoints for comprehensive admin control
- ✅ Configured luxury fonts (Figtree + Jost)
- ✅ Created design system with CSS custom properties
- ✅ Extended frontend types and API client
- 📝 Documented design philosophy and implementation plan

### Next Release (TBD)
- 🚧 Create StatusToggle component
- 🚧 Redesign fabric families page
- 🚧 Build generated images gallery

---

**Maintainers:** Development Team
**Questions:** Refer to this document or check git commit history
**Status:** Phase 1 backend complete, Phase 2 frontend foundation ready for UI implementation
