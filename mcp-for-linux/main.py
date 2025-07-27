from mcp.server.fastmcp import FastMCP
import sys
import os
import glob
import importlib.util
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    "Linux Debug Agent",
    description="A comprehensive Linux system administration and monitoring agent",
    version="2.0.0"
)

def load_modules_from_folder(folder_path: str):
    """Dynamically load MCP tools and resources from a folder."""
    logger.info(f"Loading modules from: {folder_path}")
    for file_path in glob.glob(os.path.join(folder_path, "*.py")):
        if file_path.endswith("__init__.py"):
            continue
        
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "register"):
                logger.info(f"Registering module: {module_name}")
                module.register(mcp)
            else:
                logger.warning(f"Module {module_name} has no register function.")

if __name__ == "__main__":
    logger.info("Starting Linux Debug Agent MCP Server...")
    
    # Load all tools and resources
    load_modules_from_folder("tools")
    load_modules_from_folder("resources")
    
    # Run the server
    transport = "stdio"
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        transport = "http"
        logger.info("Server will use HTTP transport on port 8080")
    else:
        logger.info("Server will use STDIO transport for MCP client")
    
    try:
        if transport == "http":
            mcp.run(transport="http", port=8080)
        else:
            mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)