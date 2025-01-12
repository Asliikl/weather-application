from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

API_KEY = 'YOUR_API KEY'

@app.route('/', methods=['GET', 'POST'])
def weather():
    weather_data = None
    forecast_data = None
    error = None
    
    if request.method == 'POST':
        city = request.form['city']

        # Mevcut durum API 
        current_url = 'https://api.openweathermap.org/data/2.5/weather'
        # 5 günlük tahmini
        forecast_url = 'https://api.openweathermap.org/data/2.5/forecast'
        
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric',
            'lang': 'tr'
        }
        
        try:
            # Mevcut hava durumu
            current_response = requests.get(current_url, params=params)
            if current_response.status_code == 200:
                data = current_response.json()
                weather_data = {
                    'city': city,
                    'temperature': round(data['main']['temp']),
                    'feels_like': round(data['main']['feels_like']),
                    'humidity': data['main']['humidity'],
                    'description': data['weather'][0]['description'].capitalize(),
                    'icon': data['weather'][0]['icon'],
                    'wind_speed': round(data['wind']['speed']),
                    'pressure': data['main']['pressure']
                }
                
                # 5 günlük
                forecast_response = requests.get(forecast_url, params=params)
                if forecast_response.status_code == 200:
                    forecast_data = []
                    for item in forecast_response.json()['list'][::8]: 
                        forecast_data.append({
                            'date': datetime.fromtimestamp(item['dt']).strftime('%d.%m'),
                            'temp': round(item['main']['temp']),
                            'icon': item['weather'][0]['icon'],
                            'description': item['weather'][0]['description'].capitalize(),
                            'precipitation': round(item.get('pop', 0) * 100), 
                            'wind_speed': round(item['wind']['speed'] * 3.6),  # m/s'den km/s'ye çevirme
                            'wind_direction': get_wind_direction(item['wind']['deg'])
                        })
            else:
                error = f"Hata: {current_response.json().get('message', 'Bilinmeyen hata')}"
        except Exception as e:
            error = "Bir hata oluştu. Lütfen daha sonra tekrar deneyin."
    
    return render_template('weather.html', 
                         weather_data=weather_data, 
                         forecast_data=forecast_data, 
                         error=error)

def get_wind_direction(degrees):
    directions = ['K', 'KD', 'D', 'GD', 'G', 'GB', 'B', 'KB']
    index = round(degrees / 45) % 8
    return directions[index]

if __name__ == '__main__':
    app.run(debug=True) 