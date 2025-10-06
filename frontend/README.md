# Frontend – Next.js App Router

## Overview
The frontend is a Next.js 15 application that delivers the client-facing stylist experience and an admin dashboard. It talks to the FastAPI service through a `/api/*` proxy, surfaces fabric and color metadata, orchestrates image generation, and lets merchandising teams curate inventory from `/admin`.【F:frontend/src/app/page.tsx†L1-L70】【F:frontend/src/app/admin/page.tsx†L1-L40】

## Core Features
- **Guided styling flow** – `useVirtualStylist` fetches the catalog, manages selection state, triggers generations, and keeps loading and error feedback consistent across components.【F:frontend/src/hooks/useVirtualStylist.ts†L1-L201】
- **Rich gallery experience** – Components such as `GeneratedImageGallery`, `ImageModal`, and `LoadingState` provide thumbnail grids, zoomable previews, and progress feedback for the rendered looks.【F:frontend/src/components/GeneratedImageGallery.tsx†L1-L120】【F:frontend/src/components/ImageModal.tsx†L1-L120】
- **Fabric search & quick create** – The `/admin` route renders an interactive table that can search, toggle active status, and seed demo fabrics via the admin API helpers in `src/lib/adminApi.ts`.【F:frontend/src/app/admin/AdminTable.tsx†L1-L228】【F:frontend/src/lib/adminApi.ts†L1-L39】
- **Device-friendly uploads** – `ImageUploadControls` expose camera and gallery pickers; previews are displayed with metadata so associates can blend reference imagery into conversations.【F:frontend/src/components/ImageUploadControls.tsx†L1-L160】

## Project Structure
```
frontend/
├── src/
│   ├── app/            # App Router pages (`page.tsx`, `/admin`)
│   ├── components/     # Reusable UI (catalog selector, gallery, modals)
│   ├── hooks/          # `useVirtualStylist` state machine
│   ├── lib/            # API clients and typed helpers
│   └── types/          # Shared TypeScript contracts
├── public/             # Static assets (logos)
├── next.config.ts      # API proxy rewrites and remote image patterns
└── package.json        # Scripts and dependencies
```

## Getting Started
1. Install dependencies: `npm install`.
2. Create `.env.local` to point the proxy and admin tooling to your backend:
   ```env
   NEXT_PUBLIC_RUNPOD_URL=http://localhost:8000
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```
   `next.config.ts` rewrites `/api/:path*` to `NEXT_PUBLIC_RUNPOD_URL`, so the catalog and generate calls go straight to FastAPI while keeping relative URLs inside the app.【F:frontend/next.config.ts†L1-L21】【F:frontend/src/lib/apiClient.ts†L1-L38】
3. Run the dev server: `npm run dev` (defaults to `http://localhost:3000`).
4. Open `/admin` to access the merchandising console. It relies on the same `/api` proxy for `GET/POST/PATCH /admin/fabrics` requests.【F:frontend/src/lib/adminApi.ts†L1-L39】

## API Helpers
- `fetchCatalog()` and `generateImages()` live in `src/lib/apiClient.ts` and return typed responses consumed by the hook and UI components.【F:frontend/src/lib/apiClient.ts†L1-L38】
- Admin helpers (`listFabrics`, `createFabric`, `setFabricStatus`, `deactivateFabric`) use an Axios client configured with the `/api` base path, making the dashboard portable between local dev and RunPod deployments.【F:frontend/src/lib/adminApi.ts†L1-L39】

## Testing & Quality
Run ESLint to catch TypeScript and accessibility issues:
```bash
npm run lint
```

## Deployment Notes
- Vercel/Next proxies will automatically forward `/api/*` when `NEXT_PUBLIC_RUNPOD_URL` is set in the environment. For static hosting or custom deployments, configure an equivalent rewrite.
- Ensure the backend exposes HTTPS asset URLs (or configure `NEXT_PUBLIC_API_BASE_URL`) so that the gallery can display generated images without mixed-content warnings.【F:frontend/src/app/admin/page.tsx†L1-L32】
