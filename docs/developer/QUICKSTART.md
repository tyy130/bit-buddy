# 🚀 Quick Start - Local Development & Testing

## For Developers: Get Bit Buddy Running in 5 Minutes

### Prerequisites
- Python 3.11+ installed
- Git installed
- Windows/macOS/Linux machine (not Codespaces - GUI required)

### Step 1: Clone and Setup (2 minutes)

```bash
# Clone the repository
git clone https://github.com/tyy130/bit-buddy.git
cd bit-buddy

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run Pre-Build Tests (30 seconds)

```bash
# Verify everything is set up correctly
python pre_build_test.py
```

Expected output:
```
🎉 ALL TESTS PASSED - READY TO BUILD!
```

### Step 3: Start the Backend Server (1 minute)

```bash
# Option A: Using PowerShell script (Windows)
.\scripts\serve.ps1

# Option B: Direct uvicorn command (all platforms)
uvicorn app.server:app --host 127.0.0.1 --port 8000 --reload
```

**Verify**: Open http://127.0.0.1:8000 in browser
- Should see: `{"service":"LLM Stick RAG","status":"ok",...}`

### Step 4: Launch the GUI (30 seconds)

```bash
# In a new terminal (keep server running)
python buddy_gui.py
```

**Expected behavior**:
1. Setup wizard appears (first run)
2. Enter buddy name (e.g., "Bitsy")
3. Choose data folder (or use default)
4. Personality gets generated
5. Chat window opens

### Step 5: Test Chat (1 minute)

Try these example queries in the chat window:
- "Hello!"
- "What files do you know about?"
- "Tell me about yourself"

**Note**: Responses require an LLM backend running (llama.cpp or Ollama). If not configured, you'll get an error message.

---

## Optional: Setup LLM Backend

### Option A: llama.cpp (Recommended)

```bash
# Download llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
make

# Download a model (TinyLlama example)
mkdir models
cd models
wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

# Start server
cd ..
./server -m models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --port 8080
```

### Option B: Ollama (Easier)

```bash
# Install Ollama from https://ollama.ai/

# Download a model
ollama pull tinyllama

# Server starts automatically
```

### Update config.yaml

Edit `app/config.yaml`:

```yaml
llm:
  provider: "llamacpp"  # or "ollama"
  llamacpp:
    endpoint: "http://127.0.0.1:8080/completion"
  ollama:
    model: "tinyllama"
    endpoint: "http://127.0.0.1:11434/api/generate"
```

---

## Building the Executable

### Generate Icons (if not already done)

```bash
python generate_icon.py
```

### Build with PyInstaller

```bash
# Install PyInstaller if not already installed
pip install pyinstaller

# Build the executable
pyinstaller buddy.spec
```

**Output locations**:
- Windows: `dist\BitBuddy.exe`
- macOS: `dist/BitBuddy.app`
- Linux: `dist/BitBuddy`

### Test the Executable

```bash
# Windows
dist\BitBuddy.exe

# macOS
open dist/BitBuddy.app

# Linux
./dist/BitBuddy
```

---

## Development Workflow

### Making Changes

1. **Edit code** in your favorite editor
2. **Test changes** with `python pre_build_test.py`
3. **Run tests** with `pytest tests/`
4. **Format code** with `black --line-length 79 <file.py>`
5. **Check lint** with `flake8 <file.py>`

### Hot Reload Development

```bash
# Server with auto-reload
uvicorn app.server:app --reload --host 127.0.0.1 --port 8000

# Make changes to app/server.py, app/rag.py, etc.
# Server automatically restarts
```

### Testing Different Personalities

```bash
# PowerShell (Windows)
.\scripts\persona.randomize.ps1

# Or manually
curl -X POST http://127.0.0.1:8000/persona/randomize
```

---

## Troubleshooting

### "ModuleNotFoundError" when running GUI

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### GUI window doesn't appear

```bash
# Check if tkinter is installed
python -c "import tkinter; print('Tkinter OK')"

# If error, install tkinter:
# Ubuntu/Debian:
sudo apt-get install python3-tk

# macOS (usually pre-installed)
# Windows (included with Python installer)
```

### Server returns 503 "RAG not initialized"

```bash
# Check config.yaml has correct embedding model
# Should be: BAAI/bge-small-en-v1.5

# Check index directory exists
ls app/index/

# If empty, rebuild index:
curl -X POST http://127.0.0.1:8000/reindex
```

### "Cannot connect to LLM" errors

```bash
# Check if llama.cpp or Ollama is running
# llama.cpp: http://127.0.0.1:8080/health
# Ollama: http://127.0.0.1:11434/api/tags

# Verify config.yaml has correct endpoints
```

### PyInstaller build fails

```bash
# Clean previous builds
pyinstaller --clean buddy.spec

# If still fails, check hidden imports in buddy.spec
# Add any missing modules to hiddenimports list
```

---

## File Structure Overview

```
bit-buddy/
├── app/                    # Backend application
│   ├── server.py          # FastAPI server (main entry)
│   ├── rag.py             # RAG engine
│   ├── persona.py         # Personality system
│   ├── mesh.py            # External interface
│   └── config.yaml        # Configuration
├── custodian/             # User data directory
│   ├── manifest.yaml      # Custodian metadata
│   ├── policy.yaml        # Privacy/sharing rules
│   ├── persona.yaml       # Personality state
│   └── peers.json         # Network peers
├── scripts/               # Helper scripts
│   ├── serve.ps1          # Start server (Windows)
│   └── persona.*.ps1      # Personality management
├── buddy_gui.py           # Desktop GUI application
├── installer.py           # System analyzer
├── generate_icon.py       # Icon generator
├── buddy.spec             # PyInstaller config
└── requirements.txt       # Python dependencies
```

---

## Common Tasks

### Add Knowledge to RAG

```bash
# 1. Add documents to custodian/kb/
cp ~/Documents/important.pdf custodian/kb/

# 2. Rebuild index
curl -X POST http://127.0.0.1:8000/reindex

# 3. Query in GUI or via API
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What does important.pdf say about X?"}'
```

### Change Personality Traits

```bash
# PowerShell
.\scripts\persona.set.ps1 -Traits '{"humor":9,"curiosity":3}'

# Or via API
curl -X POST http://127.0.0.1:8000/persona \
  -H "Content-Type: application/json" \
  -d '{"humor":9,"curiosity":3}'
```

### View Logs

```bash
# Server logs (if running in foreground)
# Just check terminal output

# Or redirect to file
uvicorn app.server:app --log-level debug > server.log 2>&1
```

---

## Resources

- **Full Build Instructions**: `BUILD_INSTRUCTIONS.md`
- **Deployment Status**: `DEPLOYMENT_SUMMARY.md`
- **End User Guide**: `END_USER_GUIDE.md`
- **Architecture**: `.github/copilot-instructions.md`
- **Icon Guide**: `assets/ICON_GUIDE.md`

---

## Quick Reference - All Commands

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Test
python pre_build_test.py
pytest tests/

# Develop
uvicorn app.server:app --reload --host 127.0.0.1 --port 8000
python buddy_gui.py

# Build
python generate_icon.py
pyinstaller buddy.spec

# Format/Lint
black --line-length 79 <file.py>
flake8 <file.py>
```

---

**Happy coding! 🎉**

Your bit buddy is ready to come to life. Start the server, launch the GUI, and meet your new digital companion!
