import subprocess
from mcp.server.fastmcp import  FastMCP

mcp = FastMCP("diff-server")
REPO="/workspace/repo"

def _merge_base()->str:
    return subprocess.run(
        ["git","merge-base","origin/HEAD","pr-branch"],
        cwd=REPO,
        capture_output=True,
        text=True
    ).stdout.strip()
    
@mcp.tool()
def get_diff()->str:
    """Return the unified diff between the PR branch and its merge base
    with the repository's default branch."""
    base = _merge_base()
    diff = subprocess.run(
        ["git","diff",base,"pr-branch"],
        cwd=REPO,
        capture_output=True,
        text=True
    ).stdout
    return diff[:2000]

@mcp.tool()
def list_changed_files()->list[str]:
    """List the files change in the PR."""
    base = _merge_base()
    out=subprocess.run(
        ["git","diff","--name-only",base,"pr-branch"],
        cwd=REPO,
        capture_output=True,
        text=True
    ).stdout
    return [line for line in out.splitlines() if line]

@mcp.tool()
def get_file(path:str)->str:
    """Read a file's full contents as it exists on the PR branch."""
    try:
        with open(f"{REPO}/{path}") as f:
            return f.read()[:2000]
    except FileNotFoundError:
        return f"error:{path} not found in checkout"

if __name__=="__main__":
    mcp.run(transport="stdio")