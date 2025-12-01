#!/usr/bin/env python3
"""
Bit Buddy Mesh Networking
Enables peer-to-peer communication between bit buddies.
"""

import hashlib
import logging
import secrets
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


@dataclass
class MeshMessage:
    """Message for peer-to-peer communication"""

    message_id: str
    sender_id: str
    recipient_id: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: float
    signature: str
    ttl: int = 10  # Time-to-live for message forwarding

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "message_type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "ttl": self.ttl,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MeshMessage":
        """Create message from dictionary"""
        return cls(
            message_id=data["message_id"],
            sender_id=data["sender_id"],
            recipient_id=data["recipient_id"],
            message_type=data["message_type"],
            payload=data["payload"],
            timestamp=data["timestamp"],
            signature=data["signature"],
            ttl=data.get("ttl", 10),
        )


@dataclass
class BuddyPeer:
    """Represents a peer buddy in the mesh network"""

    peer_id: str
    name: str
    address: str
    port: int
    public_key: str = ""
    last_seen: float = field(default_factory=time.time)
    capabilities: List[str] = field(default_factory=list)
    trust_level: int = 0  # 0-10, increases with successful interactions

    def is_active(self, timeout_seconds: float = 300) -> bool:
        """Check if peer is still active"""
        return time.time() - self.last_seen < timeout_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert peer to dictionary"""
        return {
            "peer_id": self.peer_id,
            "name": self.name,
            "address": self.address,
            "port": self.port,
            "public_key": self.public_key,
            "last_seen": self.last_seen,
            "capabilities": self.capabilities,
            "trust_level": self.trust_level,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BuddyPeer":
        """Create peer from dictionary"""
        return cls(
            peer_id=data["peer_id"],
            name=data["name"],
            address=data["address"],
            port=data["port"],
            public_key=data.get("public_key", ""),
            last_seen=data.get("last_seen", time.time()),
            capabilities=data.get("capabilities", []),
            trust_level=data.get("trust_level", 0),
        )


class BuddyMeshNetwork:
    """Mesh network manager for buddy peer-to-peer communication"""

    def __init__(
        self,
        buddy_id: str,
        buddy_name: str,
        data_dir: Path,
        port: int = 0,
    ):
        """Initialize mesh network

        Args:
            buddy_id: Unique identifier for this buddy
            buddy_name: Display name for this buddy
            data_dir: Directory for storing mesh data
            port: Port to listen on (0 for auto-assign)
        """
        self.buddy_id = buddy_id
        self.buddy_name = buddy_name
        self.data_dir = Path(data_dir)
        self.port = port

        # Network state
        self.peers: Dict[str, BuddyPeer] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.message_cache: Dict[str, MeshMessage] = {}
        self.running = False

        # Secret key for signing messages
        self._secret_key = secrets.token_hex(32)

        # Create data directory
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logging.info(f"🌐 Mesh network initialized for {buddy_name} ({buddy_id})")

    def start(self) -> bool:
        """Start the mesh network

        Returns:
            True if started successfully
        """
        if self.running:
            logging.warning("Mesh network already running")
            return False

        try:
            self.running = True
            logging.info(f"🌐 Mesh network started on port {self.port}")
            return True
        except Exception as e:
            logging.error(f"Failed to start mesh network: {e}")
            return False

    def stop(self):
        """Stop the mesh network"""
        self.running = False
        logging.info("🌐 Mesh network stopped")

    def add_peer(self, peer: BuddyPeer) -> bool:
        """Add a peer to the network

        Args:
            peer: Peer to add

        Returns:
            True if peer was added
        """
        if peer.peer_id == self.buddy_id:
            logging.warning("Cannot add self as peer")
            return False

        self.peers[peer.peer_id] = peer
        logging.info(f"🤝 Added peer: {peer.name} ({peer.peer_id})")
        return True

    def remove_peer(self, peer_id: str) -> bool:
        """Remove a peer from the network

        Args:
            peer_id: ID of peer to remove

        Returns:
            True if peer was removed
        """
        if peer_id in self.peers:
            del self.peers[peer_id]
            logging.info(f"👋 Removed peer: {peer_id}")
            return True
        return False

    def get_active_peers(self, timeout_seconds: float = 300) -> List[BuddyPeer]:
        """Get list of active peers

        Args:
            timeout_seconds: Consider peer inactive after this many seconds

        Returns:
            List of active peers
        """
        return [p for p in self.peers.values() if p.is_active(timeout_seconds)]

    def create_message(
        self,
        recipient_id: str,
        message_type: str,
        payload: Dict[str, Any],
    ) -> MeshMessage:
        """Create a new message

        Args:
            recipient_id: ID of recipient buddy
            message_type: Type of message (query, response, broadcast, etc.)
            payload: Message payload

        Returns:
            New MeshMessage
        """
        message_id = secrets.token_hex(16)
        timestamp = time.time()

        # Create signature
        sign_data = f"{message_id}{self.buddy_id}{recipient_id}{timestamp}"
        signature = hashlib.sha256(
            (sign_data + self._secret_key).encode()
        ).hexdigest()

        return MeshMessage(
            message_id=message_id,
            sender_id=self.buddy_id,
            recipient_id=recipient_id,
            message_type=message_type,
            payload=payload,
            timestamp=timestamp,
            signature=signature,
        )

    def send_message(self, message: MeshMessage) -> bool:
        """Send a message to a peer

        Args:
            message: Message to send

        Returns:
            True if message was sent successfully
        """
        if not self.running:
            logging.warning("Cannot send message: mesh network not running")
            return False

        if message.recipient_id not in self.peers:
            logging.warning(f"Unknown recipient: {message.recipient_id}")
            return False

        # Cache message
        self.message_cache[message.message_id] = message

        # In a real implementation, this would send over the network
        logging.debug(f"📤 Sent message {message.message_id} to {message.recipient_id}")
        return True

    def broadcast_message(
        self,
        message_type: str,
        payload: Dict[str, Any],
    ) -> int:
        """Broadcast a message to all peers

        Args:
            message_type: Type of message
            payload: Message payload

        Returns:
            Number of peers message was sent to
        """
        sent_count = 0
        for peer_id in self.peers:
            message = self.create_message(peer_id, message_type, payload)
            if self.send_message(message):
                sent_count += 1

        logging.info(f"📢 Broadcast {message_type} to {sent_count} peers")
        return sent_count

    def register_handler(
        self,
        message_type: str,
        handler: Callable[[MeshMessage], Optional[Dict[str, Any]]],
    ):
        """Register a message handler

        Args:
            message_type: Type of message to handle
            handler: Handler function
        """
        self.message_handlers[message_type] = handler
        logging.debug(f"Registered handler for {message_type}")

    def handle_message(self, message: MeshMessage) -> Optional[Dict[str, Any]]:
        """Handle an incoming message

        Args:
            message: Message to handle

        Returns:
            Response payload if any
        """
        # Check if we've already processed this message
        if message.message_id in self.message_cache:
            logging.debug(f"Ignoring duplicate message {message.message_id}")
            return None

        # Cache the message
        self.message_cache[message.message_id] = message

        # Update peer last seen
        if message.sender_id in self.peers:
            self.peers[message.sender_id].last_seen = time.time()

        # Find and call handler
        handler = self.message_handlers.get(message.message_type)
        if handler:
            try:
                return handler(message)
            except Exception as e:
                logging.error(f"Error handling message: {e}")
                return None

        logging.warning(f"No handler for message type: {message.message_type}")
        return None

    def discover_peers(self, timeout_seconds: float = 5.0) -> List[BuddyPeer]:
        """Discover peers on the local network

        Args:
            timeout_seconds: How long to wait for responses

        Returns:
            List of discovered peers
        """
        # In a real implementation, this would use mDNS or similar
        logging.info(f"🔍 Discovering peers (timeout: {timeout_seconds}s)")
        return []

    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics

        Returns:
            Network statistics
        """
        active_peers = self.get_active_peers()
        return {
            "buddy_id": self.buddy_id,
            "buddy_name": self.buddy_name,
            "running": self.running,
            "port": self.port,
            "total_peers": len(self.peers),
            "active_peers": len(active_peers),
            "messages_cached": len(self.message_cache),
            "handlers_registered": len(self.message_handlers),
        }


if __name__ == "__main__":
    # Demo usage
    import tempfile

    print("🌐 Bit Buddy Mesh Network Demo\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create two buddies
        buddy1 = BuddyMeshNetwork(
            buddy_id="buddy-001",
            buddy_name="Nova",
            data_dir=Path(temp_dir) / "buddy1",
        )

        buddy2 = BuddyMeshNetwork(
            buddy_id="buddy-002",
            buddy_name="Pixel",
            data_dir=Path(temp_dir) / "buddy2",
        )

        # Start networks
        buddy1.start()
        buddy2.start()

        # Add each other as peers
        peer1 = BuddyPeer(
            peer_id="buddy-001",
            name="Nova",
            address="127.0.0.1",
            port=8001,
        )
        peer2 = BuddyPeer(
            peer_id="buddy-002",
            name="Pixel",
            address="127.0.0.1",
            port=8002,
        )

        buddy1.add_peer(peer2)
        buddy2.add_peer(peer1)

        # Create and send a message
        message = buddy1.create_message(
            recipient_id="buddy-002",
            message_type="greeting",
            payload={"text": "Hello from Nova!"},
        )

        print(f"📤 Sending message: {message.payload}")
        buddy1.send_message(message)

        # Get stats
        print(f"\n📊 Buddy 1 Stats: {buddy1.get_network_stats()}")
        print(f"📊 Buddy 2 Stats: {buddy2.get_network_stats()}")

        # Cleanup
        buddy1.stop()
        buddy2.stop()
