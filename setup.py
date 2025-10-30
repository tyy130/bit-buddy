#!/usr/bin/env python3
"""
Bit Buddy Quick Setup - Get your first digital companion running in minutes!
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Optional
import platform

def print_banner():
    """Print welcome banner"""
    print("""
    🤖 =============================================== 🤖
    |                                               |
    |           🎯 BIT BUDDY QUICK SETUP 🎯          |
    |                                               |
    |     Your Personal File System Companion      |
    |                                               |
    🤖 =============================================== 🤖
    """)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version < (3, 8):
        print("❌ Python 3.8+ required. Current version:", f"{version.major}.{version.minor}.{version.micro}")
        print("   Please install Python 3.8 or newer: https://python.org/downloads/")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible!")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("   Try running manually: pip install -r requirements.txt")
        return False

def create_example_directories():
    """Create example directories for demonstration"""
    home = Path.home()
    
    # Create demo directories
    demo_dirs = {
        "Documents": home / "Documents" / "BitBuddy_Demo",
        "Photos": home / "Pictures" / "BitBuddy_Demo", 
        "Projects": home / "Desktop" / "BitBuddy_Projects"
    }
    
    created_dirs = []
    
    for name, path in demo_dirs.items():
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created_dirs.append((name, path))
            
            # Add some sample files
            if name == "Documents":
                (path / "welcome.txt").write_text(
                    "Welcome to Bit Buddy!\n\n"
                    "Your digital companion is now watching this folder.\n"
                    "Try asking: 'What files do you see?' or 'Tell me about yourself!'\n\n"
                    "Bit buddies learn your file organization patterns and develop\n"
                    "unique personalities based on what they discover.\n\n"
                    "Have fun exploring with your new digital friend! 🤖✨"
                )
                
                (path / "README.md").write_text("""
# My Bit Buddy Demo

This folder is being watched by your bit buddy! 

## What your buddy can do:
- 🔍 **Find files instantly** - "Find my vacation photos"
- 📝 **Remember content** - "What did I write about yesterday?"
- 🎭 **Develop personality** - Each buddy grows unique traits
- 🌐 **Connect with other buddies** - Share knowledge across devices
- 💡 **Smart suggestions** - "You might want to organize these files..."

## Try these questions:
- "What's the most recent file here?"
- "Tell me about your personality"
- "How would you organize this folder?"
- "What patterns do you see in my files?"

Your buddy learns from your files while respecting your privacy - 
everything stays local on your machine! 🔒
                """)
    
    if created_dirs:
        print("\n📁 Created demo directories:")
        for name, path in created_dirs:
            print(f"   📂 {name}: {path}")
    
    return demo_dirs

def setup_first_buddy(demo_dirs):
    """Set up the first bit buddy"""
    print("\n🤖 Setting up your first bit buddy...")
    
    # Import deployment manager
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from deploy import BuddyDeploymentManager
        
        manager = BuddyDeploymentManager()
        
        # Download recommended model
        print("\n📥 Downloading AI model (this may take a few minutes)...")
        import asyncio
        
        def progress_callback(downloaded, total):
            if total > 0:
                progress = (downloaded / total) * 100
                print(f"\r  Progress: {progress:.1f}% ({downloaded//1024//1024}MB/{total//1024//1024}MB)", 
                      end="", flush=True)
        
        model_path = asyncio.run(manager.download_model("qwen2.5-1.5b", progress_callback))
        print("\n✅ Model downloaded!")
        
        # Create buddy
        buddy_name = input("\n🎭 What would you like to name your buddy? (or press Enter for 'Pixel'): ").strip()
        if not buddy_name:
            buddy_name = "Pixel"
        
        # Choose watch directory
        print("\n📂 Choose a directory for your buddy to watch:")
        for i, (name, path) in enumerate(demo_dirs.items(), 1):
            print(f"   {i}. {name} ({path})")
        
        while True:
            try:
                choice = input(f"Enter choice (1-{len(demo_dirs)}) or custom path: ").strip()
                
                if choice.isdigit() and 1 <= int(choice) <= len(demo_dirs):
                    watch_dir = list(demo_dirs.values())[int(choice) - 1]
                    break
                else:
                    # Custom path
                    watch_dir = Path(choice)
                    if watch_dir.exists() and watch_dir.is_dir():
                        break
                    else:
                        print(f"   ❌ Directory doesn't exist: {choice}")
                        continue
            except (ValueError, IndexError):
                print(f"   ❌ Please enter 1-{len(demo_dirs)} or a valid path")
        
        # Create the buddy
        buddy_config = manager.create_buddy(
            name=buddy_name,
            watch_dir=watch_dir,
            model_id="qwen2.5-1.5b",
            mesh_enabled=True
        )
        
        print(f"\n✅ Created buddy '{buddy_name}' watching {watch_dir}")
        
        return buddy_name, manager
    
    except Exception as e:
        print(f"❌ Failed to setup buddy: {e}")
        return None, None

def create_startup_script(buddy_name, manager):
    """Create a simple startup script"""
    if not buddy_name or not manager:
        return
    
    script_content = f'''#!/usr/bin/env python3
"""
Quick start script for {buddy_name}
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def main():
    try:
        from enhanced_buddy import EnhancedBitBuddy
        from mesh_network import BuddyMeshNetwork
        
        print("🤖 Starting {buddy_name}...")
        
        # Load buddy config
        buddy_config = {manager.config["buddies"][buddy_name]}
        
        # Create buddy
        buddy = EnhancedBitBuddy(
            buddy_dir=Path(buddy_config["buddy_dir"]),
            watch_dir=Path(buddy_config["watch_dir"]),
            model_path=Path(buddy_config["model_path"])
        )
        
        # Add mesh networking
        mesh = BuddyMeshNetwork(buddy, 0)
        buddy.mesh = mesh
        await mesh.start_server()
        
        print(f"🎯 {{buddy.personality.name}} is now active!")
        print(f"📂 Watching: {{buddy.watch_dir}}")
        print(f"🌐 Mesh network enabled on port {{mesh.port}}")
        print()
        print("💬 Try asking your buddy:")
        print("   • 'What files do you see?'")
        print("   • 'Tell me about yourself!'") 
        print("   • 'How would you organize these files?'")
        print()
        print("🌟 Your buddy will learn and develop personality as it explores!")
        print("⏹️  Press Ctrl+C to stop")
        
        # Interactive mode
        while True:
            try:
                question = input("\\n💭 Ask your buddy: ")
                if question.lower() in ['quit', 'exit', 'bye']:
                    break
                
                response = buddy.ask(question)
                print(f"🤖 {{buddy.personality.name}}: {{response['answer']}}")
                
            except KeyboardInterrupt:
                break
        
    except ImportError as e:
        print(f"❌ Missing dependency: {{e}}")
        print("   Run: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {{e}}")
    finally:
        if 'buddy' in locals() and hasattr(buddy, 'mesh'):
            await buddy.mesh.shutdown()
        print(f"\\n👋 {{buddy_name}} shutting down. See you later!")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    script_path = Path("start_buddy.py")
    script_path.write_text(script_content)
    
    print(f"\n📜 Created startup script: {script_path}")
    print("   Run with: python start_buddy.py")

def show_next_steps(buddy_name):
    """Show what to do next"""
    print(f"""
🎉 =============================================== 🎉
           🤖 {buddy_name.upper()} IS READY! 🤖
🎉 =============================================== 🎉

🚀 QUICK START:
   python start_buddy.py

🛠️  ADVANCED MANAGEMENT:
   python deploy.py list-buddies           # See all your buddies
   python deploy.py start-buddy {buddy_name}      # Start in background
   python deploy.py health                 # System health check

💡 WHAT YOUR BUDDY CAN DO:
   ✅ Instantly find files by content
   ✅ Remember what you've worked on  
   ✅ Develop a unique personality
   ✅ Connect with other buddies via mesh network
   ✅ Give smart organization suggestions

🎭 PERSONALITY GROWTH:
   Your buddy will develop traits like humor, curiosity, and empathy
   based on the files it discovers and your interactions!

🌐 MESH NETWORKING:
   Create multiple buddies to form a helpful digital community.
   They'll share knowledge while maintaining unique personalities.

📚 LEARN MORE:
   • README.md - Full documentation  
   • .github/copilot-instructions.md - For developers
   • enhanced_buddy.py - Core implementation

🎯 HAVE FUN exploring with your new digital companion! 
   Your files have never had such an enthusiastic friend! 🤖✨
    """)

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check if already setup
    buddy_dir = Path.home() / ".bit_buddies"
    if buddy_dir.exists() and any(buddy_dir.glob("buddies/*/config.json")):
        print("🔍 Existing bit buddy installation found!")
        print(f"   Location: {buddy_dir}")
        
        response = input("\nWould you like to create another buddy? (y/N): ").lower()
        if response not in ['y', 'yes']:
            print("\n💡 Use 'python deploy.py list-buddies' to see existing buddies")
            return 0
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Create demo directories
    demo_dirs = create_example_directories()
    
    # Setup first buddy
    buddy_name, manager = setup_first_buddy(demo_dirs)
    if not buddy_name:
        return 1
    
    # Create startup script
    create_startup_script(buddy_name, manager)
    
    # Show next steps
    show_next_steps(buddy_name)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled. Run again anytime!")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("   Please report this issue with the full error message.")
        sys.exit(1)