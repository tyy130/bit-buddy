# 🤖 Bit Buddy - Personal File System Companion

<p align="center">
  <img src="assets/bit-buddy-logo.png" alt="Bit Buddy Logo" width="400">
</p>

<p align="center">
  <em>Your files deserve a friend who truly knows them</em>
</p>

---

Bit Buddy is a **living digital companion** that inhabits your filesystem. Not just software that responds, but a unique entity with its own personality, moods, and genuine reactions to your data. Each bit buddy explores files with their own curiosity, gets overwhelmed by chaos in their own way, and celebrates discoveries with their unique voice.

## 🎨 Meet Your Companions

Choose from four unique starter characters, each with their own personality:

<p align="center">
  <img src="assets/characters/character_purple_green.png" width="120" alt="Glitch">
  <img src="assets/characters/character_orange_blue.png" width="120" alt="Citrus">
  <img src="assets/characters/character_teal_orange.png" width="120" alt="Slate">
  <img src="assets/characters/character_pink_green.png" width="120" alt="Nova">
</p>

<table align="center">
  <tr>
    <th>Glitch</th>
    <th>Citrus</th>
    <th>Slate</th>
    <th>Nova</th>
  </tr>
  <tr>
    <td>Chaotic Hacker</td>
    <td>Cheerful Optimist</td>
    <td>Wise Minimalist</td>
    <td>Energetic Sidekick</td>
  </tr>
  <tr>
    <td><em>"Living between bad sectors..."</em></td>
    <td><em>"Installed on a Friday!"</em></td>
    <td><em>"Processing... with purpose."</em></td>
    <td><em>"Line 404: still not found."</em></td>
  </tr>
</table>

## 🌟 What Makes Bit Buddy Special?

- **🎭 Autonomous Personality**: Each buddy generates completely unique traits on first boot and maintains them persistently
- **🔍 Instant File Intelligence**: Ask "Find my vacation photos from 2019" and get intelligent, personality-driven responses
- **🧠 Local AI Brain**: Everything runs on your machine - your privacy stays yours
- **🌐 Buddy Network**: Multiple buddies can share knowledge while maintaining their unique personalities
- **📈 Emergent Narrative**: Through daily interactions, each buddy develops its own story over time
- **💾 Lightweight**: Runs on <2GB RAM with micro-LLM models (TinyLlama, Qwen2.5, Phi-3.5)

## 🚀 Quick Start (5 Minutes)

### Option A: Desktop App (Recommended for New Users)

**Windows:**
```cmd
1. Download BitBuddySetup-1.0.0.exe
2. Run installer
3. Choose your drive and AI model
4. Pick your character (Glitch, Citrus, Slate, or Nova)
5. Start chatting with your new companion!
```

**macOS:**
```bash
1. Download BitBuddy.dmg
2. Drag to Applications
3. Launch and follow setup wizard
4. Choose your character
5. Begin your journey together!
```

### Option B: Developer Setup (Full Control)

The setup script automatically creates a virtual environment (avoiding PEP 668 issues on modern Python 3.12+ systems) and installs all dependencies.

```bash
# 1. Clone and setup (auto-creates venv)
git clone <repository>
cd bit-buddy
python3 setup.py

# 2. Follow the interactive setup
# - Creates virtual environment automatically
# - Installs all dependencies
# - Downloads AI model (~900MB)
# - Creates your first buddy
# - Sets up demo files

# 3. Start your buddy (auto-activates venv)
./start.sh        # Unix/macOS
# or
start.bat         # Windows

# 4. Chat with your new companion!
💭 Ask your buddy: What files do you see?
🤖 Pixel: I see some interesting documents here! There's a welcome.txt that seems excited to meet me, and a README.md that explains what I can do. I'm curious about that BitBuddy_Projects folder - are you working on something creative? 
```

**Virtual Environment Notes:**
- The venv is created automatically at `./venv`
- Use `./start.sh` or `start.bat` to auto-activate the venv
- For manual activation:
  - Unix/macOS: `source venv/bin/activate`
  - Windows: `venv\Scripts\activate`

### Option C: RAG Service Only (Production API)

For deploying just the RAG API service without the personality layer:

```bash
# 1. Setup with auto-venv (recommended)
python3 setup.py    # Creates venv and installs deps

# 2. Configure your knowledge base
mkdir -p kb
# Add your .txt, .md, .pdf, or .docx files to kb/

# 3. (Optional) Copy and customize environment variables
cp .env.example .env
# Edit .env to set LLM provider, embedding model, etc.

# 4. Start the RAG service (auto-activates venv)
./start.sh

# Or manually with venv activated:
source venv/bin/activate
uvicorn app.server:app --host 127.0.0.1 --port 8000

# 5. Check health
curl http://127.0.0.1:8000/health
# {"status":"healthy","rag_initialized":true,"ready":true}

# 6. Build the index
curl -X POST http://127.0.0.1:8000/reindex
# {"status":"ok","chunks":42}

# 7. Query your knowledge base
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"What is FastAPI?","k":5}'
```

**Note**: `/reindex` may take 30-60 seconds on first run as it downloads the embedding model and processes your knowledge base.

## 🎯 Core Features

### 🔍 **Smart File Discovery**
```
You: "Find documents about machine learning"
Buddy: "I found 3 papers in your Research folder and some Python notebooks in Projects. The 'neural_networks.pdf' looks particularly interesting - want me to summarize it?"
```

### 🎭 **Personality Development**  
Your buddy develops traits over time:
- **Humor Level (1-10)**: How playful vs. professional
- **Curiosity (1-10)**: How eagerly it explores new files
- **Specialties**: Areas of expertise (code, photos, documents)
- **Empathy**: How supportive it is during your work

### 🌐 **Mesh Networking**
Multiple buddies can communicate:
```
Pixel: "Hey Echo, the user is looking for photo organization tips"
Echo: "I'm great with photos! Try organizing by color themes - very aesthetic!"
Nova: "I prefer chronological with location metadata tags"
```

### 🧠 **Micro-LLM Brain**
- **Qwen2.5-1.5B**: Recommended model (934MB)
- **TinyLlama-1.1B**: Ultra-lightweight (669MB) 
- **Phi-3.5-Mini**: Microsoft's efficient model (2.3GB)

## 🏗️ Architecture

### Core Components

```
📁 enhanced_buddy.py     # Main buddy implementation
├── BitBuddyPersonality  # Personality engine with traits & growth
├── FileSystemRAG        # Smart file indexing & search  
├── MicroLLMBrain       # Local AI integration
└── EnhancedBitBuddy    # Orchestrates everything

📁 mesh_network.py       # Buddy-to-buddy communication
├── BuddyMeshNetwork    # Secure P2P networking
├── MeshMessage         # Standardized communication
└── Discovery & Trust   # Auto-discovery with trust levels

📁 deploy.py            # Management & deployment
├── BuddyDeploymentManager  # Install & configure buddies
├── Model Management     # Download & manage AI models
└── Health Monitoring   # System health & optimization
```

### Data Flow

```
👤 User Question → 🤖 Buddy Personality → 🔍 File Search → 🧠 AI Processing → 💬 Personal Response
                              ↓
                    🌐 Mesh Network (consult other buddies if needed)
```

## 🛠️ Advanced Usage

### Creating Multiple Buddies

```bash
# Create specialized buddies
python deploy.py create-buddy "CodeWizard" ~/Projects --model qwen2.5-1.5b
python deploy.py create-buddy "PhotoFriend" ~/Pictures --model tinyllama-1.1b  
python deploy.py create-buddy "DocMaster" ~/Documents --model phi3.5-mini

# Start them all
python deploy.py start-buddy CodeWizard --port 8001
python deploy.py start-buddy PhotoFriend --port 8002
python deploy.py start-buddy DocMaster --port 8003
```

### Buddy Management

```bash
# List all your buddies
python deploy.py list-buddies

# Check system health
python deploy.py health

# Download additional models
python deploy.py download-model phi3.5-mini

# Export/Import buddy configurations
python deploy.py export-buddy Pixel pixel_backup.zip
python deploy.py import-buddy pixel_backup.zip --name PixelJr
```

### Testing & Debugging

```bash
# Run comprehensive test suite
python deploy.py test --type all --verbose

# Run specific test types
python deploy.py test --type unit          # Fast unit tests
python deploy.py test --type integration  # Full integration tests  
python deploy.py test --type performance  # Performance benchmarks

# Debug a specific buddy
python deploy.py debug MyBuddy --operation "file_scan"

# Create buddy with debug mode enabled
python deploy.py create-buddy DebugBuddy ~/Documents --debug

# Manual debugging tools
python debug_tools.py check-files ~/Documents
python debug_tools.py monitor --duration 60
python test_runner.py --stress --stress-duration 30
```

### Development & Customization

```bash
# Generate copilot instructions for AI development
# Already created in .github/copilot-instructions.md

# Run full test suite with coverage
python test_runner.py --all --verbose

# Enable verbose logging
export BUDDY_LOG_LEVEL=DEBUG
python start_buddy.py

# Performance monitoring
python debug_tools.py monitor --duration 120
```

## 🎭 Personality Examples

### The Curator (High Formality, Low Humor)
```
User: "Organize my photos"
Buddy: "I recommend a systematic approach: create folders by year, then by event type. This ensures efficient retrieval and maintains chronological integrity."
```

### The Creative (High Humor, High Curiosity)  
```
User: "Organize my photos"
Buddy: "Ooh, photos! 📸 I'm thinking rainbow themes - imagine opening 'Blue Vibes' and finding all your ocean pics! Or we could go full chaos with 'Happy Accidents' for blurry artistic shots? 🎨"
```

### The Detective (High Curiosity, Medium Empathy)
```
User: "I can't find my resume"
Buddy: "Let me investigate! 🔍 I see several document versions... Found resume_final.docx, resume_FINAL_v2.docx, and resume_actually_final.pdf. Plot twist: they're all different! Want me to compare them?"
```

## 🌐 Mesh Network Features

- **🔐 Secure Communication**: Encrypted buddy-to-buddy messages
- **🤝 Auto Discovery**: Buddies find each other automatically on local network
- **🎯 Specialty Routing**: Questions automatically go to expert buddies
- **💝 Story Sharing**: Buddies share interesting discoveries with curious peers
- **🆘 Help Network**: Struggling buddies get support from empathetic peers
- **📊 Trust Levels**: Dynamic trust system prevents spam

## 📋 System Requirements

### Minimum (TinyLlama)
- **RAM**: 2GB available
- **CPU**: 2+ cores
- **Storage**: 2GB free space
- **OS**: Windows, macOS, or Linux

### Recommended (Qwen2.5)
- **RAM**: 4GB available  
- **CPU**: 4+ cores, 3GHz+
- **Storage**: 5GB free space
- **Network**: For mesh features

### Optimal (Phi-3.5)
- **RAM**: 8GB available
- **CPU**: 8+ cores or Apple Silicon
- **Storage**: 10GB free space
- **SSD**: For best performance

## 🧪 Testing & Development

### 🌐 GitHub-Based Testing (No Local Dependencies)

**Option 1: GitHub Codespaces (Recommended)**
```bash
# 1. Push repo to GitHub
# 2. Open "Code" → "Codespaces" → "Create codespace"  
# 3. Wait for auto-setup (installs everything)
# 4. Test immediately:
python -m pytest tests/ -v
./docker-mesh-test.sh
```

**Option 2: GitHub Actions (Automatic)**
```bash
# Push code - tests run automatically
git push origin main
# Check "Actions" tab for results across all platforms
```

**Option 3: Local Testing (Requires Python)**
```bash
# Install dependencies first
pip install -r requirements.txt
python setup.py --development

# Run tests
python test_runner.py --all --verbose
python debug_tools.py --check-system
```

### 🐳 Container Testing
```bash
# Test in isolated containers (no local Python needed)
docker build -t bit-buddy-test .
docker run -it bit-buddy-test python -m pytest -v

# Test mesh networking between containers
./docker-mesh-test.sh
```

## 🐛 Troubleshooting

### Common Issues

## 🔧 Troubleshooting

**"Cannot GET /" when visiting server**
```bash
# Make sure the server is actually running
ps aux | grep uvicorn

# Check server health
curl http://127.0.0.1:8000/health

# View server logs if started in background
tail -f /tmp/server.log

# Restart with proper logging
uvicorn app.server:app --host 127.0.0.1 --port 8000 --log-level info
```

**"RAG service not available" (503 error)**
```bash
# Check /health endpoint for the specific error
curl http://127.0.0.1:8000/health
# {"status":"unhealthy","rag_initialized":false,"ready":false,"error":"..."}

# Common causes:
# 1. Unsupported embedding model - update app/config.yaml
# 2. Missing dependencies - pip install -r requirements.txt
# 3. Memory issues - try a smaller embedding model

# Fix embedding model
# Edit app/config.yaml and set:
#   embedder:
#     model: "BAAI/bge-small-en-v1.5"
#     dim: 384
```

**"/reindex endpoint hangs or times out"**
```bash
# The embedding model downloads ~66MB on first run and may take 30-60s
# If it hangs indefinitely, there may be resource constraints

# Workaround: Create a pre-built index manually
python - <<'PY'
import numpy as np, json, os
os.makedirs("index", exist_ok=True)
# Create minimal dummy index
emb = np.random.randn(1, 384).astype(np.float32)
emb = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-12)
np.save("index/embeddings.npy", emb)
with open("index/meta.jsonl", "w") as f:
    f.write('{"path":"test.txt","chunk_id":0,"chars":100}\n')
print("✓ Created dummy index")
PY

# Then restart the server - it will load the pre-built index
```

**"LLM not responding in /chat"**
```bash
# The /chat endpoint requires either llama.cpp or Ollama running

# Option 1: Start llama.cpp server (if using llamacpp provider)
# Download llama.cpp and start with:
# ./server --model models/your-model.gguf --port 8080

# Option 2: Start Ollama (if using ollama provider)
ollama serve &
ollama pull qwen2.5:1.5b-instruct

# Then verify config in app/config.yaml matches your setup
```

**"externally-managed-environment" error (PEP 668)**
```bash
# This is solved automatically by setup.py which creates a virtual environment
# Simply run:
python3 setup.py

# The script will:
# 1. Create a venv at ./venv
# 2. Install all dependencies into the venv
# 3. Create start.sh/start.bat scripts to auto-activate the venv
```

**"Python not found" / "Dependencies missing"**
```bash
# Use GitHub Codespaces instead - zero setup required
# Or install Python from python.org first
# See test-local-alternative.md for detailed options
```

**"Model download failed"**
```bash
# Check internet connection and disk space
python deploy.py health
# Try alternate model
python deploy.py download-model tinyllama-1.1b
```

**"Buddy seems slow"**  
```bash
# Check system resources and performance
python deploy.py health
python deploy.py debug MyBuddy

# Try lighter model
python deploy.py create-buddy NewBuddy ~/Documents --model tinyllama-1.1b

# Run performance tests
python deploy.py test --type performance
```

**"Mesh network not working"**
```bash
# Check firewall settings (ports 8000-8100)
# Ensure buddies on same network
# Check buddy logs for connection errors
```

### Getting Help

1. **Check Health**: `python deploy.py health`
2. **Debug Issues**: `python deploy.py debug {buddy_name}`
3. **Run Tests**: `python deploy.py test --type all`
4. **View Logs**: Look for buddy logs in `~/.bit_buddies/buddies/{name}/`
5. **Performance Check**: `python debug_tools.py monitor --duration 60`
6. **Community**: Join discussions in Issues
7. **Documentation**: See `.github/copilot-instructions.md` for developers

## 🎯 Roadmap

### Version 1.1
- [ ] Web dashboard for buddy management
- [ ] Voice interaction support  
- [ ] Advanced personality evolution
- [ ] Plugin system for custom file types

### Version 1.2  
- [ ] Cloud sync (optional, encrypted)
- [ ] Mobile companion app
- [ ] Advanced mesh routing
- [ ] Buddy marketplace for sharing personalities

### Version 2.0
- [ ] Multi-modal models (vision + text)
- [ ] Collaborative workspaces
- [ ] Advanced AI training from user feedback
- [ ] Enterprise deployment options

## 🤝 Contributing

We welcome contributions! Your buddy wants friends to help it grow:

1. **Fork** the repository
2. **Create** a feature branch
3. **Follow** the coding style in `.github/copilot-instructions.md`  
4. **Test** with your own buddies
5. **Submit** a pull request

### Development Setup
```bash
# Clone for development
git clone <repository>
cd bit-buddy

# Run setup (auto-creates venv and installs deps)
python3 setup.py

# Or manually create venv and install dev dependencies
python3 -m venv venv
source venv/bin/activate  # Unix/macOS
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
pip install pytest pytest-asyncio

# Run tests
pytest

# Create test buddy
python deploy.py create-buddy TestBuddy ~/test_files --model tinyllama-1.1b
```

## 📜 License

MIT License - See LICENSE file for details.

Your buddy's friendship is free, but the code that makes it possible is shared with love! 💝

## 🌟 Inspiration

Bit Buddy was inspired by:
- **Johnny Castaway**: The beloved 90s screensaver companion
- **Clippy**: Microsoft's helpful (if sometimes annoying) assistant  
- **Tamagotchi**: Digital pets that grow and develop
- **JARVIS**: AI that truly knows and helps with your digital life

*"What if your files had a friend who genuinely cared about them?"* 

---

Made with 💖 for humans who believe their digital life deserves a caring companion.

**Start your journey**: `python3 setup.py && ./start.sh` 🚀
