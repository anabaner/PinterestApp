# PinBoard — Frontend

A Pinterest-style image board built with React and Vite. Displays pins in a masonry grid, supports image uploads with AI auto-tagging, and shows similar pins using semantic search.

---

## Tech Stack

- **React 18** — UI framework
- **Vite** — dev server and build tool
- **react-masonry-css** — Pinterest-style masonry grid layout
- **axios** — HTTP client for API calls
- **CSS** — custom styling, no UI library needed

---

## Prerequisites

Before running the frontend, make sure the backend is running at `http://127.0.0.1:8000`.
See the [backend README](../backend/README.md) for setup instructions.

- Node.js 18+
- npm 9+

---

## Getting Started

### 1. Navigate to the frontend folder

```bash
cd frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Start the development server

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── PinCard.jsx        # Individual pin card with hover overlay
│   │   ├── PinGrid.jsx        # Masonry grid layout
│   │   └── UploadModal.jsx    # Image upload modal with board selector
│   ├── App.jsx                # Root component, state management
│   ├── App.css                # All styles
│   ├── api.js                 # All backend API calls in one place
│   └── main.jsx               # React entry point
├── index.html
├── package.json
├── package-lock.json
└── vite.config.js
```

---

## Features

### Masonry pin grid
All pins are loaded from the backend on startup and displayed in a responsive masonry grid. The number of columns adjusts automatically based on screen width — 4 columns on desktop, 3 on tablet, 2 on small screens, 1 on mobile.

### AI-powered upload
Click the **+ Upload** button to open the upload modal. Select an image and choose a board — the backend will automatically generate a title, description, and tags using Gemini AI. The new pin appears at the top of the grid instantly without a page refresh.

### Similar pins drawer
Click any pin to open a side drawer showing the pin's full description, tags, and up to 6 semantically similar pins. Similar pins are found using sentence-transformer embeddings stored in ChromaDB on the backend. Click any similar pin to navigate to it.

### Delete pins
Hover over any pin to reveal a delete button. Clicking it removes the pin from both the database and the grid instantly.

---

## API Calls

All backend communication is handled in `src/api.js`:

| Function | Method | Endpoint | Description |
|---|---|---|---|
| `getAllPins()` | GET | `/pins` | Fetch all pins |
| `uploadPin(file, board)` | POST | `/pins/upload` | Upload image, AI tags it |
| `getSimilarPins(pinId)` | GET | `/pins/:id/similar` | Get similar pins |
| `deletePin(pinId)` | DELETE | `/pins/:id` | Delete a pin |

To point the frontend at a different backend URL, update the `BASE` constant in `src/api.js`:

```js
const BASE = "http://127.0.0.1:8000";  // change this for production
```

---

## Available Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start development server at localhost:5173 |
| `npm run build` | Build for production into the `dist/` folder |
| `npm run preview` | Preview the production build locally |

---

## Boards

The upload modal supports these boards by default:

`General` · `Travel` · `Food` · `Fashion` · `Art` · `Technology` · `Nature`

To add or remove boards, edit the `BOARDS` array in `src/components/UploadModal.jsx`:

```jsx
const BOARDS = ["General", "Travel", "Food", "Fashion", "Art", "Technology", "Nature"];
```

---

## Running Both Servers

The frontend and backend must run simultaneously. Open two terminal tabs:

**Terminal 1 — backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Terminal 2 — frontend:**
```bash
cd frontend
npm run dev
```

---

## Deployment

For production deployment, build the frontend with:

```bash
npm run build
```

This creates a `dist/` folder with static files ready to deploy to **Vercel** (recommended for free hosting).

See Day 6 of the project guide for full deployment instructions.

---

## Known Limitations

- Images are served from the local backend — the `image_url` in `api.js` points to `http://127.0.0.1:8000`. Update this to your deployed backend URL before deploying to production.
- Similar pins search works best with 10+ pins per board. With fewer pins, results may be limited or empty.
- The `chroma_store/` vector database is local — if you wipe it, run `POST /admin/reindex` on the backend to rebuild embeddings from existing pins.