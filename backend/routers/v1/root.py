from datetime import datetime

from fastapi import APIRouter

router = APIRouter(tags=["Root"])


@router.get("/")
async def root_endpoint():
    """
    Root endpoint. It returns message "App is up and running" and datetime when executed
    """

    time = datetime.now().strftime("%d-%B-%Y, %I:%M:%S %p")

    return {"message": "App is up and running", "time": time}
