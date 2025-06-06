import re
import streamlit as st
from datetime import datetime
from typing import Dict, Any

def load_css(file_path: str):
    """Load CSS from external file and inject button fix"""
    try:
        with open(file_path, 'r') as f:
            css = f.read()
        
        # Add extra high-specificity CSS for button fix
        button_fix_css = """
        /* ULTRA HIGH SPECIFICITY BUTTON FIX - Override Streamlit emotion cache */
        div.stButton > button.st-emotion-cache-7ym5gk.ef3psqc12,
        div.stButton > button.st-emotion-cache-7ym5gk,
        div.stButton > button.ef3psqc12,
        div.row-widget.stButton > button,
        .stButton > button,
        [data-testid="baseButton-secondary"],
        [data-testid="baseButton-primary"] {
            background-color: #000000 !important;
            color: #ffffff !important;
            border: 2px solid #ffffff !important;
            padding: 12px 24px !important;
            border-radius: 8px !important;
            font-size: 18px !important;
            font-weight: bold !important;
            font-family: Arial, sans-serif !important;
            cursor: pointer !important;
            text-decoration: none !important;
            -webkit-text-fill-color: #ffffff !important;
            background-clip: initial !important;
            -webkit-background-clip: initial !important;
            text-shadow: none !important;
            box-shadow: none !important;
            transition: all 0.2s ease !important;
        }
        
        div.stButton > button.st-emotion-cache-7ym5gk.ef3psqc12:hover,
        div.stButton > button.st-emotion-cache-7ym5gk:hover,
        div.stButton > button.ef3psqc12:hover,
        div.row-widget.stButton > button:hover,
        .stButton > button:hover,
        [data-testid="baseButton-secondary"]:hover,
        [data-testid="baseButton-primary"]:hover {
            background-color: #222222 !important;
            color: #ffffff !important;
            border-color: #00ff88 !important;
            -webkit-text-fill-color: #ffffff !important;
            transform: scale(1.02) !important;
        }
        
        /* Force all child elements to be white text with ultra high specificity */
        div.stButton > button.st-emotion-cache-7ym5gk.ef3psqc12 *,
        div.stButton > button.st-emotion-cache-7ym5gk *,
        div.stButton > button.ef3psqc12 *,
        div.row-widget.stButton > button *,
        .stButton > button *,
        [data-testid="baseButton-secondary"] *,
        [data-testid="baseButton-primary"] * {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            background: transparent !important;
            text-shadow: none !important;
        }
        """
        
        # Combine original CSS with button fix
        combined_css = css + button_fix_css
        
        st.markdown(f'<style>{combined_css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {file_path}")

def get_weather_emoji(description: str) -> str:
    """Get appropriate emoji for weather condition"""
    description_lower = description.lower()
    
    if "rain" in description_lower:
        return "🌧️"
    elif "cloud" in description_lower:
        return "☁️"
    elif "clear" in description_lower:
        return "☀️"
    elif "snow" in description_lower:
        return "❄️"
    elif "thunder" in description_lower:
        return "⛈️"
    elif "mist" in description_lower or "fog" in description_lower:
        return "🌫️"
    elif "wind" in description_lower:
        return "💨"
    else:
        return "🌤️"

def format_time() -> str:
    """Get current formatted time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def validate_api_key(api_key: str, key_name: str) -> tuple[bool, str]:
    """Validate API key format"""
    if not api_key:
        return False, f"{key_name} is required"
    
    if len(api_key) < 10:
        return False, f"{key_name} appears to be too short"
    
    return True, "Valid"

def clean_response_text(text: str) -> str:
    """Clean and format response text from agents"""
    if not text:
        return "No response available"
    
    # Convert to string if it's not already
    text = str(text)
    
    # Remove JSON-like formatting
    text = re.sub(r'^\s*[\{\[].*?[\}\]]\s*$', '', text, flags=re.DOTALL)
    
    # Remove extra quotes and escape characters
    text = text.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
    
    # Remove leading/trailing quotes if present
    text = text.strip('"\'')
    
    # Clean up multiple newlines
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    # Remove any remaining JSON artifacts
    text = re.sub(r'^\s*".*?":\s*"', '', text)
    text = re.sub(r'",?\s*$', '', text)
    
    return text.strip()

def create_download_content(tour_data: Dict[str, Any]) -> str:
    """Create formatted content for download"""
    return f"""# Foodie Tour: {tour_data['city']}

Generated on: {format_time()}

## 🌤️ Weather Analysis
{tour_data.get('weather_analysis', 'N/A')}

## 🍜 Perfect Dishes for Today
{tour_data.get('dishes', 'N/A')}

## 🏨 Restaurant Recommendations
{tour_data.get('restaurants', 'N/A')}

## 📖 Day Adventure Timeline
{tour_data.get('narrative', 'N/A')}

## 🎯 Complete Guide
{tour_data.get('final_tour', 'N/A')}

---
*Generated by Foodie Tours powered by Julep AI*
"""

def show_progress_with_message(progress_value: int, message: str):
    """Show progress bar with custom message"""
    progress_bar = st.progress(progress_value)
    status_text = st.empty()
    status_text.text(message)
    return progress_bar, status_text

def clear_progress(progress_bar, status_text):
    """Clear progress indicators"""
    progress_bar.empty()
    status_text.empty()

def format_weather_display(weather_data: Dict[str, Any]) -> str:
    """Create beautiful weather display HTML"""
    if not weather_data:
        return "Weather data unavailable"
    
    weather_emoji = get_weather_emoji(weather_data['description'])
    
    return f"""
    <div class="weather-card">
        <h2>{weather_emoji} {weather_data['city']}, {weather_data['country']}</h2>
        <h1>{weather_data['temperature']}°C</h1>
        <h3>{weather_data['description']}</h3>
        <div class="weather-stats">
            <div class="weather-stat">
                <strong>Feels Like:</strong><br>{weather_data['feels_like']}°C
            </div>
            <div class="weather-stat">
                <strong>Humidity:</strong><br>{weather_data['humidity']}%
            </div>
            <div class="weather-stat">
                <strong>Wind:</strong><br>{weather_data['wind_speed']} m/s
            </div>
            <div class="weather-stat">
                <strong>Rain Chance:</strong><br>{weather_data['rain_probability']}%
            </div>
        </div>
        <div style="margin-top: 1rem;">
            <span class="time-badge">🌅 Sunrise: {weather_data['sunrise']}</span>
            <span class="time-badge">🌇 Sunset: {weather_data['sunset']}</span>
        </div>
    </div>
    """

def extract_agent_response(response: Any) -> str:
    """Extract clean text from agent response"""
    if isinstance(response, str):
        return clean_response_text(response)
    elif hasattr(response, 'content'):
        return clean_response_text(response.content)
    elif hasattr(response, 'response') and response.response:
        if isinstance(response.response, list) and len(response.response) > 0:
            return clean_response_text(response.response[0].content)
        else:
            return clean_response_text(str(response.response))
    else:
        return clean_response_text(str(response))
