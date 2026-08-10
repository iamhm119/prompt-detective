"""
Main API router combining all v1 endpoints
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .uploads import router as upload_router
from .jobs import router as jobs_router
from .api_keys import router as api_keys_router
from .admin import router as admin_router
from .usage import router as usage_router

# Import payment and trial routes
from ...api.routes.payments import router as payments_router
from ...api.routes.trials import router as trials_router
from ...api.routes.contact import router as contact_router
from ...api.routes.waitlist import router as waitlist_router
from .account import router as account_router

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(upload_router)
api_router.include_router(jobs_router)
api_router.include_router(api_keys_router)
api_router.include_router(admin_router)
api_router.include_router(usage_router)
api_router.include_router(payments_router)  # Payment gateway routes
api_router.include_router(trials_router)    # Trial management routes
api_router.include_router(contact_router)   # Support & contact routes
api_router.include_router(waitlist_router)  # Waitlist / coming soon subscriptions
api_router.include_router(account_router)   # Account lifecycle endpoints