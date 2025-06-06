#!/usr/bin/env python3
"""
Foodie Tours MCP Server

This MCP server exposes the functionality of the Foodie Tours Streamlit application,
allowing interaction with weather data, Julep AI agents, and tour generation
through any MCP-compatible client (Claude Desktop, IDEs, etc.).
"""

import os
import sys
import io
import json

# Fix encoding issues on Windows
if sys.platform == "win32":
    # Ensure UTF-8 encoding for stdout/stderr to handle Unicode characters
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv
from fastmcp import FastMCP, Context

# Import your existing services
from weather_service import WeatherService
from julep_service import JulepAgentService
from utils import validate_api_key, get_weather_emoji, format_time

# Load environment variables
load_dotenv()

# Initialize the MCP server
mcp = FastMCP(
    name="Foodie Tours Server",
    instructions="""
    This server provides access to the Foodie Tours application functionality.
    You can:
    - Get weather data for any city
    - Generate personalized foodie tours using AI agents
    - Get dining recommendations based on weather conditions
    - Access weather-appropriate restaurant suggestions
    - Create complete tour narratives with cultural insights
    
    The server integrates weather analysis with AI-powered culinary expertise
    to create comprehensive food tourism experiences.
    """
)

# Global services (will be initialized on server startup)
weather_service: Optional[WeatherService] = None
julep_service: Optional[JulepAgentService] = None
tours_cache: Dict[str, Any] = {}

async def initialize_services():
    """Initialize weather and Julep services"""
    global weather_service, julep_service
    
    try:
        # Get API keys from environment
        julep_key = os.getenv('JULEP_API_KEY')
        weather_key = os.getenv('OPENWEATHER_API_KEY')
        
        if not julep_key:
            print("WARNING: JULEP_API_KEY not found - some features will be disabled")
            weather_key_available = weather_key is not None
            if weather_key_available:
                weather_service = WeatherService(weather_key)
                print("SUCCESS: Weather service initialized")
            return weather_key_available
        
        if not weather_key:
            print("WARNING: OPENWEATHER_API_KEY not found - weather features will be disabled")
            # Try to initialize just Julep service
            julep_service = JulepAgentService(julep_key)
            if julep_service.initialize_client() and julep_service.create_agents():
                print("SUCCESS: Julep service initialized")
                return True
            return False
        
        # Initialize both services
        weather_service = WeatherService(weather_key)
        print("SUCCESS: Weather service initialized")
        
        julep_service = JulepAgentService(julep_key)
        if julep_service.initialize_client() and julep_service.create_agents():
            print("SUCCESS: Julep service initialized")
        else:
            print("WARNING: Julep service initialization failed")
        
        print("SUCCESS: Services initialized successfully")
        return True
        
    except Exception as e:
        print(f"WARNING: Error during service initialization: {e}")
        print("Some features may be disabled")
        return False

@mcp.tool()
def get_weather_data(city: str) -> Dict[str, Any]:
    """
    Get current weather data for a specific city.
    
    Args:
        city: Name of the city to get weather for
        
    Returns:
        Dictionary containing weather information including temperature,
        humidity, description, wind speed, and more
    """
    if not weather_service:
        return {"error": "Weather service not initialized"}
    
    try:
        weather_data = weather_service.get_weather_data(city)
        if weather_data:
            # Add emoji for better display
            weather_data['emoji'] = get_weather_emoji(weather_data['description'])
            weather_data['formatted_time'] = format_time(datetime.now())
            return weather_data
        else:
            return {"error": f"Could not fetch weather data for {city}"}
    except Exception as e:
        return {"error": f"Error fetching weather: {str(e)}"}

@mcp.tool()
def get_dining_recommendation(city: str) -> Dict[str, Any]:
    """
    Get weather-based dining recommendation for a city.
    
    Args:
        city: Name of the city
        
    Returns:
        Dictionary containing dining recommendation based on current weather
    """
    if not weather_service:
        return {"error": "Weather service not initialized"}
    
    try:
        weather_data = weather_service.get_weather_data(city)
        if weather_data:
            recommendation = weather_service.get_dining_recommendation(weather_data)
            return {
                "city": city,
                "weather": weather_data,
                "dining_recommendation": recommendation
            }
        else:
            return {"error": f"Could not fetch weather data for {city}"}
    except Exception as e:
        return {"error": f"Error getting dining recommendation: {str(e)}"}

@mcp.tool()
def chat_with_agent(agent_type: str, message: str) -> Dict[str, Any]:
    """
    Chat with a specific Julep AI agent.
    
    Args:
        agent_type: Type of agent ('weather', 'culinary', 'restaurant', 'tour', 'coordinator')
        message: Message to send to the agent
        
    Returns:
        Dictionary containing the agent's response
    """
    if not julep_service:
        return {"error": "Julep service not initialized"}
    
    valid_agents = ['weather', 'culinary', 'restaurant', 'tour', 'coordinator']
    if agent_type not in valid_agents:
        return {
            "error": f"Invalid agent type. Valid types are: {', '.join(valid_agents)}"
        }
    
    try:
        response = julep_service.chat_with_agent(agent_type, message)
        return {
            "agent_type": agent_type,
            "message": message,
            "response": response
        }
    except Exception as e:
        return {"error": f"Error chatting with agent: {str(e)}"}

@mcp.tool()
async def create_complete_foodie_tour(city: str, ctx: Context) -> Dict[str, Any]:
    """
    Create a complete foodie tour for a city using all AI agents.
    This is the main function that orchestrates weather analysis,
    culinary expertise, restaurant recommendations, and tour narrative.
    
    Args:
        city: Name of the city to create tour for
        
    Returns:
        Dictionary containing complete foodie tour information
    """
    if not weather_service or not julep_service:
        return {"error": "Services not initialized"}
    
    try:
        await ctx.info(f"Creating complete foodie tour for {city}...")
        
        # Step 1: Get weather data
        await ctx.info("Fetching weather data...")
        weather_data = weather_service.get_weather_data(city)
        if not weather_data:
            return {"error": f"Could not fetch weather data for {city}"}
        
        # Step 2: Weather analysis
        await ctx.info("Analyzing weather with AI agent...")
        weather_message = f"""
        Analyze the current weather in {city}:
        - Temperature: {weather_data['temperature']}°C (feels like {weather_data['feels_like']}°C)
        - Conditions: {weather_data['description']}
        - Humidity: {weather_data['humidity']}%
        - Wind Speed: {weather_data['wind_speed']} m/s
        
        Provide dining recommendations that match these weather conditions.
        """
        weather_analysis = julep_service.chat_with_agent('weather', weather_message)
        
        # Step 3: Culinary expertise
        await ctx.info("Getting culinary expertise...")
        culinary_message = f"""
        Based on the weather analysis for {city}, suggest authentic local dishes
        that would be perfect for these conditions:
        {weather_analysis}
        
        Focus on traditional cuisine and seasonal specialties.
        """
        culinary_suggestions = julep_service.chat_with_agent('culinary', culinary_message)
        
        # Step 4: Restaurant recommendations
        await ctx.info("Finding perfect restaurants...")
        restaurant_message = f"""
        Find restaurants in {city} that would be ideal for the current weather
        and these culinary suggestions:
        
        Weather: {weather_data['description']}, {weather_data['temperature']}°C
        Cuisine Focus: {culinary_suggestions}
        
        Recommend specific restaurants with indoor/outdoor options as appropriate.
        """
        restaurant_recommendations = julep_service.chat_with_agent('restaurant', restaurant_message)
        
        # Step 5: Create tour narrative
        await ctx.info("Crafting tour narrative...")
        tour_message = f"""
        Create an engaging foodie tour narrative for {city} incorporating:
        
        Weather Conditions: {weather_data['description']}, {weather_data['temperature']}°C
        Culinary Focus: {culinary_suggestions}
        Restaurant Recommendations: {restaurant_recommendations}
        
        Make it personal and story-driven, like a local guide showing friends around.
        """
        tour_narrative = julep_service.chat_with_agent('tour', tour_message)
        
        # Step 6: Final coordination
        await ctx.info(" Coordinating final tour...")
        coordination_message = f"""
        Synthesize all elements into a practical, comprehensive foodie tour guide:
        
        City: {city}
        Weather: {weather_data}
        Weather Analysis: {weather_analysis}
        Culinary Suggestions: {culinary_suggestions}
        Restaurant Recommendations: {restaurant_recommendations}
        Tour Narrative: {tour_narrative}
        
        Create a final, well-organized tour guide that visitors can actually use.
        """
        final_tour = julep_service.chat_with_agent('coordinator', coordination_message)
        
        # Compile complete tour
        complete_tour = {
            "city": city,
            "created_at": datetime.now().isoformat(),
            "weather_data": weather_data,
            "weather_analysis": weather_analysis,
            "culinary_suggestions": culinary_suggestions,
            "restaurant_recommendations": restaurant_recommendations,
            "tour_narrative": tour_narrative,
            "final_tour_guide": final_tour
        }
        
        # Cache the tour
        tours_cache[f"{city}_{datetime.now().strftime('%Y%m%d')}"] = complete_tour
        
        await ctx.info(f"SUCCESS: Complete foodie tour created for {city}!")
        return complete_tour
        
    except Exception as e:
        await ctx.error(f"Error creating foodie tour: {str(e)}")
        return {"error": f"Error creating foodie tour: {str(e)}"}

@mcp.tool()
def list_available_agents() -> List[str]:
    """
    List all available Julep AI agents and their specialties.
    
    Returns:
        List of agent types with descriptions
    """
    agents = [
        "weather - Expert at analyzing weather conditions and dining recommendations",
        "culinary - Specialist in local cuisines and traditional dishes",
        "restaurant - Expert at finding restaurants based on weather and cuisine",
        "tour - Master storyteller for engaging food tour narratives",
        "coordinator - Expert coordinator for comprehensive tour synthesis"
    ]
    return agents

@mcp.tool()
def get_cached_tours() -> List[str]:
    """
    Get list of cached tours.
    
    Returns:
        List of cached tour keys
    """
    return list(tours_cache.keys())

@mcp.tool()
def get_cached_tour(tour_key: str) -> Dict[str, Any]:
    """
    Retrieve a cached tour by its key.
    
    Args:
        tour_key: Key of the cached tour
        
    Returns:
        Cached tour data or error message
    """
    if tour_key in tours_cache:
        return tours_cache[tour_key]
    else:
        return {"error": f"Tour '{tour_key}' not found in cache"}

# Resources - provide access to static information
@mcp.resource("resource://app-status")
async def get_app_status(ctx: Context) -> Dict[str, Any]:
    """Get the current status of the Foodie Tours application."""
    await ctx.info("Checking application status...")
    
    status = {
        "app_name": "Foodie Tours",
        "server_name": mcp.name,
        "weather_service_active": weather_service is not None,
        "julep_service_active": julep_service is not None,
        "cached_tours_count": len(tours_cache),
        "available_agents": len(julep_service.agents) if julep_service else 0,
        "last_updated": datetime.now().isoformat()
    }
    
    return status

@mcp.resource("resource://tour-cache")
def get_tour_cache_info() -> Dict[str, Any]:
    """Get information about cached tours."""
    return {
        "total_tours": len(tours_cache),
        "tour_keys": list(tours_cache.keys()),
        "cache_created": datetime.now().isoformat()
    }

@mcp.resource("resource://service-config")
def get_service_configuration() -> Dict[str, Any]:
    """Get current service configuration."""
    return {
        "weather_api_configured": os.getenv('OPENWEATHER_API_KEY') is not None,
        "julep_api_configured": os.getenv('JULEP_API_KEY') is not None,
        "base_weather_url": "http://api.openweathermap.org/data/2.5" if weather_service else None,
        "supported_agents": [
            "weather", "culinary", "restaurant", "tour", "coordinator"
        ]
    }

# Server lifecycle management will be handled in main
if __name__ == "__main__":
    # Initialize services synchronously before starting server
    print("Starting Foodie Tours MCP Server...")
    
    # Run initialization in an event loop
    import asyncio
    try:
        asyncio.run(initialize_services())
        print("SUCCESS: Foodie Tours MCP Server started successfully!")
        # Run the server
        # Default to stdio for CLI usage, but can be overridden
        mcp.run()
    except Exception as e:
        print(f"ERROR: Failed to start server: {e}")
        exit(1)
