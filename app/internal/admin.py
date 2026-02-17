from fastapi import APIRouter

router = APIRouter(
    prefix="/admin",
    tags=["Admin Only"],
    responses={404: {"description": "Not found"}}
)

@router.get("/stats")
async def get_system_stats():
    return {"total_users": 10, "active_themes": 5}