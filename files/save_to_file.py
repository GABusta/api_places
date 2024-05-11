import csv


def save_to_csv(places, filename: str) -> None:
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Name",
                "Phone Number",
                "Website",
                "url",
                "Address",
                "Latitude",
                "Longitude",
                "street num",
                "street",
                "neighborhood",
                "locality",
                "postal_code",
            ]
        )
        for place in places:
            name = place.get("name", "No Name")
            phone_number = place.get("formatted_phone_number", "No phone-number")
            website = place.get("website", "No Website")
            URL = place.get("url", "No url")
            address = place.get("vicinity", "No Address")
            location = place.get("geometry", {}).get("location", {})
            lat = location.get("lat", "")
            lng = location.get("lng", "")

            street_num = ''
            street = ''
            neighborhood = ''
            locality = ''
            postal_code = ''

            for component in place.get("address_components", []):
                if 'street_number' in component.get("types", []):
                    street_num = component.get("long_name", "")
                elif 'route' in component.get("types", []):
                    street = component.get("long_name", "")
                elif 'sublocality' in component.get("types", []):
                    neighborhood = component.get("long_name", "")
                elif 'locality' in component.get("types", []):
                    locality = component.get("short_name", "")
                elif 'postal_code' in component.get("types", []):
                    postal_code = component.get("long_name", "")

            writer.writerow(
                [
                    name,
                    phone_number,
                    website,
                    URL,
                    address,
                    lat,
                    lng,
                    street_num,
                    street,
                    neighborhood,
                    locality,
                    postal_code,
                ]
            )
