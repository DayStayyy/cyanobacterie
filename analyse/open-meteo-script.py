import requests
from datetime import datetime, timedelta
import pandas as pd

def evaluate_risk_level(conditions, lake_type, stratification):
    """
    Ajuste les seuils de risque selon le type de lac
    Types: 'forest', 'agriculture', 'urban'
    Stratification: 'strong', 'weak', 'none'
    """
    risk_score = 0
    high_risk = 0
    
    # Ajustement des seuils selon le type de lac
    temp_threshold = {
        'forest': {'base': 23, 'high': 25},
        'agriculture': {'base': 24, 'high': 26},
        'urban': {'base': 25, 'high': 27}
    }[lake_type]
    
    humidity_threshold = {
        'strong': {'base': 70, 'high': 80},
        'weak': {'base': 65, 'high': 75},
        'none': {'base': 60, 'high': 70}
    }[stratification]
    
    wind_threshold = {
        'strong': {'base': 8, 'high': 5},
        'weak': {'base': 10, 'high': 7},
        'none': {'base': 12, 'high': 9}
    }[stratification]

    # Température
    if conditions['temp'] >= temp_threshold['base']:
        risk_score += 1
        if conditions['temp'] >= temp_threshold['high']:
            high_risk += 1
            
    # Humidité
    if conditions['humidity'] > humidity_threshold['base']:
        risk_score += 1
        if conditions['humidity'] > humidity_threshold['high']:
            high_risk += 1
    
    # Vent
    if conditions['wind'] < wind_threshold['base']:
        risk_score += 1
        if conditions['wind'] < wind_threshold['high']:
            high_risk += 1
            
    if(conditions['soil_temp']):
        # Sol (commun à tous les types)
        if conditions['soil_temp'] > 24:
            risk_score += 1
            if conditions['soil_temp'] > 26:
                high_risk += 1

    # Drapeaux
    if risk_score <= 1:
        return "VERT", "Risque faible"
    elif risk_score <= 2 or high_risk == 0:
        return "ORANGE", "Conditions favorables - Surveillance recommandée"
    else:
        return "ROUGE", "Conditions très favorables - Présence probable"


def get_weather_data(latitude, longitude, date):
    """
    Récupère les données météo des 7 derniers jours
    """
    end_date = datetime.strptime(date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=7)
    
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "hourly": [
            "temperature_2m", 
            "relative_humidity_2m", 
            "precipitation", 
            "wind_speed_10m", 
            "soil_temperature_0_to_7cm",
            "soil_moisture_0_to_7cm"
        ]
    }
    
    response = requests.get(base_url, params=params)
    return response.json()

def get_conditions(weather_data):
    """
    Calcule les conditions moyennes sur la période
    """
    df = pd.DataFrame({
        'temperature': weather_data['hourly']['temperature_2m'],
        'humidity': weather_data['hourly']['relative_humidity_2m'],
        'precipitation': weather_data['hourly']['precipitation'],
        'wind_speed': weather_data['hourly']['wind_speed_10m'],
        'soil_temp': weather_data['hourly']['soil_temperature_0_to_7cm'],
        'soil_moisture': weather_data['hourly']['soil_moisture_0_to_7cm']
    })
    
    return {
        'temp': df['temperature'].mean(),
        'humidity': df['humidity'].mean(),
        'wind': df['wind_speed'].mean(),
        'soil_temp': df['soil_temp'].mean(),
        'precip': df['precipitation'].sum(),
        'soil_moisture': df['soil_moisture'].mean()
    }

def main(latitude, longitude, date, lake_type, stratification):
    try:
        weather_data = get_weather_data(latitude, longitude, date)
        conditions = get_conditions(weather_data)
        risk_analysis = evaluate_risk_level(conditions, lake_type, stratification)
        
        print(f"\nType de lac: {lake_type}")
        print(f"Stratification: {stratification}")
        print(f"Drapeau : {risk_analysis[0]}")
        print(f"Message : {risk_analysis[1]}")
        # print("\nConditions :")
        # for key, value in conditions.items():
        #     print(f"{key}: {value:.2f}")
        
        return risk_analysis
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    # Coordonnées à modifier selon votre besoin
    print("BRR :")
    # main(latitude=37.3386, longitude=-83.4707, date="1988-07-15") # BHR
    # main(latitude=37.3386, longitude=-83.4707, date="1992-07-15") # BHR
    # main(latitude=37.3386, longitude=-83.4707, date="1995-07-15") # BHR
    # main(latitude=37.3386, longitude=-83.4707, date="2000-07-15") # BHR
    # main(latitude=37.3386, longitude=-83.4707, date="2004-07-15") # BHR
    # main(latitude=37.3386, longitude=-83.4707, date="2008-07-15") # BHR

    # main(latitude=36.892, longitude=-86.1225, date="1988-07-15", lake_type="forest",stratification="strong")


    # main(latitude=40.7143, longitude=-85.9561, date="1988-07-15") # MSR
    # main(latitude=38.434, longitude=-86.7046, date="1988-07-15") # PRR

    date = "2010-01-15"
    for i in range(12):
        print
        main(latitude=37.3386, longitude=-83.4707, date=date, lake_type="forest", stratification="strong")
        # add 1 month
        date = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=30)
        date = date.strftime("%Y-%m-%d")

