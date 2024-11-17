"""
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.config import settings
import xmltodict

router = APIRouter()

BASE_API_URL = "http://api.511.org/transit"

#function to handle http request
async def get_data(client: httpx.AsyncClient, url: str):
    try:
        response = await client.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    return response




# Dependency to provide a reusable AsyncClient instance
async def get_http_client() -> httpx.AsyncClient:
    async with httpx.AsyncClient() as client:
        yield client

# StopPlace API: Provides stops with accessibility information
@router.get("/transit/accessible_stops")
async def get_accessible_stops(
    operator_id: str = Query(..., description="Transit operator ID (e.g., 'SF')"),
    client: httpx.AsyncClient = Depends(get_http_client),
):
    #get the data
    api_url = f"{BASE_API_URL}/stopPlaces?api_key={settings.TRANSIT_API_KEY}&operator_id={operator_id}"
    response = await get_data(client, api_url)

    # Parse the response
    try:
        data = response.json()
        stop_places = data["Siri"]["ServiceDelivery"]["DataObjectDelivery"]["dataObjects"]["SiteFrame"]["stopPlaces"]["StopPlace"]
    except KeyError:
        raise HTTPException(status_code=404, detail="No stop places found.")
    
    # Sort stops: MobilityImpairedAccess 'Yes' at the top, others at the bottom
    sorted_stops = sorted(
        stop_places,
        key=lambda stop: stop.get("AccessibilityAssessment", {}).get("MobilityImpairedAccess") != "Yes",
    )

    return {"accessible_stops": sorted_stops}

# Predictions API: Provides current arrival/departure times
@router.get("/transit/predictions")
async def get_real_time_predictions(
    operator_id: str = Query(..., description="Transit operator ID (e.g., 'SF')"),
    stop_id: str = Query(..., description="Transit stop ID"),
    client: httpx.AsyncClient = Depends(get_http_client),
):
    api_url = f"{BASE_API_URL}/StopMonitoring?api_key={settings.TRANSIT_API_KEY}&agency={operator_id}&stop_id={stop_id}"
    response = await get_data(client, api_url)

    try:
        data = response.json()
        predictions = data["Siri"]["ServiceDelivery"]["DataObjectDelivery"]["dataObjects"]["SiteFrame"]["stopPlaces"]["StopPlace"]
    except KeyError:
        raise HTTPException(status_code=404, detail="No predictions found.")

    return {"real_time_predictions": predictions}


# Patterns API: Helps users know the stop sequence and when to get off
@router.get("/transit/patterns")
async def get_route_patterns(
    operator_id: str = Query(..., description="Transit operator ID (e.g., 'SF')"),
    pattern_id: str = Query(..., description="Pattern ID for the transit route"),
    client: httpx.AsyncClient = Depends(get_http_client),
):
    api_url = f"{BASE_API_URL}/patterns?api_key={settings.TRANSIT_API_KEY}&operator_id={operator_id}&pattern_id={pattern_id}"
    response = await get_data(client, api_url)

    # Parse XML to dictionary
    try:
        data = xmltodict.parse(response.text)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to parse XML response.")

    return {"route_patterns": data}


# Scheduled Departures API: Provides scheduled departures for a specific stop
@router.get("/transit/schedule")
async def get_scheduled_departures(
    operator_id: str = Query(..., description="Transit operator ID (e.g., 'SF')"),
    stop_id: str = Query(..., description="Transit stop ID"),
    client: httpx.AsyncClient = Depends(get_http_client),
):
    api_url = f"{BASE_API_URL}/stoptimetable?api_key={settings.TRANSIT_API_KEY}&MonitoringRef={stop_id}&OperatorRef={operator_id}"
    response = await get_data(client, api_url)

"""  


#NEW CODEEE

import httpx
from fastapi import APIRouter, HTTPException, Query
from app.core.config import settings
from typing import List, Optional

router = APIRouter()

BASE_API_URL = "http://api.511.org/transit"

# Helper function to fetch stop places
async def fetch_stop_places(operator_id: str) -> dict:
    api_url = f"{BASE_API_URL}/stopPlaces?api_key={settings.TRANSIT_API_KEY}&operator_id={operator_id}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
 # Parse XML to dictionary
    try:
        data = xmltodict.parse(response.text)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to parse XML response.")

    return {"scheduled_departures": data}


@router.get("/transit/destination_search")
async def destination_search(
    operator_id: str = Query(..., description="Transit operator ID (e.g., 'SF')"),
    favorited_stop_ids: Optional[List[str]] = Query(None, description="List of favorited stop IDs"),
    recently_visited_stop_ids: Optional[List[str]] = Query(None, description="List of recently visited stop IDs"),
):
    """
    Fetch and return stop places prioritized by favorited, recently visited, and others, with filtering by accessibility.
    """
    # Fetch stop places from the 511 API
    data = await fetch_stop_places(operator_id)
    
    try:
        # Extract stop places from the response
        stop_places = data["Siri"]["ServiceDelivery"]["DataObjectDelivery"]["dataObjects"]["SiteFrame"]["stopPlaces"]["StopPlace"]
    except KeyError:
        raise HTTPException(status_code=404, detail="No stop places found.")
    
    # Prioritize stop places
    # 1. Favorited stops
    # 2. Recently visited stops
    # 3. All other stops
    prioritized_stops = []
    
    # Add favorited stops first
    if favorited_stop_ids:
        favorited_stops = [stop for stop in stop_places if stop["id"] in favorited_stop_ids]
        prioritized_stops.extend(favorited_stops)
    
    # Add recently visited stops next
    if recently_visited_stop_ids:
        recently_visited_stops = [stop for stop in stop_places if stop["id"] in recently_visited_stop_ids]
        prioritized_stops.extend(recently_visited_stops)
    
    # Add remaining stops
    remaining_stops = [stop for stop in stop_places if stop["id"] not in favorited_stop_ids and stop["id"] not in recently_visited_stop_ids]
    prioritized_stops.extend(remaining_stops)
    
    # Filter by accessibility (only include stops with "MobilityImpairedAccess" marked as "Yes")
    accessible_stops = [stop for stop in prioritized_stops if stop.get("AccessibilityAssessment", {}).get("MobilityImpairedAccess") == "Yes"]

    # Return the accessible stops
    return {"accessible_stops": accessible_stops}
 