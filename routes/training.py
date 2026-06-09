import os
from fastapi import APIRouter, Header, HTTPException, status, Response
from fastapi.responses import JSONResponse
from services.training import train_model

router = APIRouter()

@router.get("/train")
async def trainRouteClient(x_training_api_key: str = Header(default="")):
    expected_key = os.getenv("TRAINING_API_KEY")
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training is disabled in this environment.",
        )
    if x_training_api_key != expected_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        train_model()
        return Response("Training successful !!")
    except Exception as e:
        import logging as app_logging
        app_logging.exception("Training failed:")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": False, "error": f"Training failed: {str(e)}"},
        )
