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

