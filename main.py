import requests
import json
import csv
import os 


def find_vet_clinics(api_key, location, term="veterinary_care"):
    endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    places = []
    params = {
        "key": api_key,
        "location": location,  # latitude,longitude for the center of the search
        "radius": 50000,  # search radius in meters
        "keyword": term  # additional search keyword
    }

    res = requests.get(endpoint_url, params=params)
    while res.status_code == 200:
        results = json.loads(res.text)
        places.extend(results['results'])
        if "next_page_token" in results:
            params['pagetoken'] = results['next_page_token']
            res = requests.get(endpoint_url, params=params)
            continue
        break
    return places

def save_to_csv(places, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Website', 'Address', 'Latitude', 'Longitude'])
        for place in places:
            name = place.get('name', 'No Name')
            website = place.get('website', 'No Website')
            address = place.get('vicinity', 'No Address')
            location = place.get('geometry', {}).get('location', {})
            lat = location.get('lat', '')
            lng = location.get('lng', '')
            writer.writerow([name, website, address, lat, lng])


if "__name__" == "__main__":
    locations = [
        ("-34.603722,-58.381592", "Buenos Aires")
    ]

    api_key = os.getenv("API_KEY")

    for location, state in locations:
        print(f"Searching in {state}...")
        vet_clinics = find_vet_clinics(api_key, location, term="veterinaria")
        if vet_clinics:
            save_to_csv(vet_clinics, f"vet_clinics_{state.replace(' ', '_')}.csv")
            print(f"Data for {state} saved.")
        else:
            print(f"No data found for {state}.")
