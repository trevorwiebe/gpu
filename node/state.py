"""
Shared global state for the LLM Node Server
"""
import uuid

# Node ID - generated once at startup
node_id = str(uuid.uuid4())
