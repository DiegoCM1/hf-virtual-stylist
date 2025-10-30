# Harris & Frank Virtual Stylist - Frontend

## Project Overview

The Harris & Frank Virtual Stylist is an AI-powered digital suit styling and visualization application for a luxury menswear brand. This Next.js 15 application provides an interactive, mobile-friendly interface that allows customers and sales associates to visualize suits in different fabrics and colors using AI-generated photorealistic images.

**Design Philosophy:**
Inspired by the Harris & Frank website aesthetic, the application follows a minimalist luxury design system featuring:
- Soft white backgrounds (#f9f9f9)
- Near-black text (#1c1d1d)
- Sharp border radius (3px)
- Generous whitespace
- Smooth micro-interactions (200ms transitions)
- Figtree (headers) and Jost (body) typography

**Tech Stack:**
- Next.js 15.5.3 with App Router
- React 19.1.0
- TypeScript 5
- Tailwind CSS 4
- Turbopack (for fast builds)
- Axios 1.12.2

## Project Structure

```
frontend/
├── src/
│   ├── app/                          # Next.js App Router pages
│   │   ├── page.tsx                  # Main stylist experience (home)
│   │   ├── layout.tsx                # Root layout with metadata
│   │   ├── globals.css               # Global styling with Tailwind
│   │   └── admin/
│   │       ├── page.tsx              # Admin dashboard
│   │       └── AdminTable.tsx        # Fabric management table
│   │
│   ├── components/                   # Reusable React components
│   │   ├── CatalogSelector.tsx       # Fabric family & color picker
│   │   ├── GenerateButton.tsx        # Main generation trigger
│   │   ├── ImageUploadControls.tsx   # Gallery/camera file inputs
│   │   ├── GeneratedImageGallery.tsx # Thumbnail grid of results
│   │   ├── ImageModal.tsx            # Fullscreen image viewer
│   │   ├── SearchTela.tsx            # Fabric ID search component
│   │   ├── LoadingState.tsx          # Generation progress UI
│   │   ├── EmptyState.tsx            # Initial guidance message
│   │   └── LogoHeader.tsx            # Harris & Frank branding
│   │
│   ├── hooks/
│   │   └── useVirtualStylist.ts      # Central state management hook
│   │
│   ├── lib/                          # API clients & utilities
│   │   ├── apiClient.ts              # Main API client (catalog, generate)
│   │   ├── adminApi.ts               # Admin-specific API helpers
│   │   └── api.ts                    # Legacy/basic API wrapper
│   │
│   └── types/                        # TypeScript type definitions
│       ├── catalog.ts                # Fabric families, colors, generated images
│       ├── admin.ts                  # Fabric and color admin types
│       └── search.ts                 # Tela search functionality types
│
├── public/                           # Static assets
│   └── logo-Harris and frank color blanco.png
│
└── Configuration Files:
    ├── next.config.ts                # API rewrites & remote image patterns
    ├── tsconfig.json                 # TypeScript configuration
    ├── postcss.config.mjs            # PostCSS with Tailwind plugin
    ├── eslint.config.mjs             # ESLint configuration
    ├── package.json                  # Dependencies & scripts
    └── .env.local                    # Environment variables (API base URL)
```

## Key Features

### 1. Stylist Experience (Customer-Facing)
- **Full-Screen Layout**: No vertical scroll, optimized viewport usage with max-w-7xl container
- **Centered Logo Header**: Dark background (gray-900) with centered white logo
- **Compact Controls**: Family selector and fabric search in same row
- **Scrollable Fabric Grid**:
  - Fixed-height container with internal scroll
  - 4-column grid on desktop (2 on mobile, 3 on tablet)
  - Large square fabric swatches with hover effects (scale + shadow)
  - Shows ~8 fabrics visible (2 rows)
- **Image Upload**: Elegant white buttons with icons (📁 Elegir Foto, 📷 Tomar Foto)
- **Generate Button**: Premium black button with uppercase text, loading spinner, and lift effect
- **AI Generation**: Generate photorealistic suit visualizations in different poses
- **Gallery View**: View generated images in a responsive grid with independent scroll
- **Fullscreen Modal**: Click to zoom images with keyboard support (Escape to close)
- **Search**: Find fabrics by ID integrated in top row

### 2. Admin Dashboard (Phase 5 - COMPLETED)
- **Luxury Design System**: Consistent 3px borders, gray color palette, Figtree/Jost fonts
- **Fabric Management Grid**:
  - Responsive 1/2/3 column layout
  - 4:3 aspect ratio preview cards
  - Hover overlays with fabric names
  - Status badges (active/inactive)
- **Status Management**: Toggle switches with smooth transitions (active=left, inactive=right)
- **Bulk Operations**:
  - Multi-select mode with checkboxes
  - Bulk activate/deactivate
  - Bulk delete with confirmation
  - Floating action bar
- **Advanced Filtering**:
  - Collapsible filter panel
  - Filter by status (all/active/inactive)
  - Sort by: name, date, fabric count, recent updates
  - Ascending/descending order
- **Fabric Cards**:
  - Expandable color grids (3 columns)
  - Drag-and-drop color moving between families
  - Individual status toggles
  - Edit/Delete actions (UI ready, modals pending)
- **Search Bar**: Real-time search by family ID, name, or fabric colors
- **Footer Statistics**: Total families and fabrics count

## Architecture & Design Patterns

### State Management
The application uses a centralized state management pattern through the `useVirtualStylist` hook:

```typescript
// Single source of truth for the entire application
const {
  // Catalog state
  families, selectedFamily, status,
  // Selection state
  familyId, colorId, currentFamily,
  // Generation state
  isGenerating, generationError, images,
  // Preview state
  preview, fileRef,
  // Modal state
  selectedImage, openModal, closeModal,
  // Actions
  selectFamily, selectColor, handleGenerate, handleFileChange
} = useVirtualStylist();
```

**Key State Features:**
- Initialization from backend on mount
- Default family selection (first active family)
- Cascading selection (color resets when family changes)
- File handling with blob URL cleanup
- Event listeners (Escape key for modal)
- Memoization for performance

### API Architecture

**Proxy-Based API Integration:**
- Frontend calls `/api/*` endpoints
- Next.js rewrites to `NEXT_PUBLIC_API_BASE` (environment variable)
- Enables CORS-free communication
- Supports local dev, staging (RunPod), and production

**API Client Features:**
- 60-second default timeout (configurable)
- Automatic Content-Type detection (JSON/FormData)
- Error propagation with status codes
- URL normalization (handles duplicate slashes)

### Component Architecture

**Component Hierarchy:**
```
App (page.tsx)
├── LogoHeader
├── CatalogSelector
├── SearchTela
├── ImageUploadControls
├── GenerateButton
├── LoadingState / EmptyState
└── GeneratedImageGallery
    └── ImageModal
```

**Design Principles:**
- Single Responsibility: Each component has one clear purpose
- Composition: Complex UI built from simple, reusable components
- Props-driven: Components receive data and callbacks via props
- Type-safe: All props and state are fully typed with TypeScript

## API Endpoints

### Public Endpoints
```
GET  /api/catalog              # Fetch fabric families and colors
POST /api/generate             # Generate AI suit visualization
GET  /api/health              # Health check
```

### Admin Endpoints
```
# Fabrics
GET    /api/admin/fabrics                    # List all fabrics
GET    /api/admin/fabrics/:id                # Get single fabric
POST   /api/admin/fabrics                    # Create fabric
PATCH  /api/admin/fabrics/:id                # Update fabric
DELETE /api/admin/fabrics/:id                # Delete fabric
PATCH  /api/admin/fabrics/:id/status         # Toggle active/inactive
POST   /api/admin/fabrics/:id/preview        # Upload preview image

# Variants (Colors)
GET    /api/admin/variants                   # List all variants
GET    /api/admin/fabrics/:id/variants       # List variants for fabric
POST   /api/admin/variants                   # Create variant
PATCH  /api/admin/variants/:id               # Update variant
DELETE /api/admin/variants/:id               # Delete variant
```

## Environment Configuration

**Required Environment Variables:**

Create a `.env.local` file in the project root:

```env
# Backend API Base URL
NEXT_PUBLIC_API_BASE=https://your-backend-url.com

# Optional: RunPod-specific URL (if using RunPod)
NEXT_PUBLIC_RUNPOD_URL=https://gnmicpjvt9n5dz-8000.proxy.runpod.net
```

**Current Backend:**
- RunPod deployment: `https://gnmicpjvt9n5dz-8000.proxy.runpod.net`

## Development

### Prerequisites
- Node.js 20+ (for Next.js 15)
- npm or yarn
- Git

### Setup
```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local  # (if .env.example exists)
# OR create .env.local manually with required variables

# Run development server
npm run dev
```

### Available Scripts
```bash
npm run dev      # Start development server with Turbopack
npm run build    # Build for production with Turbopack
npm start        # Start production server
npm run lint     # Run ESLint
```

### Development Server
- Local URL: http://localhost:3000
- Admin Dashboard: http://localhost:3000/admin

## Build & Deployment

### Next.js Configuration

**API Rewrites** (`next.config.ts`):
```typescript
async rewrites() {
  return [
    {
      source: "/api/:path*",
      destination: `${process.env.NEXT_PUBLIC_API_BASE}/:path*`
    }
  ];
}
```

**Remote Image Patterns**:
```typescript
images: {
  remotePatterns: [
    { protocol: "http", hostname: "localhost", port: "8000", pathname: "/files/**" },
    { protocol: "http", hostname: "127.0.0.1", port: "8000", pathname: "/files/**" },
    { protocol: "https", hostname: "*.proxy.runpod.net" }
  ]
}
```

### Build Process
1. **Turbopack**: Fast builds enabled by default
2. **Image Optimization**: Next.js Image component with remote patterns
3. **Code Splitting**: Automatic component-level splitting
4. **TypeScript**: Compile-time type checking

### Deployment Platforms
- **Vercel** (recommended - native Next.js support)
- **Node.js hosts** (run `npm start` after build)
- **Static export** (possible with limitations)

**Deployment Steps:**
1. Set environment variables on hosting platform
2. Run `npm run build`
3. Deploy `.next` directory
4. Start with `npm start`

## Design System (Harris & Frank Inspired)

### Color Palette
```css
/* Backgrounds */
--color-bg-light: #f9f9f9;    /* Soft white - main background */
--color-white: #ffffff;        /* Pure white - cards, buttons */

/* Text */
--color-dark: #1c1d1d;        /* Near-black - primary text */
--color-charcoal: #222222;     /* Dark charcoal - accents */

/* Borders & Shadows */
--color-border: #e5e5e5;       /* Subtle borders */
--color-shadow: rgba(0, 0, 0, 0.08);

/* Status Colors */
--color-active: #10b981;       /* Green for active */
--color-inactive: #6b7280;     /* Gray for inactive */
```

### Typography
- **Headers**: Figtree, 0.2em letter-spacing (elegant elongation)
- **Body**: Jost, 14px, 1.6 line-height
- **Buttons**: Uppercase with tracking-wide

### Spacing & Layout
- **Max Width**: 1280px (max-w-7xl)
- **Card Padding**: 24px
- **Border Radius**: 3px (sharp, not rounded)
- **Grid Gaps**: 24px (gap-6)

### Interactive Elements
- **Transitions**: 200ms ease-out
- **Hover Effects**:
  - Lift: `translateY(-0.5px)` or `translateY(-2px)` for buttons
  - Shadow: Subtle elevation increase
  - Border: Gray → Black
- **Focus States**: 2px ring with offset
- **Active States**: Return to neutral position

### Button Styles
1. **Primary (Black)**:
   - `bg-gray-900 text-white`
   - Uppercase with tracking
   - Hover: lift + shadow
   - Example: "Generar Imágenes"

2. **Secondary (White)**:
   - `bg-white border-gray-300 text-gray-900`
   - Icon + text
   - Hover: border-gray-900 + lift
   - Example: "Elegir Foto"

3. **Danger (Red)**:
   - `bg-red-600 text-white`
   - Used for delete actions
   - Hover: bg-red-700

### Component Patterns
- **Cards**: White background, gray border, subtle shadow
- **Inputs**: White background, focus ring, 3px radius
- **Toggles**: Smooth transitions, clear states
- **Modals**: Centered, backdrop blur, smooth enter/exit

## TypeScript Types

### Core Types

**Catalog Types** (`src/types/catalog.ts`):
```typescript
interface FabricFamily {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
}

interface Color {
  id: string;
  name: string;
  hex_code: string;
  family_id: string;
  is_active: boolean;
}

interface GeneratedImage {
  url: string;
  width: number;
  height: number;
  pose?: 'recto' | 'cruzado';
}
```

**Admin Types** (`src/types/admin.ts`):
```typescript
interface Fabric {
  id: string;
  family_id: string;
  family_name: string;
  description?: string;
  is_active: boolean;
  colors: Color[];
  preview_url?: string;
}
```

## Performance Optimizations

1. **Turbopack**: Next-generation bundler for faster builds
2. **Image Optimization**: Automatic Next.js image optimization
3. **Memoization**: React.memo and useMemo for expensive operations
4. **Code Splitting**: Automatic route-based splitting
5. **Lazy Loading**: Images loaded on demand
6. **Blob URL Cleanup**: Automatic cleanup to prevent memory leaks

## Testing Strategy

### Recommended Testing Approach
```bash
# Unit tests (components)
- Test catalog selection logic
- Test image upload handling
- Test search functionality

# Integration tests
- Test API client methods
- Test hook state management
- Test form submissions

# E2E tests
- Test full user flow (select fabric → upload → generate)
- Test admin CRUD operations
- Test modal interactions
```

## Git Workflow

**Current Branch**: `main`

**Recent Changes:**
- Merged PR #8: File updates for frontend and backend
- Shared API base env var across frontend
- Prompt to white background
- IP Adapter checking
- Switched to real RunPod URL

**Uncommitted Changes:**
- `src/app/admin/AdminTable.tsx`
- `src/hooks/useVirtualStylist.ts`
- `src/lib/adminApi.ts`
- `src/lib/apiClient.ts`

## Troubleshooting

### Common Issues

**Issue: API calls failing**
- Check `NEXT_PUBLIC_API_BASE` is set correctly
- Verify backend is running and accessible
- Check browser console for CORS errors

**Issue: Images not displaying**
- Verify image URL is allowed in `next.config.ts` remote patterns
- Check image URL format matches expected patterns
- Verify backend `/files/**` endpoint is accessible

**Issue: Build failures**
- Clear `.next` directory: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npm run lint`

**Issue: Environment variables not loading**
- Ensure `.env.local` exists in project root
- Restart dev server after changing env vars
- Verify variable names start with `NEXT_PUBLIC_`

## Best Practices

### Code Style
- Use TypeScript for all files
- Follow ESLint rules (`npm run lint`)
- Use meaningful component and variable names
- Add comments for complex logic

### Component Guidelines
- Keep components small and focused
- Use props for data, not state when possible
- Extract reusable logic into custom hooks
- Type all props and state

### API Integration
- Always handle loading and error states
- Use proper HTTP methods (GET, POST, PATCH, DELETE)
- Include timeout handling for long operations
- Validate responses before using data

### Performance
- Memoize expensive calculations
- Clean up event listeners and blob URLs
- Use Next.js Image component for images
- Avoid unnecessary re-renders

## Recent Updates (Latest Session - 2025-01-XX)

### ✅ Completed
1. **User Experience Redesign**:
   - Full-screen layout without vertical page scroll
   - Centered logo header with dark background
   - Family selector and fabric search in same row (2-column grid)
   - Scrollable fabric grid reduced by 33% height
   - 4-column fabric grid on desktop (responsive: 2/3/4)
   - Large square swatches with hover scale effect

2. **Button Styling (Harris & Frank aesthetic)**:
   - "Generar Imágenes": Black button with uppercase text, lift hover, loading spinner
   - "Elegir Foto"/"Tomar Foto": White buttons with icons, border transitions
   - Consistent 3px border radius, 200ms transitions

3. **Admin Panel Enhancements**:
   - Fixed StatusToggle direction (active=left, inactive=right)
   - Resolved FabricCard z-index issues (checkbox vs status badge)
   - Changed terminology from "colores" to "telas" throughout admin
   - Fabric grid shows actual fabric images (3 columns)
   - Improved fallback for missing swatch images (elegant hex display)

4. **Backend Integration**:
   - Added `build_swatch_url()` function in admin router
   - Constructs swatch URLs dynamically using `swatch_code` field
   - Updated seed script to populate `swatch_code` instead of `swatch_url`
   - Created `update_swatch_codes.py` utility script

### ⚠️ Pending Tasks

#### High Priority (Critical for Production)
1. **Admin CRUD Modals** (UI exists, handlers need implementation):
   - [ ] CreateFabricModal - New family creation form
   - [ ] EditFabricModal - Edit existing family
   - [ ] DeleteConfirmationModal - Safe deletion with confirmation
   - [ ] ColorManagementModal - Add/edit/remove fabrics within families
   - [ ] ImageUploadModal - Upload swatch images with preview

2. **Backend Data Migration**:
   - [ ] Create new seed script using `swatch_categorization.json`
   - [ ] Migrate to color-based families: azules, grises, marrones, neutros
   - [ ] Remove old fabric families (lana-cachemir, algodon-tech, etc.)
   - [ ] Populate `swatch_code` field for all existing fabrics
   - [ ] Run seed: `python seed.py` or `python update_swatch_codes.py`

3. **Authentication & Authorization**:
   - [ ] Admin login page
   - [ ] Protected routes with JWT validation
   - [ ] Session management
   - [ ] Logout functionality

4. **Validation & Error Handling**:
   - [ ] Client-side form validation (Zod or Yup)
   - [ ] Toast notifications (replace `alert()`)
   - [ ] HTTP error handling by status code
   - [ ] Retry logic for network failures

#### Medium Priority (UX Improvements)
5. **Visual Feedback**:
   - [ ] Success toasts after operations
   - [ ] Undo functionality for bulk actions
   - [ ] Loading skeletons (replace spinners)
   - [ ] Optimistic UI updates

6. **Image Management**:
   - [ ] Drag-and-drop file upload
   - [ ] Image preview before upload
   - [ ] Crop/resize functionality
   - [ ] Bulk image upload

7. **Search & Filtering**:
   - [ ] Persist filters in localStorage or URL params
   - [ ] Search by hex color code
   - [ ] Save custom filter views
   - [ ] Export catalog to CSV/Excel

8. **Performance**:
   - [ ] Pagination for large catalogs (100+ families)
   - [ ] Virtual scrolling for long lists
   - [ ] Debounce search input
   - [ ] Memoization for heavy components
   - [ ] Code splitting and lazy loading

#### Low Priority (Nice to Have)
9. **Keyboard Shortcuts**:
   - [ ] Ctrl+A (select all)
   - [ ] Delete key (bulk delete)
   - [ ] Escape (close modals)
   - [ ] Arrow keys (navigate grid)

10. **Audit & History**:
    - [ ] Change tracking (who changed what)
    - [ ] Version history
    - [ ] Rollback capability

11. **Testing**:
    - [ ] Unit tests (Jest + React Testing Library)
    - [ ] Integration tests (API mocking)
    - [ ] E2E tests (Playwright)
    - [ ] Storybook component documentation

12. **Accessibility**:
    - [ ] ARIA labels and roles
    - [ ] Keyboard navigation
    - [ ] Screen reader optimization
    - [ ] WCAG AA/AAA compliance

## Future Enhancements

### Potential Features
1. **User Authentication**: Add login/logout for admin (PENDING - High Priority)
2. **Image History**: Save generated images to user account
3. **Batch Generation**: Generate multiple variations at once
4. **Analytics**: Track fabric popularity and usage
5. **Export**: Download generated images
6. **Comparison View**: Side-by-side fabric comparison
7. **Mobile App**: React Native version

### Technical Improvements
1. **Testing**: Add Jest + React Testing Library (PENDING)
2. **E2E Tests**: Playwright or Cypress (PENDING)
3. **Storybook**: Component documentation (PENDING)
4. **CI/CD**: Automated testing and deployment
5. **Monitoring**: Error tracking (Sentry)
6. **Analytics**: User behavior tracking

## Resources

### Documentation
- [Next.js 15 Documentation](https://nextjs.org/docs)
- [React 19 Documentation](https://react.dev)
- [Tailwind CSS v4](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)

### Internal Resources
- Backend API: Check backend repository for API documentation
- Design Assets: `public/` directory
- Type Definitions: `src/types/` directory

## Support

For issues or questions:
1. Check this documentation first
2. Review recent git commits for context
3. Check backend API documentation
4. Contact development team

---

**Last Updated**: 2025-10-25
**Version**: 0.1.0
**Maintainer**: Development Team
