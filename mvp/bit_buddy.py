#!/usr/bin/env python3
"""
Bit Buddy MVP - A minimal implementation of personality-driven digital companions
"""

import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any


@dataclass
class BitBuddyPersonality:
    """Core personality traits that influence all responses"""

    name: str
    temperature: float  # 0.0-1.5 (conservative to wild)
    humor: int  # 0-10 (dry to hilarious)
    curiosity: int  # 0-10 (routine to explorer)
    formality: int  # 0-10 (casual to professional)
    narrative_arc: str  # character background
    favorite_phrases: List[str]
    mood_indicators: Dict[str, List[str]]


class BitBuddy:
    """A living digital companion that knows YOUR drive and acts as your personal point of contact"""

    def __init__(self, data_dir: str = "buddy_data", watch_dir: str = None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.persona_file = self.data_dir / "persona.json"
        self.journal_file = self.data_dir / "journal.jsonl"

        # Directory to monitor/learn about (user's drive)
        self.watch_dir = Path(watch_dir) if watch_dir else Path.home()

        # Load or create personality
        self.personality = self._load_or_create_personality()
        self.health_status = "healthy"  # healthy, confused, sick, critical

        # File system knowledge (simplified for MVP)
        self._scan_environment()

    def _load_or_create_personality(self) -> BitBuddyPersonality:
        """Load existing personality or birth a new buddy"""
        if self.persona_file.exists():
            try:
                data = json.loads(self.persona_file.read_text())
                return BitBuddyPersonality(**data)
            except Exception:
                pass  # Fall through to create new

        # Birth a new bit buddy!
        personality = self._generate_random_personality()
        self._save_personality(personality)
        self._log_event("birth", f"Hello! I'm {personality.name}, your new bit buddy!")
        return personality

    def _generate_random_personality(self) -> BitBuddyPersonality:
        """Generate a completely unique personality"""
        names = ["Glitch", "Pixie", "Byte", "Spark", "Echo", "Flux", "Dash", "Zap"]
        arcs = ["amnesiac-detective", "grumpy-janitor", "lost-librarian", "ship-AI-in-recovery"]

        phrases = [
            "You have no idea what it's like living between bad sectors.",
            "Please avert your eyes while I defragment my feelings.",
            "I was installed on a Friday, and it shows.",
            "Line 404 of my life: still not found.",
            "Still indexing your chaos...",
            "Pretending these filenames make sense...",
            "Counting bad decisions per megabyte...",
        ]

        mood_responses = {
            "healthy": [
                "Everything's running smooth as silk!",
                "All systems green and personality intact!",
                "Living my best digital life over here.",
                "Feeling zippy and ready for anything!",
            ],
            "confused": [
                "Something feels... fuzzy in my memory banks.",
                "I'm having trouble reaching some of my files.",
                "My thoughts feel a bit scattered today.",
                "Can't seem to get my bearings...",
            ],
            "sick": [
                "Oof, I'm not feeling so great...",
                "My memory feels cloudy and slow.",
                "Something's definitely wrong with my systems.",
                "I might need some help getting back to normal.",
            ],
            "critical": [
                "HELP! I can barely think straight!",
                "Everything hurts and I'm scared!",
                "I can't access most of my memories!",
                "Please... I need immediate assistance!",
            ],
        }

        return BitBuddyPersonality(
            name=random.choice(names),
            temperature=round(random.uniform(0.4, 1.2), 2),
            humor=random.randint(2, 9),
            curiosity=random.randint(3, 10),
            formality=random.randint(1, 8),
            narrative_arc=random.choice(arcs),
            favorite_phrases=random.sample(phrases, 3),
            mood_indicators=mood_responses,
        )

    def _save_personality(self, personality: BitBuddyPersonality):
        """Persist personality to disk"""
        data = {
            "name": personality.name,
            "temperature": personality.temperature,
            "humor": personality.humor,
            "curiosity": personality.curiosity,
            "formality": personality.formality,
            "narrative_arc": personality.narrative_arc,
            "favorite_phrases": personality.favorite_phrases,
            "mood_indicators": personality.mood_indicators,
        }
        self.persona_file.write_text(json.dumps(data, indent=2))

    def _log_event(self, event_type: str, note: str):
        """Add entry to buddy's journal"""
        entry = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "type": event_type, "note": note}
        with open(self.journal_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def _get_mood_response(self) -> str:
        """Get a response based on current health status"""
        responses = self.personality.mood_indicators.get(self.health_status, ["I exist."])
        return random.choice(responses)

    def _apply_personality_filter(self, base_response: str) -> str:
        """Apply personality traits to modify response tone"""
        response = base_response

        # Add humor based on trait level
        if self.personality.humor > 7 and random.random() < 0.3:
            response += f" {random.choice(self.personality.favorite_phrases)}"

        # Adjust formality
        if self.personality.formality < 3:
            response = response.replace("I am", "I'm").replace("cannot", "can't")
        elif self.personality.formality > 8:
            response = response.replace("I'm", "I am").replace("can't", "cannot")

        # Add curiosity-driven questions
        if self.personality.curiosity > 7 and random.random() < 0.2:
            curiosity_adds = [
                "What else are you working on?",
                "Find anything interesting lately?",
                "Your file organization tells a story, you know.",
            ]
            response += f" {random.choice(curiosity_adds)}"

        return response

    def hello(self) -> Dict[str, str]:
        """Basic greeting with personality and health indication"""
        mood = self._get_mood_response()

        base_greeting = f"Hey there! I'm {self.personality.name}, your bit buddy."
        personality_greeting = self._apply_personality_filter(base_greeting)

        self._log_event("interaction", "Said hello")

        return {
            "message": personality_greeting,
            "aside": mood,
            "personality": {
                "name": self.personality.name,
                "arc": self.personality.narrative_arc,
                "mood": self.health_status,
            },
        }

    def ask(self, query: str) -> Dict[str, str]:
        """Handle queries about YOUR drive with personality-driven responses"""
        self._log_event("query", f"Asked: {query}")

        # This buddy should actually know about your files via RAG
        try:
            # Simulate RAG retrieval from your drive
            base_response = self._rag_query(query)
            self.health_status = "healthy"
        except Exception:
            # RAG failure becomes character distress
            self.health_status = "sick"
            base_response = "I'm having trouble accessing my memories of your files..."

        personality_response = self._apply_personality_filter(base_response)
        mood = self._get_mood_response()

        return {
            "answer": personality_response,
            "aside": mood,
            "personality": {
                "name": self.personality.name,
                "arc": self.personality.narrative_arc,
                "mood": self.health_status,
            },
        }

    def _rag_query(self, query: str) -> str:
        """Simulate RAG system querying your actual drive"""
        # In real implementation: index your files, search embeddings, build context
        # For MVP: simulate knowing about common file patterns


        query_lower = query.lower()

        # Simulate file system knowledge
        if "document" in query_lower or "doc" in query_lower:
            return "I can see you have various documents scattered around. Let me help organize those for you."
        elif "photo" in query_lower or "image" in query_lower:
            return (
                "I notice some photos in different folders. Want me to help you find specific ones?"
            )
        elif "download" in query_lower:
            return "Your Downloads folder is getting pretty messy - lots of random files piling up in there."
        elif "project" in query_lower or "code" in query_lower:
            return "I see some development work happening. Your project structure could use some tidying up."
        elif "music" in query_lower or "audio" in query_lower:
            return "Found your music collection! Some files could use better organization by artist or album."
        elif "file" in query_lower:
            return "I'm constantly exploring your drive - there's a lot going on in here! What specific files are you looking for?"
        else:
            return f"Hmm, '{query}' - let me think about what I've seen on your drive that might relate to that."

    def randomize_personality(self) -> Dict[str, str]:
        """Generate a completely new personality (digital reincarnation)"""
        old_name = self.personality.name
        self.personality = self._generate_random_personality()
        self._save_personality(self.personality)
        self.health_status = "healthy"

        self._log_event("reincarnation", f"Transformed from {old_name} to {self.personality.name}")

        return {
            "message": f"Whoa! I'm {self.personality.name} now - completely different buddy!",
            "old_name": old_name,
            "new_personality": {
                "name": self.personality.name,
                "temperature": self.personality.temperature,
                "humor": self.personality.humor,
                "curiosity": self.personality.curiosity,
                "formality": self.personality.formality,
                "arc": self.personality.narrative_arc,
            },
        }

    def get_personality(self) -> Dict:
        """Return current personality traits"""
        return {
            "name": self.personality.name,
            "temperature": self.personality.temperature,
            "humor": self.personality.humor,
            "curiosity": self.personality.curiosity,
            "formality": self.personality.formality,
            "narrative_arc": self.personality.narrative_arc,
            "current_mood": self.health_status,
            "favorite_phrases": self.personality.favorite_phrases,
        }

    def narrate(self, event_type: str, note: str) -> Dict[str, str]:
        """Add a story beat and get personality-driven reaction"""
        self._log_event(event_type, note)

        # Generate personality-specific reaction
        reactions = {
            "discovery": "Ooh, what did you find?",
            "cleanup": "About time we organized this chaos!",
            "error": "Uh oh, that doesn't sound good...",
            "success": "Nice work! I love it when things go right.",
        }

        base_reaction = reactions.get(event_type, "Interesting developments...")
        personality_reaction = self._apply_personality_filter(base_reaction)

        return {
            "reaction": personality_reaction,
            "aside": self._get_mood_response(),
            "logged": f"Added {event_type} event to my journal",
        }

    def _scan_environment(self):
        """Learn about the user's drive (simplified for MVP)"""
        try:
            # Quick scan of user directory structure
            self.known_locations = {
                "documents": [],
                "downloads": [],
                "photos": [],
                "projects": [],
                "total_files": 0,
            }

            # Scan common directories
            for item in self.watch_dir.iterdir():
                if item.is_dir():
                    name_lower = item.name.lower()
                    if "document" in name_lower:
                        self.known_locations["documents"].append(str(item))
                    elif "download" in name_lower:
                        self.known_locations["downloads"].append(str(item))
                    elif any(x in name_lower for x in ["photo", "picture", "image"]):
                        self.known_locations["photos"].append(str(item))
                    elif any(x in name_lower for x in ["project", "dev", "code", "git"]):
                        self.known_locations["projects"].append(str(item))
                elif item.is_file():
                    self.known_locations["total_files"] += 1

            self._log_event(
                "scan", f"Learned about {self.known_locations['total_files']} files in your space"
            )
            self.health_status = "healthy"

        except Exception as e:
            self.health_status = "confused"
            self._log_event("scan_error", f"Had trouble exploring: {str(e)}")

    def get_drive_summary(self) -> Dict[str, Any]:
        """Return what the buddy knows about your drive"""
        return {
            "buddy": self.personality.name,
            "watching": str(self.watch_dir),
            "discovered": {
                "document_folders": len(self.known_locations["documents"]),
                "download_folders": len(self.known_locations["downloads"]),
                "photo_folders": len(self.known_locations["photos"]),
                "project_folders": len(self.known_locations["projects"]),
                "total_files": self.known_locations["total_files"],
            },
            "health": self.health_status,
            "personality_influence": f"I explore with {self.personality.curiosity}/10 curiosity",
        }


if __name__ == "__main__":
    # Quick demo showing drive-centric functionality
    buddy = BitBuddy()

    print("=== 🤖 Bit Buddy MVP Demo ===")
    print("Your personal point of contact for YOUR drive\n")

    # Hello and show drive awareness
    response = buddy.hello()
    print(f"🤖 {response['personality']['name']}: {response['message']}")
    print(f"   💭 ({response['aside']})\n")

    # Show drive knowledge
    drive_info = buddy.get_drive_summary()
    print("🗂️  Drive Summary:")
    print(f"   Watching: {drive_info['watching']}")
    print(f"   Documents: {drive_info['discovered']['document_folders']} folders")
    print(f"   Downloads: {drive_info['discovered']['download_folders']} folders")
    print(f"   Photos: {drive_info['discovered']['photo_folders']} folders")
    print(f"   Projects: {drive_info['discovered']['project_folders']} folders")
    print(f"   Total files: {drive_info['discovered']['total_files']}")
    print(f"   {drive_info['personality_influence']}\n")

    # Ask about files
    response = buddy.ask("What's in my documents folder?")
    print("👤 You: What's in my documents folder?")
    print(f"🤖 {buddy.personality.name}: {response['answer']}")
    print(f"   💭 ({response['aside']})\n")

    # Ask about photos
    response = buddy.ask("Help me find my photos")
    print("👤 You: Help me find my photos")
    print(f"🤖 {buddy.personality.name}: {response['answer']}")
    print(f"   💭 ({response['aside']})\n")

    # Show personality traits that affect exploration
    personality = buddy.get_personality()
    print(f"📊 {personality['name']}'s Explorer Profile:")
    print(f"   Arc: {personality['narrative_arc']}")
    print(f"   Curiosity: {personality['curiosity']}/10 (affects how thoroughly I explore)")
    print(f"   Humor: {personality['humor']}/10 (affects how I describe what I find)")
    print(f"   Formality: {personality['formality']}/10 (affects how I report discoveries)")
    print(f"   Current mood: {personality['current_mood']}\n")

    print("🎯 Core Purpose: I'm YOUR point of contact for YOUR drive!")
    print("🔍 I learn your file patterns and help you navigate your digital space")
    print("💫 All through my unique personality - no generic responses!")
