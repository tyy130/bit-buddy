#!/usr/bin/env python3
"""
Interactive Bit Buddy Demo - Chat with your digital companion
"""

import requests
import json
import time
import sys
from typing import Dict, Any

class BuddyClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")
    
    def hello(self) -> Dict[str, Any]:
        """Greet the buddy"""
        response = requests.get(f"{self.base_url}/hello")
        return response.json()
    
    def ask(self, query: str) -> Dict[str, Any]:
        """Ask the buddy something"""
        response = requests.post(f"{self.base_url}/ask", 
                               json={"query": query})
        return response.json()
    
    def get_personality(self) -> Dict[str, Any]:
        """Get buddy's personality"""
        response = requests.get(f"{self.base_url}/personality")
        return response.json()
    
    def randomize(self) -> Dict[str, Any]:
        """Give buddy new personality"""
        response = requests.post(f"{self.base_url}/personality/randomize")
        return response.json()
    
    def narrate(self, event_type: str, note: str) -> Dict[str, Any]:
        """Add story event"""
        response = requests.post(f"{self.base_url}/narrate",
                               json={"type": event_type, "note": note})
        return response.json()

def print_buddy_response(response: Dict[str, Any], label: str = "Buddy"):
    """Pretty print buddy responses"""
    if "message" in response:
        print(f"🤖 {label}: {response['message']}")
    if "answer" in response:
        print(f"🤖 {label}: {response['answer']}")
    if "reaction" in response:
        print(f"🤖 {label}: {response['reaction']}")
    
    if "aside" in response:
        print(f"   💭 ({response['aside']})")
    print()

def demo_personality_evolution():
    """Show how buddy personality affects interactions"""
    client = BuddyClient()
    
    print("=== 🤖 Bit Buddy Interactive Demo ===\n")
    
    try:
        # Initial greeting
        print("👋 Meeting your bit buddy for the first time...\n")
        response = client.hello()
        print_buddy_response(response, "First Meeting")
        
        # Show personality and drive knowledge
        personality = client.get_personality()
        print(f"📊 Personality Profile:")
        print(f"   Name: {personality['name']}")
        print(f"   Arc: {personality['narrative_arc']}")
        print(f"   Humor: {personality['humor']}/10")
        print(f"   Curiosity: {personality['curiosity']}/10") 
        print(f"   Formality: {personality['formality']}/10")
        print(f"   Temperature: {personality['temperature']}")
        print(f"   Mood: {personality['current_mood']}\n")
        
        # Show drive knowledge
        try:
            drive_info = requests.get(f"{client.base_url}/drive").json()
            print(f"🗂️  Drive Knowledge:")
            print(f"   Watching: {drive_info['watching']}")
            print(f"   Document folders: {drive_info['discovered']['document_folders']}")
            print(f"   Download folders: {drive_info['discovered']['download_folders']}")
            print(f"   Photo folders: {drive_info['discovered']['photo_folders']}")
            print(f"   Project folders: {drive_info['discovered']['project_folders']}")
            print(f"   Total files: {drive_info['discovered']['total_files']}")
            print(f"   {drive_info['personality_influence']}\n")
        except:
            print("🗂️  Drive scan in progress...\n")
        
        # Ask drive-specific questions  
        queries = [
            "What's in my documents folder?",
            "Help me find my photos",
            "My downloads folder is messy",
            "Show me my project files",
            "What files do you know about?"
        ]
        
        print("💬 Having a conversation...\n")
        for query in queries:
            print(f"👤 You: {query}")
            response = client.ask(query)
            print_buddy_response(response)
            time.sleep(1)
        
        # Add some story events
        print("📖 Adding some story beats...\n")
        events = [
            ("discovery", "Found old family photos in archives"),
            ("cleanup", "Organized messy Downloads folder"), 
            ("success", "Successfully backed up important files")
        ]
        
        for event_type, note in events:
            print(f"📝 Story: {note}")
            response = client.narrate(event_type, note)
            print_buddy_response(response, "Story Reaction")
            time.sleep(1)
        
        # Show personality evolution option
        print("🎲 Want to see your buddy reincarnate? (y/N): ", end="")
        if input().lower().startswith('y'):
            print("\n✨ Randomizing personality...\n")
            response = client.randomize()
            print(f"🔄 {response['message']}")
            
            new_personality = response['new_personality']
            print(f"📊 New Personality:")
            print(f"   Name: {new_personality['name']}")
            print(f"   Arc: {new_personality['arc']}")
            print(f"   Humor: {new_personality['humor']}/10")
            print(f"   Curiosity: {new_personality['curiosity']}/10")
            print(f"   Formality: {new_personality['formality']}/10\n")
            
            # Greet the new personality
            response = client.hello()
            print_buddy_response(response, "New Buddy")
        
        print("🎉 Demo complete! Your bit buddy is persistent and will remember everything.")
        print("💡 Try running the server (python server.py) and explore the API!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Bit Buddy server!")
        print("💡 Start the server first: python server.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Your bit buddy will be waiting for you.")
        sys.exit(0)

if __name__ == "__main__":
    demo_personality_evolution()