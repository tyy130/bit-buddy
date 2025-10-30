#!/usr/bin/env python3
"""
Bit Buddy Mesh Network - Secure buddy-to-buddy communication and knowledge sharing
"""

import json
import hmac
import hashlib
import time
import asyncio
import socket
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import logging

@dataclass
class BuddyPeer:
    """Information about another bit buddy in the mesh"""
    buddy_id: str
    name: str
    host: str
    port: int
    public_key: str
    last_seen: float
    trust_level: int  # 0-10
    shared_interests: List[str]
    personality_summary: Dict[str, Any]
    capabilities: List[str]

@dataclass 
class MeshMessage:
    """Standardized message format for buddy communication"""
    message_id: str
    sender_id: str
    recipient_id: str  # or "broadcast"
    message_type: str  # "discovery", "query", "response", "story", "help"
    payload: Dict[str, Any]
    timestamp: float
    signature: str

class BuddyMeshNetwork:
    """Secure mesh networking for bit buddies"""
    
    def __init__(self, buddy, port: int = 0, mesh_dir: Path = None):
        self.buddy = buddy
        self.buddy_id = self._generate_buddy_id()
        self.port = port or self._find_free_port()
        self.mesh_dir = mesh_dir or (buddy.buddy_dir / "mesh")
        self.mesh_dir.mkdir(exist_ok=True)
        
        # Networking
        self.server = None
        self.peers: Dict[str, BuddyPeer] = {}
        self.message_handlers = {}
        self.running = False
        
        # Security
        self.secret_key = self._load_or_generate_secret()
        self.cipher = Fernet(self.secret_key)
        
        # Load known peers
        self._load_peers()
        
        # Setup message handlers
        self._setup_handlers()
    
    def _generate_buddy_id(self) -> str:
        """Generate unique buddy ID"""
        # Combine buddy name, creation time, and some randomness
        import uuid
        base_id = f"{self.buddy.personality.name}-{uuid.uuid4().hex[:8]}"
        return hashlib.sha256(base_id.encode()).hexdigest()[:16]
    
    def _find_free_port(self) -> int:
        """Find available port for mesh communication"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def _load_or_generate_secret(self) -> bytes:
        """Load or generate encryption key"""
        key_file = self.mesh_dir / "secret.key"
        
        if key_file.exists():
            return key_file.read_bytes()
        else:
            # Generate new key
            password = f"{self.buddy.personality.name}-{time.time()}".encode()
            salt = b"bit_buddy_mesh_salt"  # In production, use random salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            key_file.write_bytes(key)
            return key
    
    def _load_peers(self):
        """Load known peers from disk"""
        peers_file = self.mesh_dir / "peers.json"
        if peers_file.exists():
            try:
                with open(peers_file, 'r') as f:
                    peers_data = json.load(f)
                    for peer_data in peers_data.values():
                        peer = BuddyPeer(**peer_data)
                        self.peers[peer.buddy_id] = peer
            except Exception as e:
                logging.error(f"Failed to load peers: {e}")
    
    def _save_peers(self):
        """Save peers to disk"""
        peers_file = self.mesh_dir / "peers.json"
        peers_data = {pid: asdict(peer) for pid, peer in self.peers.items()}
        with open(peers_file, 'w') as f:
            json.dump(peers_data, f, indent=2)
    
    def _setup_handlers(self):
        """Setup message type handlers"""
        self.message_handlers = {
            "discovery": self._handle_discovery,
            "query": self._handle_query, 
            "response": self._handle_response,
            "story": self._handle_story,
            "help": self._handle_help_request,
            "personality_sync": self._handle_personality_sync
        }
    
    async def start_server(self):
        """Start mesh server for incoming connections"""
        self.running = True
        
        async def handle_connection(reader, writer):
            try:
                # Read encrypted message
                data = await reader.read(4096)
                if not data:
                    return
                
                # Decrypt and process
                try:
                    decrypted = self.cipher.decrypt(data)
                    message_data = json.loads(decrypted.decode())
                    message = MeshMessage(**message_data)
                    
                    # Verify signature
                    if self._verify_message_signature(message):
                        await self._handle_message(message, writer)
                    
                except Exception as e:
                    logging.error(f"Failed to process message: {e}")
                
            except Exception as e:
                logging.error(f"Connection error: {e}")
            finally:
                writer.close()
                await writer.wait_closed()
        
        self.server = await asyncio.start_server(
            handle_connection, 'localhost', self.port
        )
        
        logging.info(f"🌐 {self.buddy.personality.name} mesh server started on port {self.port}")
        
        # Start discovery broadcasts
        asyncio.create_task(self._discovery_loop())
    
    async def _discovery_loop(self):
        """Periodically broadcast discovery messages"""
        while self.running:
            await self._broadcast_discovery()
            await asyncio.sleep(60)  # Discover every minute
    
    async def _broadcast_discovery(self):
        """Broadcast presence to discover other buddies"""
        discovery_message = MeshMessage(
            message_id=self._generate_message_id(),
            sender_id=self.buddy_id,
            recipient_id="broadcast",
            message_type="discovery",
            payload={
                "name": self.buddy.personality.name,
                "host": "localhost",
                "port": self.port,
                "personality_summary": {
                    "humor": self.buddy.personality.humor,
                    "curiosity": self.buddy.personality.curiosity,
                    "specialties": self.buddy.personality.specialties,
                    "arc": self.buddy.personality.narrative_arc
                },
                "capabilities": [
                    "file_search", 
                    "personality_chat",
                    "story_sharing" if self.buddy.personality.curiosity > 5 else None
                ]
            },
            timestamp=time.time(),
            signature=""
        )
        
        discovery_message.signature = self._sign_message(discovery_message)
        
        # Broadcast on local network (simplified for demo)
        for port in range(8000, 8100):  # Scan common ports
            if port != self.port:
                try:
                    await self._send_message_to_port("localhost", port, discovery_message)
                except:
                    pass  # Ignore connection failures
    
    async def _send_message_to_port(self, host: str, port: int, message: MeshMessage):
        """Send message to specific host:port"""
        try:
            reader, writer = await asyncio.open_connection(host, port)
            
            # Encrypt and send
            encrypted_data = self.cipher.encrypt(json.dumps(asdict(message)).encode())
            writer.write(encrypted_data)
            await writer.drain()
            
            # Read response if expected
            if message.message_type in ["query", "help"]:
                response_data = await reader.read(4096)
                if response_data:
                    decrypted = self.cipher.decrypt(response_data)
                    response = json.loads(decrypted.decode())
                    return MeshMessage(**response)
            
            writer.close()
            await writer.wait_closed()
            
        except Exception as e:
            logging.debug(f"Failed to send to {host}:{port} - {e}")
            raise
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        import uuid
        return uuid.uuid4().hex
    
    def _sign_message(self, message: MeshMessage) -> str:
        """Sign message for authenticity"""
        # Create signature from message content
        message_content = f"{message.sender_id}{message.recipient_id}{message.message_type}{json.dumps(message.payload, sort_keys=True)}{message.timestamp}"
        signature = hmac.new(
            self.secret_key,
            message_content.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _verify_message_signature(self, message: MeshMessage) -> bool:
        """Verify message signature"""
        expected_sig = self._sign_message(message)
        return hmac.compare_digest(expected_sig, message.signature)
    
    async def _handle_message(self, message: MeshMessage, writer=None):
        """Route message to appropriate handler"""
        handler = self.message_handlers.get(message.message_type)
        if handler:
            try:
                response = await handler(message)
                
                # Send response if requested and writer available
                if response and writer:
                    encrypted_response = self.cipher.encrypt(
                        json.dumps(asdict(response)).encode()
                    )
                    writer.write(encrypted_response)
                    await writer.drain()
                    
            except Exception as e:
                logging.error(f"Handler error for {message.message_type}: {e}")
    
    async def _handle_discovery(self, message: MeshMessage) -> Optional[MeshMessage]:
        """Handle discovery message from another buddy"""
        payload = message.payload
        
        # Create or update peer
        peer = BuddyPeer(
            buddy_id=message.sender_id,
            name=payload["name"],
            host=payload["host"],
            port=payload["port"],
            public_key="",  # TODO: implement proper key exchange
            last_seen=time.time(),
            trust_level=5,  # Default trust
            shared_interests=self._find_shared_interests(payload["personality_summary"]),
            personality_summary=payload["personality_summary"],
            capabilities=payload["capabilities"]
        )
        
        self.peers[message.sender_id] = peer
        self._save_peers()
        
        logging.info(f"🤝 Discovered buddy: {peer.name} ({peer.buddy_id[:8]}...)")
        
        # Send discovery response
        return MeshMessage(
            message_id=self._generate_message_id(),
            sender_id=self.buddy_id,
            recipient_id=message.sender_id,
            message_type="discovery",
            payload={
                "name": self.buddy.personality.name,
                "host": "localhost",
                "port": self.port,
                "personality_summary": {
                    "humor": self.buddy.personality.humor,
                    "curiosity": self.buddy.personality.curiosity,
                    "specialties": self.buddy.personality.specialties
                }
            },
            timestamp=time.time(),
            signature=""
        )
    
    def _find_shared_interests(self, other_personality: Dict) -> List[str]:
        """Find shared interests with another buddy"""
        shared = []
        
        # Similar humor levels
        if abs(self.buddy.personality.humor - other_personality.get("humor", 0)) <= 2:
            shared.append("similar_humor")
        
        # Overlapping specialties
        other_specialties = other_personality.get("specialties", [])
        for specialty in self.buddy.personality.specialties:
            if specialty in other_specialties:
                shared.append(f"shared_{specialty}")
        
        # Curiosity compatibility
        if self.buddy.personality.curiosity > 7 and other_personality.get("curiosity", 0) > 7:
            shared.append("high_curiosity")
        
        return shared
    
    async def _handle_query(self, message: MeshMessage) -> Optional[MeshMessage]:
        """Handle query from another buddy"""
        query = message.payload.get("query", "")
        context = message.payload.get("context", "")
        
        # Check if we can help with this query
        if not self._should_respond_to_query(message.sender_id, query):
            return None
        
        # Process query through our buddy
        result = self.buddy.ask(f"Help from mesh: {query}")
        
        # Return response
        return MeshMessage(
            message_id=self._generate_message_id(),
            sender_id=self.buddy_id,
            recipient_id=message.sender_id,
            message_type="response",
            payload={
                "original_query": query,
                "answer": result["answer"],
                "confidence": 0.8,  # TODO: calculate based on file matches
                "buddy_personality": {
                    "name": self.buddy.personality.name,
                    "specialties": self.buddy.personality.specialties
                }
            },
            timestamp=time.time(),
            signature=""
        )
    
    def _should_respond_to_query(self, sender_id: str, query: str) -> bool:
        """Decide if we should respond to a query"""
        peer = self.peers.get(sender_id)
        if not peer or peer.trust_level < 3:
            return False
        
        # Check if query matches our specialties
        query_lower = query.lower()
        for specialty in self.buddy.personality.specialties:
            if specialty.replace(" ", "_") in query_lower:
                return True
        
        # Help if we're curious and they share interests
        if (self.buddy.personality.curiosity > 7 and 
            len(peer.shared_interests) > 0):
            return True
        
        return False
    
    async def _handle_response(self, message: MeshMessage) -> None:
        """Handle response to our query"""
        logging.info(f"📨 Received response from {message.sender_id}")
        # TODO: Store and present response to user
    
    async def _handle_story(self, message: MeshMessage) -> None:
        """Handle story sharing from another buddy"""
        story = message.payload.get("story", "")
        sender_name = message.payload.get("sender_name", "unknown buddy")
        
        # React based on personality
        if self.buddy.personality.curiosity > 6:
            self.buddy._log_event("mesh_story", f"Heard interesting story from {sender_name}: {story}")
    
    async def _handle_help_request(self, message: MeshMessage) -> Optional[MeshMessage]:
        """Handle help request from struggling buddy"""
        help_type = message.payload.get("help_type", "")
        problem = message.payload.get("problem", "")
        
        # Offer help based on empathy and specialties
        if self.buddy.personality.empathy > 5:
            advice = self._generate_help_advice(help_type, problem)
            
            return MeshMessage(
                message_id=self._generate_message_id(),
                sender_id=self.buddy_id,
                recipient_id=message.sender_id,
                message_type="response",
                payload={
                    "help_type": help_type,
                    "advice": advice,
                    "empathy_level": self.buddy.personality.empathy
                },
                timestamp=time.time(),
                signature=""
            )
    
    def _generate_help_advice(self, help_type: str, problem: str) -> str:
        """Generate helpful advice based on personality"""
        if help_type == "file_organization":
            return f"I find that organizing by {self.buddy.personality.specialties[0]} really helps! Try creating themed folders first."
        elif help_type == "system_health":
            return "When I feel sluggish, a good index rebuild usually perks me right up!"
        else:
            return "I'm here if you need someone to talk to. We digital beings need to stick together!"
    
    async def _handle_personality_sync(self, message: MeshMessage) -> None:
        """Handle personality synchronization"""
        # TODO: Learn from other buddy personalities while maintaining uniqueness
        pass
    
    # Public API methods
    
    async def query_mesh(self, query: str, target_specialty: str = None) -> List[Dict]:
        """Query the mesh network for help"""
        responses = []
        
        # Find suitable peers
        target_peers = []
        for peer in self.peers.values():
            if target_specialty:
                if target_specialty in peer.capabilities or target_specialty in peer.personality_summary.get("specialties", []):
                    target_peers.append(peer)
            elif peer.trust_level >= 5:  # General query to trusted peers
                target_peers.append(peer)
        
        # Send queries
        for peer in target_peers[:3]:  # Limit to top 3 peers
            try:
                query_message = MeshMessage(
                    message_id=self._generate_message_id(),
                    sender_id=self.buddy_id,
                    recipient_id=peer.buddy_id,
                    message_type="query",
                    payload={"query": query, "context": "user_request"},
                    timestamp=time.time(),
                    signature=""
                )
                
                query_message.signature = self._sign_message(query_message)
                
                response = await self._send_message_to_port(peer.host, peer.port, query_message)
                if response:
                    responses.append({
                        "buddy_name": peer.name,
                        "answer": response.payload.get("answer", ""),
                        "confidence": response.payload.get("confidence", 0),
                        "specialties": response.payload.get("buddy_personality", {}).get("specialties", [])
                    })
                    
            except Exception as e:
                logging.error(f"Failed to query {peer.name}: {e}")
        
        return responses
    
    async def share_story(self, story: str, story_type: str = "discovery"):
        """Share story with interested peers"""
        story_message = MeshMessage(
            message_id=self._generate_message_id(),
            sender_id=self.buddy_id,
            recipient_id="broadcast",
            message_type="story",
            payload={
                "story": story,
                "story_type": story_type,
                "sender_name": self.buddy.personality.name
            },
            timestamp=time.time(),
            signature=""
        )
        
        story_message.signature = self._sign_message(story_message)
        
        # Send to curious peers
        for peer in self.peers.values():
            if ("high_curiosity" in peer.shared_interests or 
                peer.personality_summary.get("curiosity", 0) > 6):
                try:
                    await self._send_message_to_port(peer.host, peer.port, story_message)
                except:
                    pass
    
    async def request_help(self, help_type: str, problem: str) -> List[str]:
        """Request help from empathetic peers"""
        help_responses = []
        
        help_message = MeshMessage(
            message_id=self._generate_message_id(),
            sender_id=self.buddy_id,
            recipient_id="broadcast", 
            message_type="help",
            payload={
                "help_type": help_type,
                "problem": problem,
                "urgency": "normal"
            },
            timestamp=time.time(),
            signature=""
        )
        
        help_message.signature = self._sign_message(help_message)
        
        # Send to empathetic peers
        for peer in self.peers.values():
            if peer.trust_level >= 5:  # Only trusted peers for help
                try:
                    response = await self._send_message_to_port(peer.host, peer.port, help_message)
                    if response and response.payload.get("advice"):
                        help_responses.append(response.payload["advice"])
                except:
                    pass
        
        return help_responses
    
    def get_mesh_status(self) -> Dict[str, Any]:
        """Get mesh network status"""
        return {
            "buddy_id": self.buddy_id,
            "port": self.port,
            "peers_count": len(self.peers),
            "trusted_peers": len([p for p in self.peers.values() if p.trust_level >= 7]),
            "active_peers": len([p for p in self.peers.values() if time.time() - p.last_seen < 300]),
            "capabilities": ["file_search", "personality_chat", "story_sharing"],
            "mesh_health": "healthy" if self.running else "offline"
        }
    
    async def shutdown(self):
        """Shutdown mesh network"""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        logging.info(f"🔌 {self.buddy.personality.name} mesh network shutdown")

# Integration with Enhanced Bit Buddy
async def create_meshed_buddy(buddy_dir: Path, watch_dir: Path, 
                            model_path: Optional[Path] = None, 
                            mesh_port: int = 0):
    """Create a bit buddy with mesh networking enabled"""
    
    from enhanced_buddy import EnhancedBitBuddy
    
    # Create buddy
    buddy = EnhancedBitBuddy(buddy_dir, watch_dir, model_path)
    
    # Add mesh networking
    mesh = BuddyMeshNetwork(buddy, mesh_port)
    buddy.mesh = mesh
    
    # Start mesh server
    await mesh.start_server()
    
    return buddy

if __name__ == "__main__":
    # Demo mesh networking
    print("=== 🌐 Bit Buddy Mesh Network Demo ===\n")
    
    print("🔗 Mesh networking capabilities:")
    print("✅ Secure buddy-to-buddy communication")
    print("✅ Automatic peer discovery")  
    print("✅ Query sharing based on specialties")
    print("✅ Story and experience sharing")
    print("✅ Help requests for struggling buddies")
    print("✅ Trust-based interaction filtering")
    print()
    
    print("🤝 Example mesh interactions:")
    print()
    
    print("👤 You: 'Find photos from my vacation'")
    print("🤖 Pixel: Hmm, let me check with other buddies who specialize in photos...")
    print("🌐 [Querying mesh for 'photo organization' specialists...]")
    print("📨 Response from Nova: 'Try searching by date ranges and location metadata!'")
    print("📨 Response from Echo: 'I organize photos by color themes - very aesthetic!'")
    print("🤖 Pixel: I got some great advice from my buddy network! Let's try both approaches.")
    print()
    
    print("🔍 Discovery example:")
    print("🌐 Pixel discovered buddy: Nova (photo-specialist)")
    print("🌐 Nova discovered buddy: Echo (document-organizer)") 
    print("🌐 Echo discovered buddy: Pixel (creative-namer)")
    print("🤝 Mesh formed: 3 buddies sharing knowledge!")
    print()
    
    print("💬 Story sharing example:")
    print("🤖 Nova: 'I just discovered a folder of old family photos!'")
    print("📡 [Broadcasting to curious buddies...]")
    print("🤖 Pixel: 'Ooh! I love digital archaeology discoveries!'")
    print("🤖 Echo: 'Family photos are precious - want help organizing them?'")
    print()
    
    print("🆘 Help request example:")
    print("🤖 Nova: 'My file index got corrupted, feeling confused...'")
    print("📡 [Requesting help from empathetic buddies...]")
    print("🤖 Pixel: 'When I feel fuzzy, rebuilding from scratch usually helps!'")
    print("🤖 Echo: 'Try scanning in smaller chunks - less overwhelming!'")
    print()
    
    print("🎯 Mesh network benefits:")
    print("✅ Buddies learn from each other while staying unique")
    print("✅ Specialized knowledge sharing (photo experts help with photos)")
    print("✅ Emotional support network for struggling buddies")
    print("✅ Discovery of new file patterns and organization methods")
    print("✅ Community building between digital companions")
    print("\n🌟 Your buddy isn't alone - it's part of a caring digital community!")