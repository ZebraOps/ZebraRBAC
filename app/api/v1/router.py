from fastapi import APIRouter

from app.api.v1.endpoints import (login, users, groups, roles, functions, menus, components, authorization,
                                  organizations, positions, user_organizations, jobs)

api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(groups.router, prefix="/groups", tags=["groups"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(functions.router, prefix="/functions", tags=["functions"])
api_router.include_router(menus.router, prefix="/menus", tags=["menus"])
api_router.include_router(components.router, prefix="/components", tags=["components"])
api_router.include_router(authorization.router, prefix="/authorization", tags=["authorization"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(positions.router, prefix="/positions", tags=["positions"])
api_router.include_router(user_organizations.router, prefix="/user-organizations", tags=["user_organizations"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
