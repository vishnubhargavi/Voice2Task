from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import uuid

from ai import process_audio


# ---------------------------------------------------------
# APP
# ---------------------------------------------------------

app = FastAPI(
    title="Voice2Task API",
    description="Convert voice messages into transcripts, summaries and tasks.",
    version="1.0"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# TEMP AUDIO DIRECTORY
# ---------------------------------------------------------

UPLOAD_DIR = "temp_audio"

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "Voice2Task API is running!"
    }


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# ---------------------------------------------------------
# PROCESS AUDIO
# ---------------------------------------------------------

@app.post("/process")
async def process_voice(audio: UploadFile = File(...)):

    if not audio:
        raise HTTPException(
            status_code=400,
            detail="No audio file received."
        )

    # Generate unique filename
    file_id = str(uuid.uuid4())

    original_name = audio.filename or "audio.webm"

    extension = os.path.splitext(original_name)[1]

    if not extension:
        extension = ".webm"

    filename = file_id + extension

    filepath = os.path.join(
        UPLOAD_DIR,
        filename
    )

    try:

        # Save uploaded audio
        with open(filepath, "wb") as buffer:

            shutil.copyfileobj(
                audio.file,
                buffer
            )

        print()
        print("=" * 50)
        print("VOICE2TASK")
        print("=" * 50)
        print("Received:", original_name)
        print("Saved:", filepath)
        print("Processing audio...")
        print("=" * 50)

        # Process audio
        result = process_audio(filepath)

        print()
        print("Processing completed!")
        print("=" * 50)

        return result

    except Exception as e:

        print()
        print("ERROR:")
        print(str(e))
        print("=" * 50)

        raise HTTPException(
            status_code=500,
            detail=f"Audio processing failed: {str(e)}"
        )

    finally:

        # Delete temporary audio file
        if os.path.exists(filepath):

            try:
                os.remove(filepath)

            except Exception:
                pass