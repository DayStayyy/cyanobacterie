import pandas as pd
from datetime import datetime

def analyze_cyano_presence(file_path, target_lake):
    # Lire le fichier Excel
    df = pd.read_excel(file_path, sheet_name='All_data')
    
    # Convertir les colonnes de date 
    df['date'] = pd.to_datetime(df['date'])
    
    # Filtrer pour le lac spécifié
    lake_data = df[df['reservoir'] == target_lake]
    
    # Grouper par date
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
    print(toxic_density)
    if toxic_density > 100:
        return "ROUGE"
    elif toxic_density > 50:
        return "ORANGE"
    return "VERT"

# Utilisation:
data_string = "./data2/cyanotoxin-taxa-data-xlsx-3.xls"

results = analyze_cyano_presence(data_string, "BHR")
print(results)