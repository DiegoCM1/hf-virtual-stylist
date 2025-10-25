# Harris & Frank Virtual Stylist - Frontend

## Project Overview

The Harris & Frank Virtual Stylist is an AI-powered digital suit styling and visualization application for a luxury menswear brand. This Next.js 15 application provides an interactive, mobile-friendly interface that allows customers and sales associates to visualize suits in different fabrics and colors using AI-generated photorealistic images.

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
- **Catalog Selection**: Browse fabric families and color variants
- **Image Upload**: Capture from camera or upload from gallery
- **AI Generation**: Generate photorealistic suit visualizations in different poses (recto/front and cruzado/side)
- **Gallery View**: View generated images in a responsive grid
- **Fullscreen Modal**: Click to zoom images with keyboard support (Escape to close)
- **Search**: Find fabrics by ID (e.g., "navy-001")

### 2. Admin Dashboard
- **Fabric Management**: View, create, edit, and delete fabrics
- **Status Management**: Toggle active/inactive status for fabrics
- **Color Management**: Add and manage color variants for each fabric
- **Preview Upload**: Upload preview images for fabrics
- **Search & Filter**: Search by family ID or name
- **Quick Create**: Fast form for adding new fabrics

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

## Future Enhancements

### Potential Features
1. **User Authentication**: Add login/logout for admin
2. **Image History**: Save generated images to user account
3. **Batch Generation**: Generate multiple variations at once
4. **Analytics**: Track fabric popularity and usage
5. **Export**: Download generated images
6. **Comparison View**: Side-by-side fabric comparison
7. **Mobile App**: React Native version

### Technical Improvements
1. **Testing**: Add Jest + React Testing Library
2. **E2E Tests**: Playwright or Cypress
3. **Storybook**: Component documentation
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
