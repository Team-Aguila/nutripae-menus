import aiohttp
import logging
import os
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class CampusInfo(BaseModel):
    id: int
    name: str
    dane_code: str
    institution_id: int
    address: str
    latitude: float
    longitude: float


class TownInfo(BaseModel):
    id: int
    name: str
    dane_code: str
    department_id: int


class InstitutionInfo(BaseModel):
    id: int
    name: str
    dane_code: str
    town_id: int
    number_of_campuses: int


class CoverageService:
    """Service to communicate with the external coverage service"""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"

    async def get_auth_admin_token(self, **kwargs) -> str:
        NUTRIPAE_AUTH_HOST = os.getenv("NUTRIPAE_AUTH_HOST", "nutripae-auth-api")
        NUTRIPAE_AUTH_PORT = os.getenv("NUTRIPAE_AUTH_PORT", "8000")
        NUTRIPAE_AUTH_PREFIX = os.getenv("NUTRIPAE_AUTH_PREFIX", "/api/v1")

        url = f"http://{NUTRIPAE_AUTH_HOST}:{NUTRIPAE_AUTH_PORT}{NUTRIPAE_AUTH_PREFIX}/auth/login"
        payload = {
            "email": "admin@test.com",
            "password": "Password123!",  # YO SE QUE ES UN MACHETAZO, PERO ES PARA PRUEBAS
        }
        headers = {"Content-Type": "application/json"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("access_token", "")
                    else:
                        logger.error(
                            f"Failed to retrieve admin token: {response.status}"
                        )
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Could not retrieve admin token",
                        )
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cannot connect to auth service",
            )

    async def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        **kwargs,
    ) -> Dict[Any, Any]:
        """Make HTTP request to coverage service"""
        url = f"{self.api_base}/{endpoint}"

        token = await self.get_auth_admin_token()
        if not token:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Admin token not available",
            )
        headers = {"Authorization": f"Bearer {token}"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method, url, params=params, headers=headers, **kwargs
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Resource not found in coverage service: {endpoint}",
                        )
                    else:
                        error_text = await response.text()
                        logger.error(
                            f"Coverage service error {response.status}: {error_text}"
                        )
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Coverage service unavailable: {response.status}",
                        )
        except aiohttp.ClientError as e:
            logger.error(f"Failed to connect to coverage service: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cannot connect to coverage service",
            )

    async def get_towns(self, skip: int = 0, limit: int = 1000) -> List[TownInfo]:
        """Get all towns from coverage service"""
        data = await self._make_request("towns/", params={"skip": skip, "limit": limit})
        return [TownInfo(**town) for town in data]

    async def get_town_by_id(self, town_id: int) -> TownInfo:
        """Get a specific town by ID"""
        data = await self._make_request(f"towns/{town_id}")
        return TownInfo(**data)

    async def get_campuses(self, skip: int = 0, limit: int = 1000) -> List[CampusInfo]:
        """Get all campuses from coverage service"""
        data = await self._make_request(
            "campuses/", params={"skip": skip, "limit": limit}
        )
        return [CampusInfo(**campus) for campus in data]

    async def get_campus_by_id(self, campus_id: int) -> CampusInfo:
        """Get a specific campus by ID"""
        data = await self._make_request(f"campuses/{campus_id}")
        return CampusInfo(**data)

    async def get_institutions(
        self, skip: int = 0, limit: int = 1000
    ) -> List[InstitutionInfo]:
        """Get all institutions from coverage service"""
        data = await self._make_request(
            "institutions/", params={"skip": skip, "limit": limit}
        )
        return [InstitutionInfo(**institution) for institution in data]

    async def get_institution_by_id(self, institution_id: int) -> InstitutionInfo:
        """Get a specific institution by ID"""
        data = await self._make_request(f"institutions/{institution_id}")
        return InstitutionInfo(**data)

    async def validate_campus_ids(self, campus_ids: List[str]) -> List[CampusInfo]:
        """Validate that campus IDs exist and return their info"""
        validated_campuses = []
        for campus_id in campus_ids:
            try:
                campus = await self.get_campus_by_id(int(campus_id))
                validated_campuses.append(campus)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid campus ID format: {campus_id}",
                )
        return validated_campuses

    async def validate_town_ids(self, town_ids: List[str]) -> List[TownInfo]:
        """Validate that town IDs exist and return their info"""
        validated_towns = []
        for town_id in town_ids:
            try:
                town = await self.get_town_by_id(int(town_id))
                validated_towns.append(town)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid town ID format: {town_id}",
                )
        return validated_towns


# Create singleton instance
NUTRIPAE_COVERAGE_HOST = os.getenv("NUTRIPAE_COVERAGE_HOST", "nutripae-cobertura-api")
NUTRIPAE_COVERAGE_PORT = os.getenv("NUTRIPAE_COVERAGE_PORT", "8000")

coverage_service = CoverageService(
    base_url=f"http://{NUTRIPAE_COVERAGE_HOST}:{NUTRIPAE_COVERAGE_PORT}"
)
