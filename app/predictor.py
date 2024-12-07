import requests
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def analyze_weather_variations(weather_data):
    """
    Analyse les variations météorologiques sur la période
    Retourne un score de variation et un descriptif des changements
    """
    df = pd.DataFrame({
        'temperature': weather_data['hourly']['temperature_2m'],
        'humidity': weather_data['hourly']['relative_humidity_2m'],
        'precipitation': weather_data['hourly']['precipitation'],
        'wind_speed': weather_data['hourly']['wind_speed_10m']
    })
    
    # Calculer les variations
    variations = {
        'temp_variation': df['temperature'].std(),
        'humidity_variation': df['humidity'].std(),
        'wind_variation': df['wind_speed'].std(),
        'rain_episodes': len(df[df['precipitation'] > 0.5])  # Episodes de pluie > 0.5mm
    }
    
    # Calculer le nombre de changements significatifs
    significant_changes = 0
    weather_changes = []
    
    # Variation significative de température (plus de 5 degrés)
    temp_changes = df['temperature'].diff().abs() > 5
    if temp_changes.any():
        significant_changes += 1
        weather_changes.append("variations importantes de température")
    
    # Alternance pluie/sec
    rain_periods = (df['precipitation'] > 0.5).astype(int).diff().abs()
    if rain_periods.sum() > 4:  # Plus de 2 alternances pluie/sec
        significant_changes += 1
        weather_changes.append("alternances pluie/sec")
    
    # Variation significative d'humidité (plus de 20%)
    humidity_changes = df['humidity'].diff().abs() > 20
    if humidity_changes.any():
        significant_changes += 1
        weather_changes.append("variations importantes d'humidité")
    
    # Variation significative de vent (plus de 10 km/h)
    wind_changes = df['wind_speed'].diff().abs() > 10
    if wind_changes.any():
        significant_changes += 1
        weather_changes.append("variations importantes de vent")
    
    weather_score = min(significant_changes, 3)  # Score plafonné à 3
    variations['weather_score'] = weather_score
    variations['weather_changes'] = len(weather_changes)
    variations['weather_description'] = ", ".join(weather_changes) if weather_changes else "conditions stables"
    
    return variations

def evaluate_risk_level(conditions, lake_type):
    """
    Ajuste les seuils de risque selon le type de lac et les variations météo
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
            
    # Sol
    if conditions.get('soil_temp'):
        if conditions['soil_temp'] > 24:
            risk_score += 1
            if conditions['soil_temp'] > 26:
                high_risk += 1

    # Score des variations météo
    if 'weather_score' in conditions:
        risk_score += conditions['weather_score'] * 0.5  # Ajoute 0.5 point par niveau de variation
        if conditions['weather_score'] >= 2:
            high_risk += 1

    # Messages personnalisés selon les conditions
    weather_message = ""
    if 'weather_description' in conditions and conditions['weather_description'] != "conditions stables":
        weather_message = f" - Instabilité météo : {conditions['weather_description']}"

    # Just get  weather_description, weather_score, wind, temp, humidity, precip
    conditions = {k: v for k, v in conditions.items() if k in ['weather_description', 'wind', 'temp', 'humidity', 'precip']}
    # Drapeaux
    if risk_score <= 1.5:  # Seuil ajusté pour tenir compte des variations
        return "VERT", f"Risque faible{weather_message}", conditions
    elif risk_score <= 2.5 or high_risk == 0:
        return "ORANGE", f"Conditions favorables - Surveillance recommandée{weather_message}", conditions
    else:
        return "ROUGE", f"Conditions très favorables - Présence probable{weather_message}", conditions

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
    
    # Analyser les variations météo
    variations = analyze_weather_variations(weather_data)
    
    conditions = {
        'temp': round(df['temperature'].mean(), 1),
        'humidity': round(df['humidity'].mean(), 1),
        'wind': round(df['wind_speed'].mean(), 1),
        'soil_temp': round(df['soil_temp'].mean(), 1),
        'precip': round(df['precipitation'].sum(), 1),
        'soil_moisture': round(df['soil_moisture'].mean(), 1),
        'weather_score': variations['weather_score'],
        'weather_changes': variations['weather_changes'],
        'weather_description': variations['weather_description']
    }
    
    return conditions

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