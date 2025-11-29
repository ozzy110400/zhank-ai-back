from fastapi import FastAPI, UploadFile, File
from .models import ImageAnalysisResponse
from .services import analyze_image

app = FastAPI()


@app.get("/health")
def read_root():
    return {"status": "ok"}


@app.post("/upload-image/", response_model=ImageAnalysisResponse)
async def upload_image(image: UploadFile = File(...)):
    """
    Accepts an image file, passes it to a service for analysis,
    and returns the analysis result.
    """

    return await analyze_image(image)
