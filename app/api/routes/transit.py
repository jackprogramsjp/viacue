import httpx
from fastapi import APIRouter, HTTPException, Query
from app.core.config import settings
import xmltodict

router = APIRouter()

BASE_API_URL = "http://api.511.org/transit"

# StopPlace API: Provides stops with accessibility information
@router.get("/transit/accessible_stops")
async def get_accessible_stops(operator_id: str = Query(..., description="Transit operator ID (e.g., 'SF')")):
    api_url = f"{BASE_API_URL}/stopPlaces?api_key={settings.TRANSIT_API_KEY}&operator_id={operator_id}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    # Check if data is accessible then get the "Siri" key from the JSON response
    if response.status_code == 200:
        data = response.json()

        # Extract stop places from the "Siri" key -> "ServiceDelivery" -> "DataObjectDelivery" -> "dataObjects"
        try:
            stop_places = data["Siri"]["ServiceDelivery"]["DataObjectDelivery"]["dataObjects"]["SiteFrame"]["stopPlaces"]["StopPlace"]
        except KeyError:
            raise HTTPException(status_code=404, detail="No stop places found.")
        
        # Sort stops: MobilityImpairedAccess 'Yes' at the top, others at the bottom
        sorted_stops = sorted(stop_places, key=lambda stop: stop.get('AccessibilityAssessment', {}).get('MobilityImpairedAccess') != 'Yes')

        # Return the sorted stops
        return {"accessible_stops": sorted_stops}



# Predictions API: Provides current arrival/departure times
@router.get("/transit/predictions")
async def get_real_time_predictions(
    operator_id: str = Query(..., description="Transit operator ID (e.g., 'SF')"),
    stop_id: str = Query(..., description="Transit stop ID")
):
    """
    Fetch real-time arrival predictions for a specific stop.
    """
    api_url = f"{BASE_API_URL}/StopMonitoring?api_key={settings.TRANSIT_API_KEY}&agency={operator_id}&stop_id={stop_id}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    if response.status_code == 200:
        # Access the "Siri" key from the JSON response
        data = response.json()

        # Extract real-time predictions from the "Siri" key -> "ServiceDelivery" -> "DataObjectDelivery" -> "dataObjects"
        try:
            predictions = data["Siri"]["ServiceDelivery"]["DataObjectDelivery"]["dataObjects"]["SiteFrame"]["stopPlaces"]["StopPlace"]
        except KeyError:
            raise HTTPException(status_code=404, detail="No predictions found.")
        
        return {"real_time_predictions": predictions}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch real-time predictions")


# Patterns API: Helps users know the stop sequence and when to get off
@router.get("/transit/patterns")
async def get_route_patterns(
    operator_id: str = Query(..., description="Transit operator ID (e.g., 'SF')"),
    pattern_id: str = Query(..., description="Pattern ID for the transit route")
):
    """
    Fetch route patterns for a transit operator and pattern ID.
    """
    api_url = f"{BASE_API_URL}/patterns?api_key={settings.TRANSIT_API_KEY}&operator_id={operator_id}&pattern_id={pattern_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)

    if response.status_code == 200:
        # Parse XML to dictionary
        data = xmltodict.parse(response.text)
        return {"route_patterns": data}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch route patterns")


#Transit Scheduled Departures for a Stop API:
# Scheduled departures ensure reliability when real-time data is unavailable
@router.get("/transit/schedule")
async def get_scheduled_departures(
    operator_id: str = Query(..., description="Transit operator ID (e.g., 'SF')"),
    stop_id: str = Query(..., description="Transit stop ID")
):
    """
    Fetch scheduled departures for a specific stop.
    """
    api_url = f"{BASE_API_URL}/stoptimetable?api_key={settings.TRANSIT_API_KEY}&MonitoringRef={stop_id}&OperatorRef={operator_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url)

    if response.status_code == 200:
        # Parse XML to dictionary
        data = xmltodict.parse(response.text)
        return {"scheduled_departures": data}
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch scheduled departures")