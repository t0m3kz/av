# SPDX-License-Identifier: Apache-2.0
"""Main device API router that combines inventory and configuration management.

Follows FastAPI best practices with clean separation of concerns.
"""

from fastapi import APIRouter

from spatium.api import containerlab_inventory, deployment
from spatium.api.routers.device_config import router as config_router
from spatium.api.routers.inventory import router as inventory_router

# Main device router that combines all device-related endpoints
router = APIRouter()

# Include sub-routers
router.include_router(inventory_router, prefix="/topology")
router.include_router(config_router)

# --- Import other routers at the end to avoid circular import ---
router.include_router(containerlab_inventory.router)
router.include_router(deployment.router)
