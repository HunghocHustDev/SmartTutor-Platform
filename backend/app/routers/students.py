from app.routers import student_relations
from app.routers.student_profiles import router


router.include_router(student_relations.router)
