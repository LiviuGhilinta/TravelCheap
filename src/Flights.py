import requests
import os
from dotenv import load_dotenv

def search_flights(flight_type, departure, arrival, outbound_date, return_date, people):
    load_dotenv()
    Api_Key = os.getenv("SerpAPI")

    param = {
        "engine": "google_flights",
        "departure_id": departure,
        "arrival_id": arrival,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "currency": "RON",  
        "hl": "en",
        "api_key": Api_Key,
        "type": flight_type
    }

    resp = requests.get("https://serpapi.com/search", params=param)
    result = resp.json()
    
    flights_list = []
    
    for i in result.get("best_flights", [])[:3]:
        flight_info = i["flights"][0]
        flight_dict = {
            "airline": flight_info.get("airline", ""),
            "flight_number": flight_info.get("flight_number", ""),
            "departure_time": flight_info["departure_airport"].get("time", ""),
            "arrival_time": flight_info["arrival_airport"].get("time", ""),
            "duration": flight_info.get("duration", ""),
            "travel_class": flight_info.get("travel_class", ""),
            "price": i.get("price", ""),
            "airline_logo" : flight_info.get("airline_logo","")
        }
        flights_list.append(flight_dict)
    
    return flights_list

if __name__ =="__main__":
    pass    

