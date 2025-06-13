import aiohttp
import logging
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
    
    async def _make_request(self, endpoint: str, method: str = "GET", params: Optional[Dict] = None, **kwargs) -> Dict[Any, Any]:
        """Make HTTP request to coverage service"""
        url = f"{self.api_base}/{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, params=params, **kwargs) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Resource not found in coverage service: {endpoint}"
                        )
                    else:
                        error_text = await response.text()
                        logger.error(f"Coverage service error {response.status}: {error_text}")
                        raise HTTPException(
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Coverage service unavailable: {response.status}"
                        )
        except aiohttp.ClientError as e:
            logger.error(f"Failed to connect to coverage service: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cannot connect to coverage service"
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
        data = await self._make_request("campuses/", params={"skip": skip, "limit": limit})
        return [CampusInfo(**campus) for campus in data]
    
    async def get_campus_by_id(self, campus_id: int) -> CampusInfo:
        """Get a specific campus by ID"""
        data = await self._make_request(f"campuses/{campus_id}")
        return CampusInfo(**data)
    
    async def get_institutions(self, skip: int = 0, limit: int = 1000) -> List[InstitutionInfo]:
        """Get all institutions from coverage service"""
        data = await self._make_request("institutions/", params={"skip": skip, "limit": limit})
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
                    detail=f"Invalid campus ID format: {campus_id}"
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
                    detail=f"Invalid town ID format: {town_id}"
                )
        return validated_towns

    async def validate_geographic_consistency(
        self, 
        campus_ids: List[str], 
        town_ids: List[str]
    ) -> None:
        """
        Validate that campuses belong to institutions in the specified towns.
        
        This method ensures geographic consistency by verifying that each campus
        belongs to an institution that is located in one of the specified towns.
        
        Args:
            campus_ids: List of campus IDs to validate
            town_ids: List of town IDs that should contain the campus institutions
            
        Raises:
            HTTPException: If any campus belongs to an institution outside specified towns
        """
        if not campus_ids or not town_ids:
            # If no campuses or no towns specified, no geographic validation needed
            return
        
        # Convert town_ids to integers for comparison
        try:
            town_id_ints = [int(town_id) for town_id in town_ids]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid town ID format in geographic validation: {str(e)}"
            )
        
        inconsistent_campuses = []
        
        for campus_id in campus_ids:
            try:
                # Get campus information
                campus = await self.get_campus_by_id(int(campus_id))
                
                # Get the institution that owns this campus
                institution = await self.get_institution_by_id(campus.institution_id)
                
                # Check if the institution's town is in the specified towns
                if institution.town_id not in town_id_ints:
                    # Get town name for better error message
                    try:
                        institution_town = await self.get_town_by_id(institution.town_id)
                        inconsistent_campuses.append({
                            'campus_name': campus.name,
                            'campus_id': campus_id,
                            'institution_name': institution.name,
                            'actual_town': institution_town.name,
                            'actual_town_id': institution.town_id
                        })
                    except Exception:
                        # Fallback if we can't get town name
                        inconsistent_campuses.append({
                            'campus_name': campus.name,
                            'campus_id': campus_id,
                            'institution_name': institution.name,
                            'actual_town': f"Town ID {institution.town_id}",
                            'actual_town_id': institution.town_id
                        })
                        
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid campus ID format: {campus_id}"
                )
            except HTTPException:
                # Re-raise HTTP exceptions (like 404 for missing resources)
                raise
            except Exception as e:
                logger.error(f"Unexpected error during geographic validation for campus {campus_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Error validating geographic consistency for campus {campus_id}"
                )
        
        if inconsistent_campuses:
            # Build detailed error message
            error_details = []
            for campus_info in inconsistent_campuses:
                error_details.append(
                    f"Campus '{campus_info['campus_name']}' (ID: {campus_info['campus_id']}) "
                    f"belongs to institution '{campus_info['institution_name']}' "
                    f"in town '{campus_info['actual_town']}' (ID: {campus_info['actual_town_id']})"
                )
            
            error_message = (
                "Geographic consistency validation failed. The following campuses belong to "
                f"institutions outside the specified towns: {'; '.join(error_details)}. "
                "Please ensure campuses are only assigned with their corresponding towns."
            )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

# Create singleton instance
coverage_service = CoverageService() 