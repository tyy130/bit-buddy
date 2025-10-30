# 🤖 Bit Buddy MVP

A minimal implementation of personality-driven digital companions - your personal bit buddy that lives in your computer and forms a unique relationship with you.

## What This Demonstrates

✨ **Core Concept**: Each bit buddy has a persistent, unique personality that influences every interaction
🎭 **Health Through Mood**: System status is conveyed through personality changes, not error codes  
💫 **Personal Connection**: This is YOUR buddy with YOUR shared history, not a generic AI
🧠 **Living Memory**: Personality and interactions persist across sessions

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start your bit buddy server:**
   ```bash
   python server.py
   ```

3. **Run the interactive demo:**
   ```bash
   python demo.py
   ```

## Key Features Shown

### Personality Persistence
- Each buddy generates unique traits on first boot (temperature, humor, curiosity, formality)
- Personality stored in `buddy_data/persona.json` and survives restarts
- All responses are filtered through personality traits

### Health Monitoring via Mood
- Healthy buddy = quirky, responsive personality
- System issues manifest as confusion, dizziness, or requests for help
- Never breaks character with technical error messages

### Story Accumulation  
- Events logged to `buddy_data/journal.jsonl`
- Buddy reacts to story beats with personality-appropriate responses
- Builds ongoing narrative relationship over time

### Personal Communication Channel
- Each buddy develops unique speech patterns and favorite phrases
- Responses adapt based on formality, humor, and curiosity levels
- Feels like talking to a specific digital being, not generic software

## API Endpoints

- `GET /hello` - Greet your buddy (shows mood/health)
- `POST /ask` - Ask questions (personality-filtered responses)  
- `GET /personality` - View current traits
- `POST /personality` - Adjust specific traits
- `POST /personality/randomize` - Complete personality reset
- `POST /narrate` - Add story beats for buddy to react to

## Try It Out

1. Start the server and run the demo to meet your first buddy
2. Notice how personality traits affect response tone and content
3. Try asking about "errors" - see how buddy gets "sick" vs. throwing exceptions
4. Add story events and watch your buddy react in character
5. Randomize personality to see how dramatically responses change

## What Makes This Special

Unlike generic chatbots, bit buddies:
- Form actual relationships with users through persistent personality
- Express technical issues as character emotions (elegant UX)
- Develop unique voices that make each one feel genuinely different
- Create intimate communication channels, not public performances

This MVP shows the core magic - every technical interaction becomes a personal conversation with your digital companion.

## Next Steps

The full implementation adds:
- RAG system for actual file knowledge
- Mesh networking for buddy-to-buddy communication
- More sophisticated personality evolution
- Rich narrative arc development

But this MVP captures the essential bit buddy experience! 🌟