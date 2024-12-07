import requests
from datetime import datetime, timedelta
import pandas as pd

def evaluate_risk_level(conditions, lake_type):
    """
    Ajuste les seuils de risque selon le type de lac
    Types: 'forest', 'agriculture', 'urban'
    """
    risk_score = 0
    high_risk = 0
    
    # Ajustement des seuils selon le type de lac
    temp_threshold = {
        'forest': {'base': 23, 'high': 25},
        'agriculture': {'base': 24, 'high': 26},
        'urban': {'base': 25, 'high': 27}
    }[lake_type]
    
    # Seuils fixes sans stratification
    humidity_threshold = {'base': 65, 'high': 75}
    wind_threshold = {'base': 10, 'high': 7}

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
    
    if conditions.get('soil_temp') is not None:
        # Sol (commun à tous les types)
        if conditions['soil_temp'] > 24:
            risk_score += 1
            if conditions['soil_temp'] > 26:
                high_risk += 1

    # Drapeaux
    if risk_score <= 1:
        return "VERT", "Risque faible", conditions
    elif risk_score <= 2 or high_risk == 0:
        return "ORANGE", "Conditions favorables - Surveillance recommandée", conditions
    else:
        return "ROUGE", "Conditions très favorables - Présence probable", conditions

def get_forecast_data(latitude, longitude, date):
    """
    Récupère les données de prévision météo pour les dates futures
    """
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date,
        "end_date": date,
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
    print(response.json())
    return response.json()

def get_historical_data(latitude, longitude, date):
    """
    Récupère les données météo historiques
    """
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    end_date = datetime.strptime(date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=7)
    
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
        'temp': round(df['temperature'].mean(), 1),
        'humidity': round(df['humidity'].mean(), 1),
        'wind': round(df['wind_speed'].mean(), 1),
        'precip': round(df['precipitation'].sum(), 1),
   }

def predict_for_date(latitude, longitude, date, lake_type):
    try:
        # Vérifier si la date est dans le futur
        target_date = datetime.strptime(date, "%Y-%m-%d")
        current_date = datetime.now()
        
        if target_date > current_date:
            weather_data = get_forecast_data(latitude, longitude, date)
        else:
            weather_data = get_historical_data(latitude, longitude, date)
            
        conditions = get_conditions(weather_data)
        return evaluate_risk_level(conditions, lake_type)
    except Exception as e:
        print(f"Erreur : {e}")
        raise e