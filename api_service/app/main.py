from fastapi import FastAPI, HTTPException, Response
from .schemas import SynthesizeRequest
from .validation import validate_text
from .tts_client import synthesize_text

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/synthesize")
def synthesize(request: SynthesizeRequest):
    try:
        validate_text(request.text, request.language)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    
    audio_data = synthesize_text(request.text, request.voice, request.language, request.environment)

    return Response(
        content=audio_data,
        media_type="audio/wav",
    )
