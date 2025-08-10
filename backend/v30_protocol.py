"""
CryptoMiner Enterprise V30 - Custom Node Communication Protocol
High-performance binary protocol for distributed mining coordination
"""

import asyncio
import json
import struct
import time
import zlib
import hashlib
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import IntEnum
from dataclasses import dataclass, asdict
import socket

logger = logging.getLogger(__name__)

class MessageType(IntEnum):
    """Protocol message types"""
    # Node Registration
    NODE_REGISTER = 0x01
    NODE_REGISTER_ACK = 0x02
    NODE_HEARTBEAT = 0x03
    NODE_HEARTBEAT_ACK = 0x04
    NODE_DISCONNECT = 0x05
    
    # Mining Coordination
    WORK_REQUEST = 0x10
    WORK_ASSIGNMENT = 0x11
    WORK_COMPLETE = 0x12
    WORK_RESULT = 0x13
    MINING_START = 0x14
    MINING_STOP = 0x15
    
    # Statistics & Monitoring
    STATS_REQUEST = 0x20
    STATS_RESPONSE = 0x21
    PERFORMANCE_UPDATE = 0x22
    SYSTEM_STATUS = 0x23
    
    # Control Commands
    CONFIG_UPDATE = 0x30
    CONTROL_COMMAND = 0x31
    LICENSE_VALIDATE = 0x32
    LICENSE_RESPONSE = 0x33
    
    # Error Handling
    ERROR = 0xE0
    UNKNOWN = 0xE1

@dataclass
class NodeInfo:
    node_id: str
    hostname: str
    ip_address: str
    port: int
    license_key: str
    capabilities: Dict[str, Any]
    system_specs: Dict[str, Any]
    connected_time: float
    last_heartbeat: float
    status: str = "connected"

@dataclass
class MiningWork:
    work_id: str
    coin_config: Dict[str, Any]
    wallet_address: str
    start_nonce: int
    nonce_range: int
    difficulty_target: str
    timestamp: float
    assigned_node: Optional[str] = None

@dataclass 
class WorkResult:
    work_id: str
    node_id: str
    found_nonce: Optional[int]
    hash_result: Optional[str]
    hashes_computed: int
    processing_time: float
    success: bool
    shares_found: int = 0

class V30Protocol:
    """Custom high-performance protocol for V30 distributed mining"""
    
    MAGIC_BYTES = b'\x43\x4D\x50\x33'  # CMP3 (CryptoMiner Pro V30)
    VERSION = 1
    HEADER_SIZE = 16
    MAX_PAYLOAD_SIZE = 1024 * 1024  # 1MB max payload
    
    @classmethod
    def create_message(cls, msg_type: MessageType, data: Dict[str, Any], 
                      node_id: str = "", compress: bool = True) -> bytes:
        """Create a protocol message"""
        try:
            # Serialize payload
            json_data = json.dumps(data, separators=(',', ':'))
            payload = json_data.encode('utf-8')
            
            # Compress if enabled and payload is large
            compressed = False
            if compress and len(payload) > 256:
                compressed_payload = zlib.compress(payload, level=6)
                if len(compressed_payload) < len(payload):
                    payload = compressed_payload
                    compressed = True
            
            # Calculate payload hash
            payload_hash = hashlib.sha256(payload).digest()[:4]  # First 4 bytes
            
            # Create header
            flags = 0x01 if compressed else 0x00
            header = struct.pack(
                '<4s B B H I 4s',
                cls.MAGIC_BYTES,      # Magic bytes (4)
                cls.VERSION,          # Version (1)
                msg_type,             # Message type (1)
                flags,                # Flags (2)
                len(payload),         # Payload length (4)
                payload_hash          # Payload hash (4)
            )
            
            return header + payload
            
        except Exception as e:
            logger.error(f"Failed to create message: {e}")
            return cls.create_error_message(f"Message creation failed: {e}")
    
    @classmethod
    def parse_message(cls, data: bytes) -> Tuple[Optional[MessageType], Optional[Dict], str]:
        """Parse a protocol message"""
        try:
            if len(data) < cls.HEADER_SIZE:
                return None, None, "Incomplete header"
            
            # Parse header
            header = struct.unpack('<4s B B H I 4s', data[:cls.HEADER_SIZE])
            magic, version, msg_type, flags, payload_len, payload_hash = header
            
            # Validate magic bytes and version
            if magic != cls.MAGIC_BYTES:
                return None, None, "Invalid magic bytes"
            
            if version != cls.VERSION:
                return None, None, f"Unsupported version: {version}"
            
            # Check if we have complete message
            total_len = cls.HEADER_SIZE + payload_len
            if len(data) < total_len:
                return None, None, "Incomplete payload"
            
            # Extract payload
            payload = data[cls.HEADER_SIZE:total_len]
            
            # Verify payload hash
            calculated_hash = hashlib.sha256(payload).digest()[:4]
            if calculated_hash != payload_hash:
                return None, None, "Payload hash mismatch"
            
            # Decompress if needed
            if flags & 0x01:  # Compressed flag
                try:
                    payload = zlib.decompress(payload)
                except Exception as e:
                    return None, None, f"Decompression failed: {e}"
            
            # Parse JSON payload
            try:
                json_data = json.loads(payload.decode('utf-8'))
                return MessageType(msg_type), json_data, ""
            except json.JSONDecodeError as e:
                return None, None, f"JSON parse error: {e}"
                
        except struct.error as e:
            return None, None, f"Header parse error: {e}"
        except Exception as e:
            return None, None, f"Parse error: {e}"
    
    @classmethod
    def create_error_message(cls, error_msg: str) -> bytes:
        """Create an error message"""
        return cls.create_message(MessageType.ERROR, {"error": error_msg}, compress=False)

class NodeManager:
    """Manages connected mining nodes"""
    
    def __init__(self):
        self.nodes: Dict[str, NodeInfo] = {}
        self.work_queue: List[MiningWork] = []
        self.active_work: Dict[str, MiningWork] = {}
        self.completed_work: List[WorkResult] = []
        self.stats_lock = asyncio.Lock()
        
    def register_node(self, node_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Register a new mining node"""
        try:
            node_id = node_data.get("node_id")
            if not node_id:
                return False, "Node ID required"
            
            # Create node info
            node_info = NodeInfo(
                node_id=node_id,
                hostname=node_data.get("hostname", "unknown"),
                ip_address=node_data.get("ip_address", "0.0.0.0"),
                port=node_data.get("port", 0),
                license_key=node_data.get("license_key", ""),
                capabilities=node_data.get("capabilities", {}),
                system_specs=node_data.get("system_specs", {}),
                connected_time=time.time(),
                last_heartbeat=time.time()
            )
            
            self.nodes[node_id] = node_info
            logger.info(f"✅ Node registered: {node_id} ({node_info.hostname})")
            
            return True, "Node registered successfully"
            
        except Exception as e:
            logger.error(f"Node registration failed: {e}")
            return False, str(e)
    
    def update_heartbeat(self, node_id: str) -> bool:
        """Update node heartbeat"""
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = time.time()
            return True
        return False
    
    def disconnect_node(self, node_id: str) -> bool:
        """Disconnect a mining node"""
        if node_id in self.nodes:
            self.nodes[node_id].status = "disconnected"
            # Reassign any active work from this node
            self._reassign_work_from_node(node_id)
            logger.info(f"🔌 Node disconnected: {node_id}")
            return True
        return False
    
    def get_node_stats(self) -> Dict[str, Any]:
        """Get aggregate node statistics"""
        total_nodes = len(self.nodes)
        active_nodes = len([n for n in self.nodes.values() if n.status == "connected"])
        
        # Aggregate capabilities
        total_cpu_cores = 0
        total_gpus = 0
        total_ram_gb = 0
        
        for node in self.nodes.values():
            if node.status == "connected":
                specs = node.system_specs
                total_cpu_cores += specs.get("cpu_cores", 0)
                total_gpus += specs.get("total_gpus", 0)
                total_ram_gb += specs.get("ram_gb", 0)
        
        return {
            "total_nodes": total_nodes,
            "active_nodes": active_nodes,
            "inactive_nodes": total_nodes - active_nodes,
            "aggregate_stats": {
                "total_cpu_cores": total_cpu_cores,
                "total_gpus": total_gpus,
                "total_ram_gb": total_ram_gb
            },
            "work_stats": {
                "queued_work": len(self.work_queue),
                "active_work": len(self.active_work),
                "completed_work": len(self.completed_work)
            }
        }
    
    def create_mining_work(self, coin_config: Dict, wallet_address: str, 
                          total_nonce_space: int = 10000000) -> List[MiningWork]:
        """Create work assignments for distributed mining"""
        work_assignments = []
        active_nodes = [n for n in self.nodes.values() if n.status == "connected"]
        
        if not active_nodes:
            return work_assignments
        
        # Calculate work distribution based on node capabilities
        nonce_per_node = total_nonce_space // len(active_nodes)
        current_nonce = 0
        
        for i, node in enumerate(active_nodes):
            # Adjust work size based on node capabilities
            node_cores = node.system_specs.get("cpu_cores", 1)
            node_gpus = node.system_specs.get("total_gpus", 0)
            
            # Scale work based on processing power
            scale_factor = max(1.0, (node_cores / 4) + (node_gpus * 2))
            adjusted_nonce_range = int(nonce_per_node * scale_factor)
            
            work = MiningWork(
                work_id=f"work_{int(time.time())}_{i}",
                coin_config=coin_config,
                wallet_address=wallet_address,
                start_nonce=current_nonce,
                nonce_range=adjusted_nonce_range,
                difficulty_target="00000000",  # Simplified
                timestamp=time.time(),
                assigned_node=node.node_id
            )
            
            work_assignments.append(work)
            self.work_queue.append(work)
            current_nonce += adjusted_nonce_range
        
        logger.info(f"📋 Created {len(work_assignments)} work assignments for {len(active_nodes)} nodes")
        return work_assignments
    
    def _reassign_work_from_node(self, node_id: str):
        """Reassign work from disconnected node"""
        work_to_reassign = []
        
        # Find work assigned to this node
        for work_id, work in self.active_work.items():
            if work.assigned_node == node_id:
                work_to_reassign.append(work_id)
        
        # Move back to queue for reassignment
        for work_id in work_to_reassign:
            work = self.active_work.pop(work_id)
            work.assigned_node = None
            self.work_queue.append(work)
        
        if work_to_reassign:
            logger.info(f"♻️  Reassigned {len(work_to_reassign)} work items from node {node_id}")

class DistributedMiningServer:
    """Central server for distributed mining coordination"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 9001):
        self.host = host
        self.port = port
        self.server = None
        self.node_manager = NodeManager()
        self.license_system = None  # Will be injected
        self.is_running = False
        
    async def start_server(self):
        """Start the distributed mining server"""
        try:
            self.server = await asyncio.start_server(
                self.handle_client,
                self.host,
                self.port
            )
            
            self.is_running = True
            addr = self.server.sockets[0].getsockname()
            logger.info(f"🚀 V30 Distributed Mining Server started on {addr[0]}:{addr[1]}")
            
            async with self.server:
                await self.server.serve_forever()
                
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            self.is_running = False
    
    async def stop_server(self):
        """Stop the distributed mining server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            self.is_running = False
            logger.info("🛑 Distributed mining server stopped")
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle client connection"""
        client_addr = writer.get_extra_info('peername')
        logger.info(f"🔗 New connection from {client_addr}")
        
        try:
            while True:
                # Read message header
                header_data = await reader.readexactly(V30Protocol.HEADER_SIZE)
                if not header_data:
                    break
                
                # Parse header to get payload length
                _, _, _, _, payload_len, _ = struct.unpack('<4s B B H I 4s', header_data)
                
                # Read payload
                payload_data = await reader.readexactly(payload_len)
                
                # Parse complete message
                msg_type, data, error = V30Protocol.parse_message(header_data + payload_data)
                
                if error:
                    logger.error(f"Protocol error from {client_addr}: {error}")
                    response = V30Protocol.create_error_message(error)
                    writer.write(response)
                    await writer.drain()
                    continue
                
                # Handle message
                response = await self.process_message(msg_type, data, client_addr)
                if response:
                    writer.write(response)
                    await writer.drain()
                
        except asyncio.IncompleteReadError:
            logger.info(f"🔌 Client {client_addr} disconnected")
        except Exception as e:
            logger.error(f"Error handling client {client_addr}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def process_message(self, msg_type: MessageType, data: Dict, 
                            client_addr: Tuple[str, int]) -> Optional[bytes]:
        """Process incoming protocol message"""
        try:
            if msg_type == MessageType.NODE_REGISTER:
                return await self._handle_node_register(data, client_addr)
            
            elif msg_type == MessageType.NODE_HEARTBEAT:
                return await self._handle_heartbeat(data)
            
            elif msg_type == MessageType.WORK_REQUEST:
                return await self._handle_work_request(data)
            
            elif msg_type == MessageType.WORK_RESULT:
                return await self._handle_work_result(data)
            
            elif msg_type == MessageType.STATS_REQUEST:
                return await self._handle_stats_request(data)
            
            elif msg_type == MessageType.LICENSE_VALIDATE:
                return await self._handle_license_validate(data)
            
            else:
                logger.warning(f"Unknown message type: {msg_type}")
                return V30Protocol.create_error_message(f"Unknown message type: {msg_type}")
                
        except Exception as e:
            logger.error(f"Error processing message {msg_type}: {e}")
            return V30Protocol.create_error_message(str(e))
    
    async def _handle_node_register(self, data: Dict, client_addr: Tuple[str, int]) -> bytes:
        """Handle node registration"""
        # Add client IP to node data
        data["ip_address"] = client_addr[0]
        
        # Validate license if provided
        license_key = data.get("license_key")
        if license_key and self.license_system:
            validation = self.license_system.validate_license(license_key)
            if not validation["valid"]:
                return V30Protocol.create_message(
                    MessageType.NODE_REGISTER_ACK,
                    {"success": False, "error": f"Invalid license: {validation['error']}"}
                )
        
        # Register node
        success, message = self.node_manager.register_node(data)
        
        response_data = {
            "success": success,
            "message": message,
            "server_info": {
                "version": "v30",
                "protocol_version": V30Protocol.VERSION,
                "capabilities": ["distributed_mining", "gpu_support", "load_balancing"]
            }
        }
        
        return V30Protocol.create_message(MessageType.NODE_REGISTER_ACK, response_data)
    
    async def _handle_heartbeat(self, data: Dict) -> bytes:
        """Handle node heartbeat"""
        node_id = data.get("node_id")
        if node_id and self.node_manager.update_heartbeat(node_id):
            return V30Protocol.create_message(
                MessageType.NODE_HEARTBEAT_ACK,
                {"success": True, "timestamp": time.time()}
            )
        else:
            return V30Protocol.create_error_message("Node not found")
    
    async def _handle_work_request(self, data: Dict) -> bytes:
        """Handle work request from node"""
        node_id = data.get("node_id")
        
        if not node_id or node_id not in self.node_manager.nodes:
            return V30Protocol.create_error_message("Invalid node ID")
        
        # Find available work
        if self.node_manager.work_queue:
            work = self.node_manager.work_queue.pop(0)
            work.assigned_node = node_id
            self.node_manager.active_work[work.work_id] = work
            
            return V30Protocol.create_message(
                MessageType.WORK_ASSIGNMENT,
                asdict(work)
            )
        else:
            return V30Protocol.create_message(
                MessageType.WORK_ASSIGNMENT,
                {"no_work": True, "message": "No work available"}
            )
    
    async def _handle_work_result(self, data: Dict) -> bytes:
        """Handle work result from node"""
        try:
            work_result = WorkResult(**data)
            self.node_manager.completed_work.append(work_result)
            
            # Remove from active work
            if work_result.work_id in self.node_manager.active_work:
                del self.node_manager.active_work[work_result.work_id]
            
            logger.info(f"📊 Work result received: {work_result.work_id} from {work_result.node_id}")
            
            return V30Protocol.create_message(
                MessageType.WORK_COMPLETE,
                {"success": True, "work_id": work_result.work_id}
            )
            
        except Exception as e:
            return V30Protocol.create_error_message(f"Invalid work result: {e}")
    
    async def _handle_stats_request(self, data: Dict) -> bytes:
        """Handle statistics request"""
        stats = self.node_manager.get_node_stats()
        return V30Protocol.create_message(MessageType.STATS_RESPONSE, stats)
    
    async def _handle_license_validate(self, data: Dict) -> bytes:
        """Handle license validation request"""
        license_key = data.get("license_key")
        
        if not license_key or not self.license_system:
            return V30Protocol.create_message(
                MessageType.LICENSE_RESPONSE,
                {"valid": False, "error": "No license system available"}
            )
        
        validation = self.license_system.validate_license(license_key)
        return V30Protocol.create_message(MessageType.LICENSE_RESPONSE, validation)

# Test the protocol when run directly
if __name__ == "__main__":
    import asyncio
    
    print("🌐 Testing V30 Protocol...")
    
    # Test message creation and parsing
    test_data = {
        "node_id": "test_node_001",
        "hostname": "mining-rig-01",
        "capabilities": {
            "cpu_cores": 32,
            "gpus": 4,
            "ram_gb": 128
        }
    }
    
    # Create message
    message = V30Protocol.create_message(MessageType.NODE_REGISTER, test_data)
    print(f"✅ Created message: {len(message)} bytes")
    
    # Parse message
    msg_type, parsed_data, error = V30Protocol.parse_message(message)
    
    if error:
        print(f"❌ Parse error: {error}")
    else:
        print(f"✅ Parsed message type: {msg_type}")
        print(f"✅ Data integrity check: {parsed_data == test_data}")
    
    # Test node manager
    node_manager = NodeManager()
    success, msg = node_manager.register_node(test_data)
    print(f"✅ Node registration: {success} - {msg}")
    
    stats = node_manager.get_node_stats()
    print(f"✅ Node stats: {stats['active_nodes']} active nodes")
    
    print("\n🎉 V30 Protocol test completed successfully!")