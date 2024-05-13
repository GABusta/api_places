import requests
import json
import os
from files.save_to_file import save_to_csv
from typing import List


def get_place_details(api_key: str, place_id: str, fields: list):
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {"key": api_key, "place_id": place_id, "fields": ",".join(fields)}
    response = requests.get(details_url, params=params)
    if response.status_code == 200:
        detail_results = json.loads(response.text)
        return detail_results.get("result", {})
    else:
        return {}


def find_places(api_key: str, location: str, keyword: str, extra_fields: List[str], radius: float):
    endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    places = []

    params = {
        "key": api_key,
        "location": location,  # center latitude, longitude
        "radius": radius,  # search radius in meters
        "keyword": keyword,
    }

    res = requests.get(endpoint_url, params=params)
    while res.status_code == 200:
        results = json.loads(res.text)
        for place in results["results"]:
            # Fetch additional details
            detailed_info = get_place_details(
                api_key=api_key, place_id=place["place_id"], fields=extra_fields
            )
            place.update(detailed_info)
            places.append(place)

        # places.extend(results["results"])
        if "next_page_token" in results:
            params["pagetoken"] = results["next_page_token"]
            res = requests.get(endpoint_url, params=params)
            continue
        break
    return places


def get_locations_from_centroids(model_name: str):
    centroid_coordinates = []
    centroids = f'map_coordinates/centroids/centroids_{model_name}.txt'
    with open(centroids, "r") as file:
        for line in file:
            lat, lon, radius = line.strip().split(',')
            centroid_coordinates.append([f'{lat},{lon}', float(radius)])
    return centroid_coordinates


if __name__ == "__main__":
    api_key = os.getenv("API_KEY")

    state = "buenos_aires"
    query = "veterinaria"
    extra_fields = ["formatted_phone_number", "website", "url", "address_component"]
    locations = get_locations_from_centroids(state)
    places = []

    locations = locations[0:6]

    filename = f"values_found_{state.replace(' ', '_')}.csv"
    is_header = True
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        for location, radius in locations:
            places_found = find_places(
                api_key=api_key,
                location=location,
                keyword=query,
                extra_fields=extra_fields,
                radius=radius,
                )
            if places_found:
                save_to_csv(places_found, file, is_header)
                # print(f"Data for {state} saved.")
            else:
                print(f"No data found for {state}.")
            is_header = False