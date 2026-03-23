from fastapi import APIRouter

from src.modules.health.api.v1.health import router as health_router
from src.modules.post.api.v1.comments import router as comment_router
from src.modules.post.api.v1.posts import router as post_router
from src.modules.user.api.v1.login import router as login_router
from src.modules.user.api.v1.logout import router as logout_router
from src.modules.user.api.v1.users import router as user_router

router = APIRouter()

router.include_router(login_router, prefix="/api/v1")
router.include_router(logout_router, prefix="/api/v1")
router.include_router(user_router, prefix="/api/v1")
router.include_router(health_router, prefix="/api/v1")
router.include_router(post_router, prefix="/api/v1")
router.include_router(comment_router, prefix="/api/v1")
