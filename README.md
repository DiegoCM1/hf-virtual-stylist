# The HF Virtual Stylist

An AI-powered design studio that brings the entire Harris & Frank bespoke collection to life, instantly.

---

## The Vision

In the world of bespoke tailoring, imagination is the only limit. Yet, showrooms are finite. **Project Atelier** bridges the gap between a client's vision and tangible reality by creating an infinite digital showroom.

This tool empowers Harris & Frank's sales associates to move beyond physical samples and render any suit from their catalog in any available fabric and color combination, on-demand. It transforms the sales conversation into an interactive design session, providing clients with immediate, photorealistic visualizations of their unique creations.

---

## How It Works

The workflow is designed for elegance and speed, mirroring a natural sales conversation:

1.  **Select a Style:** The associate chooses a fabric family or style that matches the client's needs (e.g., "Lana-Cachemir").

2.  **Choose a Color:** The UI displays a rich palette of available colors for that specific fabric.

3.  **Generate Reality:** With a single click, the AI engine generates two photorealistic, high-resolution images of the final suit, showcasing both a direct (`recto`) and crossed-arm (`cruzado`) pose.

---

## Key Features

-   **Dynamic Fabric & Color Catalog:** A fully dynamic, visually-driven menu of all available H&F fabrics and colors, easily managed via a dedicated admin panel.
-   **Photorealistic On-Demand Renders:** State-of-the-art AI generates lifelike images in under 60 seconds, capturing the unique texture and drape of each fabric.
-   **Seamless Sharing:** Associates can instantly share the generated visuals with clients via a public link, continuing the sales conversation beyond the showroom.
-   **Built for the Sales Floor:** A clean, intuitive, and reliable interface designed for tablets and large screens in a client-facing environment.

---

## Tech Stack

This project leverages a modern, high-performance stack to deliver a cutting-edge experience.

-   **Frontend:** Next.js, React, Tailwind CSS
-   **Backend:** FastAPI, Python
-   **AI Engine:** PyTorch, SDXL, with custom-trained LoRA models for fabric realism and ControlNet for pose consistency.

---

## Current Status

**MVP in Development.** The backend skeleton with mock data is complete and functional. The minimal frontend UI is in progress. The core focus is on completing the Week 1 deliverable: a functional end-to-end flow with placeholder data.

---

## Commands
### Backend
source .venv/Scripts/activate

uvicorn app.main:app --reload --port 8000


### Frontend
npm run dev

---

## Architecture Overview

This repository is organized as a **two-tier application** where a FastAPI backend exposes a REST API that the Next.js frontend consumes. Both services share a simple contract that revolves around catalog metadata and image-generation requests.

- **Frontend (`frontend/`):** A React/Next.js App Router project. UI components live in `src/components`, reusable hooks in `src/hooks`, and all HTTP helpers in `src/lib`. The frontend retrieves catalog metadata, lets the associate curate a request, and sends a JSON payload to `/generate`.
- **Backend (`backend/`):** A FastAPI application inside `backend/app`. It exposes `/catalog` and `/generate` endpoints, persists generated assets under `backend/storage/`, and serves them via the `/files` static route. Services under `app/services` encapsulate catalog lookups, image synthesis (mock or SDXL), watermarking, and storage.
- **Shared Contract:** Request/response models in `backend/app/models` (e.g., `GenerationRequest`, `GenerationResponse`) define the JSON schema consumed by the frontend and documented in the backend README.

### Data Flow at a Glance

1. A sales associate selects a fabric family and color from the catalog component, powered by `GET /catalog/fabrics`.
2. Clicking **Generate** triggers the frontend hook `useVirtualStylist` to POST a `GenerationRequest` to `/generate` with the desired `family_id`, `color_id`, and cuts (poses).
3. The backend generator service creates (or mocks) images, stores them via `LocalStorage.save_bytes`, and responds with HTTPS URLs under `/files/generated/...` alongside metadata.
4. The frontend's `GeneratedImageGallery` renders the thumbnails, and `ImageModal` loads the high-resolution assets using the returned URLs.

---

## Environment & Tooling

| Concern | Frontend | Backend |
| --- | --- | --- |
| Language | TypeScript (ESNext) | Python 3.10+
| Package manager | `npm` (Node 18+) | `pip` + `uv`/`venv`
| Entrypoint | `npm run dev` (Next.js dev server on port 3000) | `uvicorn app.main:app --reload --port 8000`
| Static assets | `frontend/public` | `/files` mounted from `backend/storage`
| Tests | `npm run lint` / component tests (future) | `pytest` under `backend/tests`

> Tip: Run both services together for the full experience. The frontend expects the API at `http://localhost:8000` and has CORS rules preconfigured for `http://localhost:3000`.

### Local Development Checklist

1. **Clone & Install:** `npm install` inside `frontend/` and `pip install -r requirements.txt` inside `backend/` (activate the virtualenv as needed).
2. **Environment Variables:**
   - Backend honors `APP_VERSION`, `WATERMARK_PATH`, and (future) storage credentials like `AWS_ACCESS_KEY_ID`.
   - Frontend reads `NEXT_PUBLIC_API_BASE` (defaulting to `http://localhost:8000`).
3. **Start Services:** Launch the backend first, then the frontend. Use two terminals or a process manager.
4. **Verify Health:** `curl http://localhost:8000/healthz` should return `{ "ok": true, ... }`. Load `http://localhost:3000` to interact with the UI.

### Deployment Snapshot

- **Backend:** Container-friendly FastAPI app. Mount persistent storage (or configure S3/R2) at `/files`. The provided `deploy.sh` script in the README demonstrates how the team syncs to a RunPod instance.
- **Frontend:** Ready for Vercel/Netlify deployment. Ensure `NEXT_PUBLIC_API_BASE` points to the deployed backend URL and that CORS allows the frontend origin.
- **Model Weights:** When switching from the mock generator to SDXL (`USE_MOCK = False` in `app/routers/generate.py`), ensure GPU availability and that the Hugging Face cache is writable (`HF_HOME`).

---

## Feature Walkthrough

### Catalog Exploration
- `CatalogSelector` fetches fabric families and colors from `/catalog/fabrics`.
- The UI groups colors by family and highlights availability.
- Selecting a color updates the hook state and primes the generation request.

### Image Generation
- `GenerateButton` disables itself while awaiting a response.
- The backend responds with two `ImageResult` entries (`recto`, `cruzado`), each watermarked via `apply_watermark_image`.
- URLs are persisted locally by default (`storage/generated/...`) and are immediately available to the frontend.

### Download & Sharing
- The gallery component provides modal zoom with download-ready URLs.
- Since assets are served by FastAPI's static files, they can be bookmarked or shared externally as long as the backend remains online.

---

## Troubleshooting

- **CORS errors?** Verify the frontend origin matches the `allow_origins` list in `app/main.py`.
- **Missing watermark assets?** Set `WATERMARK_PATH` to an accessible `.webp` file (see `backend/tests/assets/logo.webp`).
- **Slow generation?** When using SDXL, generation speed depends on GPU availability. Switch to the mock generator for demos by setting `USE_MOCK = True` in `app/routers/generate.py`.
- **Broken image URLs?** Confirm the backend has write permissions to `backend/storage` and that the `/files` mount points to the same directory.

