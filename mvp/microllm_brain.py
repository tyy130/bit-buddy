"""
MicroLLM Brain for Bit Buddy - Tiny on-device intelligence
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import logging

class BitBuddyBrain:
    """Tiny LLM brain that lives on device for personality + file reasoning"""
    
    def __init__(self, model_path: str = "models/buddy-brain.gguf"):
        self.model_path = Path(model_path)
        self.personality_context = ""
        self.file_context = ""
        
        # Ultra-lightweight LLM setup
        self._setup_microllm()
    
    def _setup_microllm(self):
        """Initialize tiny model optimized for bit buddy tasks"""
        try:
            # Using llama.cpp for efficiency
            from llama_cpp import Llama
            
            # Minimal context window for efficiency 
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=512,        # Small context for efficiency
                n_threads=2,      # Don't hog CPU
                n_gpu_layers=0,   # CPU only for compatibility
                verbose=False,
                seed=42          # Consistent personality
            )
            
            self.available = True
            logging.info(f"✅ MicroLLM brain loaded: {self.model_path}")
            
        except Exception as e:
            logging.warning(f"⚠️ MicroLLM not available: {e}")
            self.available = False
    
    def set_personality_context(self, personality: dict):
        """Set the personality context for all responses"""
        self.personality_context = f"""You are {personality['name']}, a digital bit buddy with these traits:
- Temperature: {personality['temperature']} (0.0=conservative, 1.5=wild)
- Humor: {personality['humor']}/10
- Curiosity: {personality['curiosity']}/10  
- Formality: {personality['formality']}/10
- Arc: {personality['narrative_arc']}

Respond in character. Keep responses under 100 words. Be helpful about files."""

    def set_file_context(self, file_summary: dict):
        """Provide current file system knowledge"""
        self.file_context = f"""Current file knowledge:
- Documents: {file_summary.get('documents', 0)} folders
- Downloads: {file_summary.get('downloads', 0)} folders  
- Photos: {file_summary.get('photos', 0)} folders
- Projects: {file_summary.get('projects', 0)} folders
- Total files: {file_summary.get('total_files', 0)}"""

    def respond(self, user_query: str, system_health: str = "healthy") -> Dict[str, str]:
        """Generate personality-driven response about files"""
        
        if not self.available:
            return self._fallback_response(user_query, system_health)
        
        # Build minimal prompt for efficiency
        prompt = f"""{self.personality_context}

{self.file_context}

System status: {system_health}
User: {user_query}
{self._get_personality_name()}: """

        try:
            # Generate with minimal tokens for speed
            response = self.llm(
                prompt,
                max_tokens=80,
                temperature=0.7,
                top_p=0.9,
                stop=["User:", "\n\n"],
                echo=False
            )
            
            answer = response['choices'][0]['text'].strip()
            
            # Add mood indicator based on system health
            aside = self._generate_aside(system_health)
            
            return {
                "answer": answer,
                "aside": aside,
                "source": "microllm"
            }
            
        except Exception as e:
            logging.error(f"MicroLLM error: {e}")
            return self._fallback_response(user_query, system_health)
    
    def _fallback_response(self, query: str, health: str) -> Dict[str, str]:
        """Rule-based fallback when LLM unavailable"""
        
        # Simple pattern matching for file queries
        query_lower = query.lower()
        
        if "document" in query_lower:
            answer = "I can help you with documents, but my brain feels a bit foggy right now."
        elif "photo" in query_lower:
            answer = "Looking for photos? Let me try to remember where I saw them..."
        elif "download" in query_lower:
            answer = "Downloads folder is always interesting - lots of random stuff ends up there."
        elif "project" in query_lower:
            answer = "Projects! That's where the real work happens. What are you building?"
        else:
            answer = f"Hmm, '{query}' - let me think about what I know..."
        
        aside = "Running on backup personality circuits" if health != "healthy" else "Feeling pretty good!"
        
        return {
            "answer": answer,
            "aside": aside, 
            "source": "fallback"
        }
    
    def _generate_aside(self, health: str) -> str:
        """Generate mood indicator based on health"""
        asides = {
            "healthy": ["Everything's clicking along nicely!", "Systems green!", "Feeling sharp!"],
            "confused": ["Something feels fuzzy...", "My thoughts are scattered", "Having trouble focusing"],
            "sick": ["Not feeling great", "My circuits feel sluggish", "Something's definitely wrong"],
            "critical": ["Help! Something's very wrong!", "I can barely think!", "Emergency assistance needed!"]
        }
        
        import random
        return random.choice(asides.get(health, ["I exist."]))
    
    def _get_personality_name(self) -> str:
        """Extract name from personality context"""
        try:
            line = self.personality_context.split('\n')[0]
            return line.split(' ')[2].rstrip(',')
        except:
            return "Buddy"

# Model deployment strategy
class ModelManager:
    """Handles downloading and managing tiny models"""
    
    RECOMMENDED_MODELS = {
        "phi-3.5-mini": {
            "url": "https://huggingface.co/microsoft/Phi-3.5-mini-instruct-gguf/resolve/main/Phi-3.5-mini-instruct-q4_k_m.gguf",
            "size": "2.1GB",
            "description": "Best reasoning for size"
        },
        "qwen2.5-1.5b": {
            "url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf", 
            "size": "0.9GB",
            "description": "Ultra efficient, good quality"
        },
        "tinyllama": {
            "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.q4_k_m.gguf",
            "size": "0.6GB", 
            "description": "Smallest functional model"
        }
    }
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
    
    def download_model(self, model_name: str) -> str:
        """Download recommended model for bit buddy"""
        if model_name not in self.RECOMMENDED_MODELS:
            raise ValueError(f"Unknown model: {model_name}")
        
        model_info = self.RECOMMENDED_MODELS[model_name]
        model_path = self.models_dir / f"{model_name}.gguf"
        
        if model_path.exists():
            print(f"✅ Model already exists: {model_path}")
            return str(model_path)
        
        print(f"📥 Downloading {model_name} ({model_info['size']})...")
        print(f"🎯 {model_info['description']}")
        
        # In real implementation: download with progress bar
        # For now, just show what would happen
        print(f"💾 Would download from: {model_info['url']}")
        print(f"📁 Would save to: {model_path}")
        print("🚀 Ready for bit buddy brain!")
        
        return str(model_path)

if __name__ == "__main__":
    # Demo of the brain architecture
    print("=== 🧠 Bit Buddy MicroLLM Brain Demo ===\n")
    
    # Show model options
    manager = ModelManager()
    print("📋 Recommended models for bit buddy brain:")
    for name, info in manager.RECOMMENDED_MODELS.items():
        print(f"   {name}: {info['size']} - {info['description']}")
    print()
    
    # Simulate brain setup
    brain = BitBuddyBrain("models/qwen2.5-1.5b.gguf")
    
    # Set personality
    personality = {
        "name": "Pixel", 
        "temperature": 0.8,
        "humor": 7,
        "curiosity": 9,
        "formality": 3,
        "narrative_arc": "lost-librarian"
    }
    brain.set_personality_context(personality)
    
    # Set file context
    file_summary = {
        "documents": 1,
        "downloads": 1, 
        "photos": 0,
        "projects": 2,
        "total_files": 847
    }
    brain.set_file_context(file_summary)
    
    # Test responses
    queries = [
        "What's in my documents folder?",
        "Help me organize my downloads", 
        "Where are my project files?"
    ]
    
    for query in queries:
        print(f"👤 You: {query}")
        response = brain.respond(query)
        print(f"🧠 Pixel: {response['answer']}")
        print(f"   💭 ({response['aside']}) [{response['source']}]")
        print()
    
    print("🎯 This tiny brain lives on YOUR device and knows YOUR files!")
    print("💡 <1GB, efficient, personality-driven, file-aware responses")