from pydantic import BaseModel

class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "default"
