import React, { useState } from 'react';

const PredictionForm = () => {
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const formData = {
      latitude: e.target.latitude.value,
      longitude: e.target.longitude.value,
      lakeType: e.target.lakeType.value
    };

    try {
      const response = await fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();
      
      if (data.success) {
        setPredictions(data.predictions);
      } else {
        console.error('Error:', data.error);
        alert('Une erreur est survenue lors de la récupération des prédictions');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Une erreur est survenue lors de la connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-blue-50 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-blue-600 shadow-lg transform -skew-y-6 sm:skew-y-0 sm:-rotate-6 sm:rounded-3xl"></div>
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <div className="max-w-md mx-auto">
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <h1 className="text-2xl font-bold mb-8 text-center text-blue-600">Prévision Cyanobactéries</h1>
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="flex flex-col">
                    <label className="text-sm font-medium text-gray-600 mb-1">Latitude</label>
                    <input 
                      name="latitude"
                      type="number" 
                      step="0.000001" 
                      className="px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
                      placeholder="46.2276" 
                      required 
                    />
                  </div>
                  <div className="flex flex-col">
                    <label className="text-sm font-medium text-gray-600 mb-1">Longitude</label>
                    <input 
                      name="longitude"
                      type="number" 
                      step="0.000001" 
                      className="px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
                      placeholder="2.2137" 
                      required 
                    />
                  </div>
                  <div className="flex flex-col">
                    <label className="text-sm font-medium text-gray-600 mb-1">Type de lac</label>
                    <select 
                      name="lakeType" 
                      className="px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
                      required
                    >
                      <option value="forest">Forestier</option>
                      <option value="agriculture">Agricole</option>
                      <option value="urban">Urbain</option>
                    </select>
                  </div>
                  <button 
                    type="submit" 
                    className="w-full px-4 py-2 text-white font-semibold bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={loading}
                  >
                    {loading ? 'Chargement...' : 'Obtenir la prévision'}
                  </button>
                </form>

                {predictions && (
                  <div className="mt-8 space-y-4">
                    <h2 className="text-xl font-semibold text-blue-600 mb-4">Prévisions sur 7 jours</h2>
                    <div className="grid gap-4 grid-cols-1">
                      {predictions.map((day, index) => (
                        <div 
                          key={index} 
                          className={`p-4 rounded-lg shadow ${
                            day.flag === 'ROUGE' ? 'bg-red-100' :
                            day.flag === 'ORANGE' ? 'bg-orange-100' : 'bg-green-100'
                          }`}
                        >
                          <div className="font-semibold text-gray-800">{day.date}</div>
                          <div className={`mt-2 font-bold ${
                            day.flag === 'ROUGE' ? 'text-red-600' :
                            day.flag === 'ORANGE' ? 'text-orange-600' : 'text-green-600'
                          }`}>
                            {day.flag}
                          </div>
                          <p className="mt-2 text-sm text-gray-600">{day.message}</p>
                          <div className="mt-2 text-xs text-gray-500">
                            {day.conditions && Object.entries(day.conditions).map(([key, value]) => (
                              <div key={key}>{key}: {typeof value === 'number' ? value.toFixed(1) : value}</div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PredictionForm;