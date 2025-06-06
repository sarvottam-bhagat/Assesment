import requests
import os
from datetime import datetime
from typing import Dict, Any, Optional

class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_weather_data(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Fetch current weather data for a city
        
        Args:
            city: Name of the city
            
        Returns:
            Dictionary containing weather data or None if error
        """
        try:
            # Current weather endpoint
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'  # For Celsius
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            weather_data = {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'].title(),
                'wind_speed': round(data['wind']['speed'], 1),
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime("%H:%M"),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime("%H:%M"),
                'rain_probability': self._get_rain_probability(data)
            }
            
            return weather_data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data for {city}: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing weather data for {city}: {e}")
            return None
    
    def _get_rain_probability(self, data: Dict[str, Any]) -> int:
        """
        Extract rain probability from weather data
        
        Args:
            data: Raw weather API response
            
        Returns:
            Rain probability as percentage
        """
        # OpenWeatherMap doesn't always provide rain probability in current weather
        # We'll estimate based on weather conditions
        weather_main = data['weather'][0]['main'].lower()
        
        if 'rain' in weather_main:
            return 80
        elif 'drizzle' in weather_main:
            return 60
        elif 'cloud' in weather_main:
            humidity = data['main']['humidity']
            if humidity > 80:
                return 40
            elif humidity > 60:
                return 20
            else:
                return 10
        elif 'clear' in weather_main:
            return 5
        else:
            return 15
    
    def get_dining_recommendation(self, weather_data: Dict[str, Any]) -> str:
        """
        Generate dining recommendation based on weather conditions
        
        Args:
            weather_data: Weather information
            
        Returns:
            Dining recommendation string
        """
        temp = weather_data['temperature']
        rain_prob = weather_data['rain_probability']
        description = weather_data['description'].lower()
        
        if rain_prob > 50:
            return "🏠 Perfect weather for cozy indoor dining with warm comfort foods!"
        elif temp < 10:
            return "🔥 Cold weather calls for warm, hearty meals in comfortable indoor spaces!"
        elif temp > 25 and rain_prob < 20:
            return "☀️ Beautiful weather for outdoor dining, rooftop restaurants, and patio experiences!"
        elif 15 <= temp <= 25:
            return "🌤️ Pleasant weather ideal for both indoor and outdoor dining options!"
        else:
            return "🏛️ Mixed conditions - indoor dining recommended with possible outdoor options!"
