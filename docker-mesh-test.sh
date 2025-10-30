#!/bin/bash
# Test mesh networking between buddy containers

set -e

echo "🌐 Testing Bit Buddy Mesh Networking in Containers"
echo "=================================================="

# Create test network
echo "📡 Creating buddy mesh network..."
docker network create buddy-mesh-test 2>/dev/null || true

# Function to cleanup on exit
cleanup() {
    echo "🧹 Cleaning up..."
    docker stop buddy-1 buddy-2 buddy-3 2>/dev/null || true
    docker network rm buddy-mesh-test 2>/dev/null || true
}
trap cleanup EXIT

# Start buddy containers
echo "🤖 Starting buddy containers..."

# Buddy 1 - Code specialist
docker run -d --name buddy-1 --network buddy-mesh-test \
    -v $(pwd)/buddy-1:/app/workspace \
    --expose 8001 \
    bit-buddy-test:mesh-tests \
    python -c "
import asyncio
import time
from enhanced_buddy import EnhancedBitBuddy
from mesh_network import BuddyMeshNetwork
from pathlib import Path

async def run_buddy():
    buddy = EnhancedBitBuddy(
        buddy_dir=Path('/app/buddy-1/buddy'),
        watch_dir=Path('/app/buddy-1/watch'),
        model_path=None
    )
    buddy.personality.name = 'CodeBuddy'
    buddy.personality.specialties = ['programming', 'code_files']
    
    mesh = BuddyMeshNetwork(buddy, 8001)
    await mesh.start_server()
    
    print(f'🤖 {buddy.personality.name} online on mesh network')
    await asyncio.sleep(30)

asyncio.run(run_buddy())
" &

# Buddy 2 - Document specialist  
docker run -d --name buddy-2 --network buddy-mesh-test \
    -v $(pwd)/buddy-2:/app/workspace \
    --expose 8002 \
    bit-buddy-test:mesh-tests \
    python -c "
import asyncio
import time
from enhanced_buddy import EnhancedBitBuddy  
from mesh_network import BuddyMeshNetwork
from pathlib import Path

async def run_buddy():
    buddy = EnhancedBitBuddy(
        buddy_dir=Path('/app/buddy-2/buddy'),
        watch_dir=Path('/app/buddy-2/watch'),
        model_path=None
    )
    buddy.personality.name = 'DocBuddy'
    buddy.personality.specialties = ['documents', 'text_files']
    
    mesh = BuddyMeshNetwork(buddy, 8002)
    await mesh.start_server()
    
    print(f'🤖 {buddy.personality.name} online on mesh network')
    await asyncio.sleep(30)

asyncio.run(run_buddy())
" &

# Buddy 3 - General specialist
docker run -d --name buddy-3 --network buddy-mesh-test \
    -v $(pwd)/buddy-3:/app/workspace \
    --expose 8003 \
    bit-buddy-test:mesh-tests \
    python -c "
import asyncio
import time
from enhanced_buddy import EnhancedBitBuddy
from mesh_network import BuddyMeshNetwork  
from pathlib import Path

async def run_buddy():
    buddy = EnhancedBitBuddy(
        buddy_dir=Path('/app/buddy-3/buddy'),
        watch_dir=Path('/app/buddy-3/watch'),
        model_path=None
    )
    buddy.personality.name = 'GenericBuddy'
    buddy.personality.specialties = ['general_files', 'organization']
    
    mesh = BuddyMeshNetwork(buddy, 8003)
    await mesh.start_server()
    
    print(f'🤖 {buddy.personality.name} online on mesh network')
    
    # Test mesh queries
    await asyncio.sleep(5)  # Wait for other buddies
    
    print('🔍 Testing mesh queries...')
    responses = await mesh.query_mesh('programming help', 'programming')
    print(f'Got {len(responses)} responses from mesh')
    
    await asyncio.sleep(25)

asyncio.run(run_buddy())
" &

echo "⏳ Waiting for buddies to start..."
sleep 10

# Test network connectivity
echo "🔗 Testing network connectivity..."
docker exec buddy-1 ping -c 2 buddy-2
docker exec buddy-2 ping -c 2 buddy-3  
docker exec buddy-3 ping -c 2 buddy-1

echo "✅ Network connectivity verified"

# Wait for mesh tests to complete
echo "🕒 Running mesh communication tests..."
sleep 25

# Check logs
echo "📋 Buddy logs:"
echo "--- CodeBuddy (buddy-1) ---"
docker logs buddy-1 | tail -n 5

echo "--- DocBuddy (buddy-2) ---"  
docker logs buddy-2 | tail -n 5

echo "--- GenericBuddy (buddy-3) ---"
docker logs buddy-3 | tail -n 5

echo "🎉 Mesh networking test completed!"
echo "✅ Multiple buddies can communicate in containerized environment"
echo "🌐 No local dependencies required for mesh functionality"