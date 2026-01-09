import os
import sys
import contextlib
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

# Import PhoneAgent components
# We assume the parent directory is installed as a package or available in path
from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig
from phone_agent.device_factory import DeviceType, get_device_factory, set_device_type
from phone_agent.model import ModelConfig

# Initialize FastMCP server
mcp = FastMCP("phone-agent")

@contextlib.contextmanager
def redirect_stdout_to_stderr():
    """Redirect stdout to stderr to prevent breaking JSON-RPC protocol."""
    old_stdout = sys.stdout
    sys.stdout = sys.stderr
    try:
        yield
    finally:
        sys.stdout = old_stdout

def get_agent(device_type: str = "adb", device_id: Optional[str] = None) -> PhoneAgent:
    """Helper to initialize the agent based on configuration."""
    
    # Environment variables for configuration
    base_url = os.getenv("PHONE_AGENT_BASE_URL", "http://localhost:8000/v1")
    model_name = os.getenv("PHONE_AGENT_MODEL", "autoglm-phone-9b")
    api_key = os.getenv("PHONE_AGENT_API_KEY", "EMPTY")
    max_steps = int(os.getenv("PHONE_AGENT_MAX_STEPS", "100"))
    lang = os.getenv("PHONE_AGENT_LANG", "cn")
    
    # Use env var if device_id arg is not provided
    if device_id is None:
        device_id = os.getenv("PHONE_AGENT_DEVICE_ID")
    
    # Set device type globally
    dtype = DeviceType.ADB
    if device_type.lower() == "hdc":
        dtype = DeviceType.HDC
    elif device_type.lower() == "ios":
        dtype = DeviceType.IOS
    
    if dtype != DeviceType.IOS:
        set_device_type(dtype)

    # Create configs
    model_config = ModelConfig(
        base_url=base_url,
        model_name=model_name,
        api_key=api_key,
        lang=lang,
    )

    agent_config = AgentConfig(
        max_steps=max_steps,
        device_id=device_id,
        verbose=True,
        lang=lang,
    )
    return PhoneAgent(model_config=model_config, agent_config=agent_config)

@mcp.tool()
def run_task(task: str, device_id: Optional[str] = None) -> str:
    """
    Run a natural language task on the phone.
    
    Args:
        task: The task description (e.g., "Open Settings and turn on WiFi")
        device_id: Optional specific device ID to control. If not provided, uses the default device.
    """
    with redirect_stdout_to_stderr():
        try:
            # Initialize agent
            agent = get_agent("adb", device_id)
            
            # Run task
            result = agent.run(task)
            
            # Format output
            # PhoneAgent.run returns True/False or some result object depending on implementation
            # We want to provide a clear summary
            if result:
                return f"Task completed successfully.\nResult: {result}"
            else:
                return "Task execution finished (check output for details)."
                
        except Exception as e:
            # Enhanced error handling
            error_msg = str(e)
            if "device not found" in error_msg.lower():
                return f"Error: Device not found. Please check ADB connection or device ID.\nDetails: {error_msg}"
            elif "model" in error_msg.lower():
                return f"Error: Model communication failed. Please check API key and Base URL.\nDetails: {error_msg}"
            else:
                return f"Error executing task: {error_msg}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
