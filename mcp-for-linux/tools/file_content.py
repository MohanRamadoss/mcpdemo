import os

def register(mcp):
    @mcp.tool()
    def view_file(path: str, lines: int = 20) -> dict:
        """View the first or last N lines of a file."""
        if not os.path.exists(path):
            return {"error": f"File not found: {path}"}
        try:
            with open(path, 'r') as f:
                all_lines = f.readlines()
            return {
                "path": path,
                "total_lines": len(all_lines),
                "head": all_lines[:lines],
                "tail": all_lines[-lines:]
            }
        except Exception as e:
            return {"error": str(e)}
