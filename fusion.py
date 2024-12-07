import pandas as pd
from datetime import datetime, timedelta
import requests

def analyze_cyano_presence(file_path, target_lake):
    df = pd.read_excel(file_path, sheet_name='All_data')
    df['date'] = pd.to_datetime(df['date'])
    lake_data = df[df['reservoir'] == target_lake]

    daily_data = []
    for date, group in lake_data.groupby('date'):
        toxic_samples = group[group['toxin'] == 1]
        daily_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'total_density': group['density_cells/ml'].sum(),
            'toxic_density': toxic_samples['density_cells/ml'].sum(),
            'risk_level': get_risk_level(toxic_samples['density_cells/ml'].sum())
        })
    return pd.DataFrame(daily_data).sort_values('date')

def get_risk_level(toxic_density):
    if toxic_density > 100:
        return "ROUGE"
    elif toxic_density > 50:
        return "ORANGE"
    return "VERT"

def get_weather_data(latitude, longitude, date):
    end_date = datetime.strptime(date, "%Y-%m-%d")
    start_date = end_date - timedelta(days=7)
    
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "soil_temperature_0_to_7cm"]
    }
    
    response = requests.get(base_url, params=params)
    return response.json()

def get_conditions(weather_data):
    df = pd.DataFrame({
        'temperature': weather_data['hourly']['temperature_2m'],
        'humidity': weather_data['hourly']['relative_humidity_2m'],
        'wind': weather_data['hourly']['wind_speed_10m'],
        'soil_temp': weather_data['hourly']['soil_temperature_0_to_7cm']
    })
    return {
        'temp': df['temperature'].mean(),
        'humidity': df['humidity'].mean(),
        'wind': df['wind'].mean(),
        'soil_temp': df['soil_temp'].mean()
    }

def evaluate_risk(latitude, longitude, lake_name, lake_type, stratification):
    cyano_data = analyze_cyano_presence("./data2/cyanotoxin-taxa-data-xlsx-3.xls", lake_name)

    count_vert = 0
    count_orange = 0
    count_rouge = 0
    count_rouge_to_orange = 0
    count_rouge_to_vert = 0
    count_vert_to_rouge = 0
    count_vert_to_orange = 0
    count_orange_to_rouge = 0
    count_orange_to_vert = 0

    for i, row in cyano_data.iterrows():
        weather_data = get_weather_data(latitude, longitude, row['date'])
        weather_conditions = get_conditions(weather_data)
        risk_analysis = evaluate_risk_level(weather_conditions, lake_type, stratification)

        # if (risk_analysis[0] == "ROUGE" and row['risk_level'] == "VERT") or (risk_analysis[0] == "VERT" and row['risk_level'] == "ROUGE"):
        #     print(f"Année: {row['date']}")
        #     print(f"Type de lac: {lake_type}")
        #     print(f"Stratification: {stratification}")
        #     print(f"Drapeau météo : {risk_analysis[0]}")
        #     print(f"Drapeau cyanobactéries : {row['risk_level']}")
        #     print(f"Message météo : {risk_analysis[1]}")
        #     print(f"Densité totale de cyanobactéries: {row['total_density']:.2f} cellules/ml")
        #     print(f"Densité de toxines: {row['toxic_density']:.2f} cellules/ml")
        #     print()

        if row['risk_level'] == "ROUGE" :
            if risk_analysis[0] == "ORANGE":
                count_rouge_to_orange += 1
            if risk_analysis[0] == "VERT":
                count_rouge_to_vert += 1
            if risk_analysis[0] == "ROUGE":
                count_rouge += 1
        if row['risk_level'] == "VERT" :
            if risk_analysis[0] == "ORANGE":
                count_vert_to_orange += 1
            if risk_analysis[0] == "ROUGE":
                count_vert_to_rouge += 1
            if risk_analysis[0] == "VERT":
                count_vert += 1
        if row['risk_level'] == "ORANGE" :
            if risk_analysis[0] == "ROUGE":
                count_orange_to_rouge += 1
            if risk_analysis[0] == "VERT":
                count_orange_to_vert += 1
            if risk_analysis[0] == "ORANGE":
                count_orange += 1
            


    # print(f"Nombre de drapeaux verts : {count_vert}")
    # print(f"Nombre de drapeaux oranges : {count_orange}")
    # print(f"Nombre de drapeaux rouges : {count_rouge}")
    # print(f"Nombre de rouge présenté comme orange par la météo : {count_rouge_to_orange}")
    # print(f"Nombre de rouge présenté comme vert par la météo : {count_rouge_to_vert}")
    # print(f"Nombre de vert présenté comme rouge par la météo : {count_vert_to_rouge}")
    # print(f"Nombre de vert présenté comme orange par la météo : {count_vert_to_orange}")
    # print(f"Nombre de orange présenté comme rouge par la météo : {count_orange_to_rouge}")
    # print(f"Nombre de orange présenté comme vert par la météo : {count_orange_to_vert}")
    results = {
        "Nombre de drapeaux verts": count_vert,
        "Nombre de drapeaux oranges": count_orange,
        "Nombre de drapeaux rouges": count_rouge,
        "Nombre de rouge présenté comme orange par la météo": count_rouge_to_orange,
        "Nombre de rouge présenté comme vert par la météo": count_rouge_to_vert,
        "Nombre de vert présenté comme rouge par la météo": count_vert_to_rouge,
        "Nombre de vert présenté comme orange par la météo": count_vert_to_orange,
        "Nombre de orange présenté comme rouge par la météo": count_orange_to_rouge,
        "Nombre de orange présenté comme vert par la météo": count_orange_to_vert
    }
    print("Lake: ", lake_name)
    print(results)
    


def evaluate_risk_level(conditions, lake_type, stratification):
    risk_score = 0
    high_risk = 0
    
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

    if conditions['temp'] >= temp_threshold['base']:
        risk_score += 1
        if conditions['temp'] >= temp_threshold['high']:
            high_risk += 1
    if conditions['humidity'] > humidity_threshold['base']:
        risk_score += 1
        if conditions['humidity'] > humidity_threshold['high']:
            high_risk += 1
    if conditions['wind'] < wind_threshold['base']:
        risk_score += 1
        if conditions['wind'] < wind_threshold['high']:
            high_risk += 1
    if conditions['soil_temp'] > 24:
        risk_score += 1
        if conditions['soil_temp'] > 26:
            high_risk += 1

    if risk_score <= 1:
        return "VERT", "Risque faible"
    elif risk_score <= 2 or high_risk == 0:
        return "ORANGE", "Conditions favorables - Surveillance recommandée"
    else:
        return "ROUGE", "Conditions très favorables - Présence probable"

evaluate_risk(37.3386, -83.4707, "BHR", "forest", "strong")
evaluate_risk(36.892, -86.1225, "BRR", "agriculture", "strong")
evaluate_risk(39.4428, -85.0001, "BVR", "agriculture", "strong")
