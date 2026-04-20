Pinterest Demo App
===================

A small Pinterest-like backend demo written in FastAPI. This repository provides a REST API to create, read, update, and delete "pins", upload images, auto-generate titles/tags using an LLM image-tagging agent, and perform similarity search using embeddings stored in ChromaDB.

This README covers setup (Windows cmd.exe), required environment variables, how to run the backend, and a quick reference to the API endpoints.

What's included
- `backend/` - FastAPI application and supporting modules (database, embeddings, agents, upload helper).
- `static/uploads/` - uploaded images (this folder is ignored by git by default).
- `chroma_store/` - local ChromaDB store (ignored by git by default).

Quick checklist
- [x] Create a virtual environment
- [x] Install dependencies
- [x] Provide API keys in a `.env` file
- [x] Run the server with Uvicorn

Prerequisites
- Python 3.10 or newer
- Git (already used for this repo)

Environment variables
Create a `.env` file in the project root containing the API keys the project uses. Example:

```
# .env (example)
GEMINI_API_KEY=sk-xxxx...        # used by backend/agent.py (Google Gemini)
ANTHROPIC_API_KEY=claude-xxxx...  # used by backend/agent_claude.py (Anthropic Claude)
```

(If you only plan to use Claude-based auto-tagging, you can ignore the Gemini key and vice-versa.)

Install dependencies

From a Windows cmd.exe prompt, run:

```cmd
cd /d C:\Users\Ananya\PycharmProjects\PinterestDemoApp
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install fastapi[all] sqlalchemy aiosqlite uvicorn python-dotenv pillow sentence-transformers chromadb anthropic google-generative-ai
```

Note: `sentence-transformers` will download a model (~90MB) the first time it runs. `chromadb` stores its data under `chroma_store/`.

Run the server (development)

```cmd
cd /d C:\Users\Ananya\PycharmProjects\PinterestDemoApp
.venv\Scripts\activate
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Once running, OpenAPI docs are available at:
- http://127.0.0.1:8000/docs (Swagger UI)
- http://127.0.0.1:8000/redoc (ReDoc)

API endpoints (summary)
- POST /pins - create a pin (JSON body matching `PinCreate` schema).
- GET /pins - list all pins (most recent first).
- GET /pins/{pin_id} - get a single pin by id.
- PATCH /pins/{pin_id} - update fields on a pin.
- DELETE /pins/{pin_id} - delete a pin (also removes embedding).
- POST /pins/upload - upload an image file. The server saves the image, runs the auto-tagging agent, creates a Pin, and indexes its embedding.
- GET /pins/{pin_id}/similar - get similar pins using ChromaDB embeddings.
- POST /admin/reindex - reindex all pins into ChromaDB (useful when changing collection or after a reset).

Uploading an image (example curl)

From cmd.exe you can upload a file using curl (replace `path\to\image.jpg`):

```cmd
curl -X POST "http://127.0.0.1:8000/pins/upload" -F "file=@C:\path\to\image.jpg" -F "board=General"
```

Notes about auto-tagging agents
- There are two agent implementations in `backend/`:
  - `agent_claude.py` — uses Anthropic Claude and sends the image as base64. Use `ANTHROPIC_API_KEY`.
  - `agent.py` — uses Google Gemini (`GEMINI_API_KEY`).

By default `backend/main.py` imports `auto_tag_image` from `agent` (Gemini). If you'd rather use the Claude agent, swap the import to use `agent_claude.auto_tag_image` instead, or set up both and choose at runtime.

Git / repository notes
- The repository already includes a `.gitignore` that excludes `static/uploads/`, `pinterest.db`, and `chroma_store/`. Uploaded images and the local DB won't be committed.
- Remote repository: https://github.com/anabaner/PinterestApp

Troubleshooting
- "Model download" or import errors: ensure `sentence-transformers` installed and you have network access for initial model download.
- Push failures due to large files: GitHub blocks files >100MB. If you accidentally committed large files, use `git rm --cached <file>` and rewrite history with the BFG or `git filter-branch` if necessary.
- Auth errors on push: create a GitHub personal access token (PAT) and use it as the password, or use the Git Credential Manager for Windows:
  - Create PAT at https://github.com/settings/tokens
  - Run `git push` and enter your username and the PAT when prompted.

Extending this project
- Add authentication and user accounts.
- Add pagination and filtering to GET /pins.
- Add a frontend (example Vite + React) that consumes this API and shows pins.

License
MIT — feel free to adapt this demo for learning and prototyping.

Acknowledgements
This project uses:
- FastAPI for the API server
- SQLAlchemy + SQLite for persistence
- ChromaDB + SentenceTransformers for embeddings and similarity
- Claude/Gemini for image auto-tagging examples


