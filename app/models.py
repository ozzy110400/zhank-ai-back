from pydantic import BaseModel


class ImageAnalysisResponse(BaseModel):
    """
    Represents the response from the image analysis service.
    """
    description: str
    tags: list[str]
