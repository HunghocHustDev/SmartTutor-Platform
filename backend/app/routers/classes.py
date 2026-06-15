from app.routers import class_finance
from app.routers.class_profiles import router


router.include_router(class_finance.router)
