import httpx
from fastapi import APIRouter, HTTPException, Query
from app.core.config import settings

router = APIRouter()

BASE_API_URL = "http://api.511.org/transit"

@router.get("/transit/destination_search")
async def get_destinations(operator_id: str = Query(..., description="Transit operator ID (e.g., 'SF')")):
    # Construct the API URL with the operator_id and API key
    api_url = f"{BASE_API_URL}/stopPlaces?api_key={settings.TRANSIT_API_KEY}&operator_id={operator_id}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
        response.raise_for_status()  # HTTPError for bad responses
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP error: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    if response.status_code == 200:
        data = response.json()

        # Extract the list of stops from the API response
        try:
            stop_places = data["Siri"]["ServiceDelivery"]["DataObjectDelivery"]["dataObjects"]["SiteFrame"]["stopPlaces"]["StopPlace"]
        except KeyError:
            raise HTTPException(status_code=404, detail="No stop places found.")
        
        # Filter stops based on accessibility (only include accessible stops)
        accessible_stops = [
            stop for stop in stop_places
            if stop.get("AccessibilityAssessment", {}).get("MobilityImpairedAccess") == "Yes"
        ]
        print(f"Number of accessible stops: {len(accessible_stops)}")

        # Simulate favorites and recent stops (replace with actual logic for your app)
        favorited_stop_ids = []  # Example of favorited stop IDs (could be replaced by actual user data)
        recently_visited_stop_ids = []  # Example of recent stops (could be replaced by actual user data)

        # Prioritize favorited and recently visited stops if available
        sorted_stops = sorted(accessible_stops, key=lambda stop: (
            stop["Name"] in favorited_stop_ids,   # Favorited first
            stop["Name"] in recently_visited_stop_ids  # Recently visited second
        ), reverse=True)
        
        print(f"Number of sorted stops: {len(sorted_stops)}")

        return {"sorted_stops": sorted_stops}

    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to get stop places")
