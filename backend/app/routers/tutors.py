from app.routers import tutor_availabilities, tutor_capabilities
from app.routers.tutor_profiles import router


router.include_router(tutor_capabilities.router)
router.include_router(tutor_availabilities.router)
