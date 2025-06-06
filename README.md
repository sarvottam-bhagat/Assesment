# Foodie Tours

A comprehensive AI-powered workflow that creates personalized foodie tours based on real-time weather conditions and local cuisine. Built with Julep AI's powerful workflow engine.

## Features

- **Real-time Weather Integration**: Fetches current weather data to suggest indoor/outdoor dining
- **Local Cuisine Discovery**: Identifies 3 iconic dishes per city based on weather conditions
- **Restaurant Recommendations**: Finds top-rated restaurants serving recommended dishes
- **Intelligent Tour Planning**: Creates a complete day itinerary with breakfast, lunch, and dinner
- **Weather-Adaptive Narratives**: Tailors the experience based on current conditions

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your API keys in `.env`:
```
JULEP_API_KEY=your_julep_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
```

3. Run the application:
```bash
streamlit run app.py
```

## Architecture

### Julep Workflow Components

1. **Weather Agent**: Analyzes current conditions and suggests appropriate dining styles
2. **Culinary Agent**: Recommends weather-appropriate local dishes
3. **Restaurant Agent**: Finds suitable restaurants based on weather and dishes
4. **Tour Agent**: Creates engaging narratives and itineraries
5. **Coordinator Agent**: Combines all information into a comprehensive guide

### Workflow Process

1. **Weather Analysis**: Fetch real-time weather data and determine dining recommendations
2. **Dish Selection**: Identify 3 iconic local dishes perfect for current weather
3. **Restaurant Discovery**: Find top-rated restaurants with appropriate indoor/outdoor options
4. **Narrative Creation**: Generate engaging tour stories with cultural insights
5. **Final Coordination**: Combine all elements into a downloadable tour guide

## Usage

1. Select cities from the sidebar or add custom cities
2. Click "Generate Foodie Tours"
3. View beautiful, formatted tour guides
4. Download your personalized tour as a Markdown file

## Workflow Details

The application uses Julep AI's multi-agent workflow system to:
- Process multiple cities in parallel
- Coordinate between specialized agents
- Handle complex data transformations
- Provide real-time status updates
- Generate rich, contextual content

Each agent has specific expertise and contributes to creating a cohesive dining experience.
