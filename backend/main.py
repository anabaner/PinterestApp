from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from upload import save_upload
from agent import auto_tag_image
from embeddings import add_pin_embedding, get_similar_pin_ids, delete_pin_embedding

from database import engine, get_db, Base
from models import Pin
from schemas import PinCreate, PinUpdate, PinResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Pinterest Clone API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/pins", response_model=PinResponse, status_code=201)
async def create_pin(pin: PinCreate, db: AsyncSession = Depends(get_db)):
    new_pin = Pin(**pin.model_dump())
    db.add(new_pin)
    await db.commit()
    await db.refresh(new_pin)
    return new_pin


@app.get("/pins", response_model=List[PinResponse])
async def get_all_pins(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Pin).order_by(Pin.created_at.desc()))
    return result.scalars().all()


@app.get("/pins/{pin_id}", response_model=PinResponse)
async def get_pin(pin_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Pin).where(Pin.id == pin_id))
    pin = result.scalar_one_or_none()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    return pin


@app.patch("/pins/{pin_id}", response_model=PinResponse)
async def update_pin(pin_id: int, updates: PinUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Pin).where(Pin.id == pin_id))
    pin = result.scalar_one_or_none()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    for field, value in updates.model_dump(exclude_none=True).items():
        setattr(pin, field, value)
    await db.commit()
    await db.refresh(pin)
    return pin


@app.delete("/pins/{pin_id}", status_code=204)
async def delete_pin(pin_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Pin).where(Pin.id == pin_id))
    pin = result.scalar_one_or_none()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    await db.delete(pin)
    await db.commit()
    delete_pin_embedding(pin_id)  # clean up the vector too

# # ── UPLOAD IMAGE + CREATE PIN ────────────────────────────
# @app.post("/pins/upload", response_model=PinResponse, status_code=201)
# async def upload_pin(
#     title: str,
#     file: UploadFile = File(...),
#     description: str = "",
#     tags: str = "",
#     board: str = "General",
#     db: AsyncSession = Depends(get_db)
# ):
#     # Save image to disk, get back the URL
#     image_url = await save_upload(file)
#
#     # Create the pin record in the database
#     new_pin = Pin(
#         title=title,
#         image_url=image_url,
#         description=description,
#         tags=tags,
#         board=board
#     )
#     db.add(new_pin)
#     await db.commit()
#     await db.refresh(new_pin)
#     return new_pin

#Upload Pin with Claude Auto Tagging
@app.post("/pins/upload", response_model=PinResponse, status_code=201)
async def upload_pin(
    file: UploadFile = File(...),
    board: str = "General",
    db: AsyncSession = Depends(get_db)
):
    # Step 1: Save the image to disk
    image_url = await save_upload(file)

    # Step 2: Build the local file path so Claude can read it
    image_path = image_url.lstrip("/")  # "static/uploads/abc123.jpg"

    # Step 3: Ask Claude to analyze the image
    tags_data = auto_tag_image(image_path)

    # Step 4: Create the pin using Claude's suggestions
    new_pin = Pin(
        title=tags_data.get("title", "Untitled Pin"),
        description=tags_data.get("description", ""),
        tags=tags_data.get("tags", ""),
        image_url=image_url,
        board=board
    )
    db.add(new_pin)
    await db.commit()
    await db.refresh(new_pin)
    # Step 4: Store embedding for similarity search
    add_pin_embedding(
        pin_id=new_pin.id,
        title=new_pin.title,
        description=new_pin.description,
        tags=new_pin.tags
    )
    return new_pin

# ── SIMILAR PINS ─────────────────────────────────────────
@app.get("/pins/{pin_id}/similar", response_model=List[PinResponse])
async def get_similar_pins(pin_id: int, db: AsyncSession = Depends(get_db)):
    # Confirm the pin exists
    result = await db.execute(select(Pin).where(Pin.id == pin_id))
    pin = result.scalar_one_or_none()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    from embeddings import debug_distances
    debug_distances(pin_id)
    # Get similar pin IDs from ChromaDB
    similar_ids = get_similar_pin_ids(pin_id, n=3)
    if not similar_ids:
        return []

    # Fetch those pins from the database
    result = await db.execute(
        select(Pin).where(Pin.id.in_(similar_ids))
    )
    return result.scalars().all()

@app.post("/admin/reindex", status_code=200)
async def reindex_all_pins(db: AsyncSession = Depends(get_db)):
    """Re-add all existing pins to ChromaDB. Run once after changing collection."""
    result = await db.execute(select(Pin))
    pins = result.scalars().all()

    for pin in pins:
        add_pin_embedding(
            pin_id=pin.id,
            title=pin.title,
            description=pin.description,
            tags=pin.tags
        )

    return {"message": f"Reindexed {len(pins)} pins successfully"}