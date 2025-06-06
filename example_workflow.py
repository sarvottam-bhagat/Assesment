"""
Example workflow demonstrating Julep AI integration for foodie tours
This shows how to create agents and tasks using the Julep platform
"""

from julep import Julep
import yaml
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Initialize Julep client
    client = Julep(api_key=os.getenv('JULEP_API_KEY'))
    
    # Create a foodie tour agent
    agent = client.agents.create(
        name="Foodie Tour Agent",
        about="An expert travel and culinary agent that creates food tours",
        model="gpt-4o",
        instructions=[
            "You are a knowledgeable food and travel expert",
            "Always consider weather conditions when making recommendations",
            "Focus on authentic local cuisine and cultural experiences",
            "Provide practical, actionable advice",
            "Include timing and logistics in your recommendations"
        ]
    )
    
    print(f"✅ Created agent: {agent.name} (ID: {agent.id})")
    
    # Define a simple task for generating a food tour
    task_definition = yaml.safe_load("""
    name: Food Tour
    description: Create a food tour that adapts to current weather conditions
    
    input_schema:
      type: object
      properties:
        city:
          type: string
          description: The city to create a food tour for
        weather:
          type: string
          description: Current weather conditions
        temperature:
          type: number
          description: Current temperature in Celsius
    
    main:
    - prompt:
      - role: system
        content: >
          You are an expert food tour guide. Create a weather-appropriate 
          food tour for the given city and conditions.
      - role: user
        content: >
          $ f'''Create a one-day food tour for {steps[0].input.city}.
          Current weather: {steps[0].input.weather}
          Temperature: {steps[0].input.temperature}°C
          
          Include:
          1. 3 weather-appropriate local dishes
          2. Recommended restaurants
          3. Timing suggestions
          4. Indoor/outdoor dining recommendations
          '''
      unwrap: true
    """)
    
    # Create the task
    task = client.tasks.create(
        agent_id=agent.id,
        **task_definition
    )
    
    print(f"✅ Created task: {task.name} (ID: {task.id})")
    
    # Execute the task with sample data
    execution = client.executions.create(
        task_id=task.id,
        input={
            "city": "Tokyo",
            "weather": "Rainy",
            "temperature": 15
        }
    )
    
    print(f"✅ Started execution: {execution.id}")
    
    # Wait for completion
    import time
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        result = client.executions.get(execution.id)
        print(f"Status: {result.status}")
        
        if result.status == 'succeeded':
            print("\n🎉 Task completed successfully!")
            print("Generated Food Tour:")
            print("-" * 50)
            print(result.output)
            break
        elif result.status == 'failed':
            print(f"❌ Task failed: {getattr(result, 'error', 'Unknown error')}")
            break
        
        attempt += 1
        time.sleep(2)
    
    if attempt >= max_attempts:
        print("⏰ Task execution timed out")

if __name__ == "__main__":
    main()
