from julep import Julep
import yaml
import uuid
from typing import Dict, Any, Optional

class JulepAgentService:
    """Service for managing Julep AI agents and tasks"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        self.agents = {}
        self.tasks = {}
    
    def initialize_client(self) -> bool:
        """Initialize the Julep client"""
        try:
            self.client = Julep(api_key=self.api_key)
            return True
        except Exception as e:
            print(f"Error initializing Julep client: {e}")
            return False
    
    def create_agents(self) -> bool:
        """Create all required agents for the foodie tour workflow"""
        try:
            # Weather Analysis Agent
            weather_agent = self.client.agents.create(
                name="Weather Analysis Agent",
                about="Expert at analyzing weather conditions and recommending appropriate dining experiences based on temperature, precipitation, and atmospheric conditions.",
                model="gpt-4o",
                instructions=[
                    "Analyze weather conditions comprehensively",
                    "Consider temperature, humidity, wind, and precipitation",
                    "Provide specific dining recommendations",
                    "Factor in seasonal and cultural dining preferences",
                    "Suggest timing for outdoor activities"
                ]
            )
            self.agents['weather'] = weather_agent
            
            # Culinary Expert Agent
            culinary_agent = self.client.agents.create(
                name="Local Culinary Expert",
                about="Specialist in local cuisines, traditional dishes, and cultural food significance. Expert at matching dishes to weather conditions and seasonal preferences.",
                model="gpt-4o",
                instructions=[
                    "Identify authentic local dishes for each city",
                    "Match dishes to weather conditions appropriately",
                    "Explain cultural significance and history",
                    "Consider seasonal availability and preparation",
                    "Recommend weather-appropriate cooking methods"
                ]
            )
            self.agents['culinary'] = culinary_agent
            
            # Restaurant Finder Agent
            restaurant_agent = self.client.agents.create(
                name="Restaurant Discovery Agent",
                about="Expert at finding and recommending restaurants based on weather conditions, cuisine types, and dining preferences. Specialized in matching venues to atmospheric conditions.",
                model="gpt-4o",
                instructions=[
                    "Find restaurants suitable for current weather",
                    "Consider indoor/outdoor seating options",
                    "Recommend highly-rated and authentic venues",
                    "Factor in weather-appropriate ambiance",
                    "Suggest backup options for weather changes"
                ]
            )
            self.agents['restaurant'] = restaurant_agent
            
            # Tour Narrative Agent
            tour_agent = self.client.agents.create(
                name="Tour Storytelling Agent",
                about="Master storyteller who creates engaging food tour narratives, weaving together weather, culture, and culinary experiences into memorable adventures.",
                model="gpt-4o",
                instructions=[
                    "Create engaging, personal tour narratives",
                    "Incorporate weather conditions into the story",
                    "Include cultural context and local insights",
                    "Suggest optimal timing and transitions",
                    "Make the experience feel like a personal guide"
                ]
            )
            self.agents['tour'] = tour_agent
            
            # Coordination Agent
            coordinator_agent = self.client.agents.create(
                name="Tour Coordination Agent",
                about="Expert coordinator who synthesizes all tour elements into a comprehensive, practical guide that visitors can actually use.",
                model="gpt-4o",
                instructions=[
                    "Synthesize all tour components cohesively",
                    "Create practical, actionable itineraries",
                    "Ensure logical flow and timing",
                    "Include backup plans and alternatives",
                    "Format information clearly and attractively"
                ]
            )
            self.agents['coordinator'] = coordinator_agent
            
            return True
            
        except Exception as e:
            print(f"Error creating agents: {e}")
            return False
    
    def chat_with_agent(self, agent_type: str, message: str) -> str:
        """
        Send a message to a specific agent and get response
        
        Args:
            agent_type: Type of agent ('weather', 'culinary', 'restaurant', 'tour', 'coordinator')
            message: Message to send to the agent
            
        Returns:
            Agent's response
        """
        try:
            if agent_type not in self.agents:
                return f"Agent type '{agent_type}' not found"
            
            agent = self.agents[agent_type]
            
            # Create a session for this conversation
            session = self.client.sessions.create(
                agent=agent.id,
                situation="Helping create a foodie tour"
            )
            
            # Send message and get response
            response = self.client.sessions.chat(
                session_id=session.id,
                messages=[{
                    "role": "user",
                    "content": message
                }]
            )
              # Extract the response content
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                return "No response from agent"
                
        except Exception as e:
            print(f"Error chatting with {agent_type} agent: {e}")
            return f"Error communicating with {agent_type} agent"
    
    def create_foodie_tour_task(self) -> bool:
        """Create a comprehensive foodie tour task with all agents"""
        try:
            # Create the main coordinator agent if not exists
            if 'coordinator' not in self.agents:
                self.create_agents()
            
            # Define the comprehensive foodie tour task
            task_definition = yaml.safe_load("""
            name: Foodie Tour Generator
            description: Creates comprehensive foodie tours that adapt to real-time weather conditions and local cuisine
            
            input_schema:
              type: object
              properties:
                city:
                  type: string
                  description: The city to create a foodie tour for
                weather_data:
                  type: object
                  description: Current weather data for the city
                  properties:
                    temperature:
                      type: number
                    description:
                      type: string
                    rain_probability:
                      type: number
                    humidity:
                      type: number
                    wind_speed:
                      type: number
                num_dishes:
                  type: integer
                  default: 3
                  description: Number of iconic dishes to recommend
            
            main:
            # Step 1: Weather Analysis
            - prompt:
              - role: system
                content: >
                  You are a weather analysis expert. Analyze the given weather conditions
                  and provide specific dining recommendations for the city.
              - role: user
                content: >
                  $ f'''Analyze the weather in {steps[0].input.city}:
                  Temperature: {steps[0].input.weather_data.temperature}°C
                  Conditions: {steps[0].input.weather_data.description}
                  Rain Probability: {steps[0].input.weather_data.rain_probability}%
                  Humidity: {steps[0].input.weather_data.humidity}%
                  Wind Speed: {steps[0].input.weather_data.wind_speed} m/s
                  
                  Provide specific dining recommendations based on these conditions.'''
              unwrap: true
            
            # Step 2: Find Weather-Appropriate Dishes
            - prompt:
              - role: system
                content: >
                  You are a local culinary expert. Recommend iconic local dishes
                  that are perfect for the current weather conditions.
              - role: user
                content: >
                  $ f'''For {steps[0].input.city} with current weather conditions
                  (Temperature: {steps[0].input.weather_data.temperature}°C, 
                  Conditions: {steps[0].input.weather_data.description}),
                  recommend {steps[0].input.num_dishes} iconic local dishes that are perfect for today's weather.
                  Explain why each dish suits these conditions.'''
              unwrap: true
            
            # Step 3: Find Suitable Restaurants
            - prompt:
              - role: system
                content: >
                  You are a restaurant discovery expert. Find restaurants that serve
                  the recommended dishes and are suitable for current weather conditions.
              - role: user
                content: >
                  $ f'''Based on the weather in {steps[0].input.city} and the recommended dishes,
                  find top-rated restaurants that:
                  1. Serve these authentic local dishes
                  2. Have appropriate indoor/outdoor seating for the weather
                  3. Are highly rated and authentic
                  
                  Weather: {steps[0].input.weather_data.temperature}°C, {steps[0].input.weather_data.description}
                  Dishes: {steps[1].output}'''
              unwrap: true
            
            # Step 4: Create Tour Narrative
            - prompt:
              - role: system
                content: >
                  You are a master storyteller creating engaging food tour narratives.
                  Create a day-long adventure that feels personal and exciting.
              - role: user
                content: >
                  $ f'''Create an engaging one-day foodie tour for {steps[0].input.city}:
                  
                  Weather Context: {steps[0].input.weather_data.temperature}°C, {steps[0].input.weather_data.description}
                  Weather Analysis: {steps[0].output}
                  Recommended Dishes: {steps[1].output}
                  Restaurant Options: {steps[2].output}
                  
                  Create a narrative that includes morning, afternoon, and evening activities,
                  with cultural stories and weather-appropriate transitions.'''
              unwrap: true
            
            # Step 5: Final Coordination
            - prompt:
              - role: system
                content: >
                  You are a tour coordinator. Create a comprehensive, practical guide
                  that combines all elements into an easy-to-follow format.
              - role: user
                content: >
                  $ f'''Create a final comprehensive guide for {steps[0].input.city} that combines:
                  
                  Weather Analysis: {steps[0].output}
                  Local Dishes: {steps[1].output}
                  Restaurant Recommendations: {steps[2].output}
                  Tour Narrative: {steps[3].output}
                  
                  Format this as a practical guide with clear sections, timing,
                  and actionable advice that someone could use today.'''
              unwrap: true
            """)
            
            # Create the task
            task = self.client.tasks.create(
                agent_id=self.agents['coordinator'].id,
                **task_definition
            )
            
            self.tasks['foodie_tour'] = task
            return True
            
        except Exception as e:
            print(f"Error creating foodie tour task: {e}")
            return False
    
    def execute_foodie_tour(self, city: str, weather_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute the foodie tour task for a specific city
        
        Args:
            city: Name of the city
            weather_data: Weather information
            
        Returns:
            Task execution result or None if error
        """
        try:
            if 'foodie_tour' not in self.tasks:
                if not self.create_foodie_tour_task():
                    return None
            
            task = self.tasks['foodie_tour']
            
            # Execute the task
            execution = self.client.executions.create(
                task_id=task.id,
                input={
                    'city': city,
                    'weather_data': weather_data,
                    'num_dishes': 3
                }
            )
            
            # Wait for completion with timeout
            max_attempts = 30
            attempt = 0
            
            while attempt < max_attempts:
                result = self.client.executions.get(execution.id)
                
                if result.status == 'succeeded':
                    return {
                        'status': 'success',
                        'output': result.output,
                        'steps': result.output if hasattr(result, 'output') else None
                    }
                elif result.status == 'failed':
                    return {
                        'status': 'failed',
                        'error': getattr(result, 'error', 'Unknown error')
                    }
                
                attempt += 1
                # Small delay between checks
                import time
                time.sleep(2)
            
            return {
                'status': 'timeout',
                'error': 'Task execution timed out'
            }
            
        except Exception as e:
            print(f"Error executing foodie tour for {city}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
