This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.


<!-- Start backend -->
uvicorn app.main:app --reload --port 8000

<!-- Start frontend -->
npm run dev

---

## Application Guide

### Folder Structure

```
frontend/
├── src/
│   ├── app/                # App Router entrypoints (layout, page, globals.css)
│   ├── components/         # Reusable UI building blocks
│   ├── hooks/              # State + API orchestration (`useVirtualStylist`)
│   ├── lib/                # REST client (`apiClient`), typed endpoints
│   └── types/              # Shared TypeScript interfaces
├── public/                 # Static assets (logos, icons)
├── next.config.ts          # Custom Next.js config (images, rewrites, etc.)
└── tsconfig.json           # Path aliases and compiler options
```

### Core Experience

1. **Catalog Discovery** – `CatalogSelector` renders families and colors fetched from `GET /catalog/fabrics`. Selections are bubbled up through props into the main page state.
2. **Styling Workflow** – `SearchTela` combines the selector, upload controls, and copy deck to guide the associate through fabric exploration.
3. **Generation Trigger** – `GenerateButton` invokes the `useVirtualStylist` hook, which wraps the API call, loading states, and error handling.
4. **Results Gallery** – `GeneratedImageGallery` and `ImageModal` display returned assets, providing zoom/download actions using the URLs served by FastAPI.

### API Integration Details

- `src/lib/apiClient.ts` centralizes fetch logic. It respects the `NEXT_PUBLIC_API_BASE` environment variable and automatically attaches JSON headers.
- `src/lib/api.ts` and `src/lib/adminApi.ts` expose typed helpers such as `generateLook()` or `fetchCatalog()` to keep components declarative.
- The hook `useVirtualStylist` manages debounce, optimistic loading, and exposes `generate`, `isLoading`, and `result` fields for the UI.

### Styling System

- Tailwind CSS powers utility classes (see `postcss.config.mjs` and `globals.css`).
- Component-level styling leans on semantic classnames with Tailwind modifiers, ensuring the layout remains responsive on showroom tablets.
- Add bespoke design tokens inside `globals.css` (CSS variables) for brand colors and typography.

### Environment Variables

Create a `.env.local` with:

```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

For production, point this variable to the deployed FastAPI origin and ensure CORS allows the frontend hostname.

### Development Tips

- Run `npm run lint` to catch JSX/TypeScript issues early.
- Use the React DevTools extension to inspect component state transitions, especially around `useVirtualStylist`.
- When mocking the backend, you can stub responses in `apiClient.ts` or leverage MSW (Mock Service Worker) in future tests.

### Deployment Notes

- Vercel automatically reads environment variables prefixed with `NEXT_PUBLIC_` from the project dashboard.
- To host elsewhere, generate a static build with `npm run build` and run `npm start` behind your preferred reverse proxy.
- Ensure the backend exposes HTTPS URLs for generated images so that modern browsers do not block mixed content.
