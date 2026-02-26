from fastapi import APIRouter
from .items_router import router as items_router
from .inventory_router import router as inventory_router
from .outbound_router import router as outbound_router
from .sku_router import router as sku_router
from .location_router import router as location_router
from .dashboard_router import router as dashboard_router
from .machine_router import router as machine_router

# 创建主路由
api_router = APIRouter()

# 挂载子路由
api_router.include_router(dashboard_router)
api_router.include_router(sku_router)
api_router.include_router(items_router)
api_router.include_router(location_router)
api_router.include_router(inventory_router)
api_router.include_router(outbound_router)
api_router.include_router(machine_router)