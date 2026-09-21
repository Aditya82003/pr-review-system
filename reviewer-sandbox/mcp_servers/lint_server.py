import subprocess
from pathlib import Path
from mcp.server.fastmcp import  FastMCP

mcp = FastMCP("lint-server")
REPO="/workspace/repo"

# def _detect_language(file_path:str)->str:
#     suffix = Path(file_path).suffix.lower()
#     mapping = {
#         ".py": "python",
#         ".js": "javascript",
#         ".jsx": "javascript",
#         ".ts": "typescript",
#         ".tsx": "typescript",
#     }
#     return mapping.get(suffix)
    
# def _get_command(language: str, file_path: str)->list[str] | None:
#     if language == "python":
#         return ["ruff","check",file_path,"--output-format=json"]
#     if language in ("javascript", "typescript"):
#         return ["npx","eslint",file_path,"--format=json"]
    # return None
    
@mcp.tool()
def run_lint(file_path: str,changed_files: list[str])->dict:
    """Run the linter against a single file in the PR checkout and return
    any issues it reports, verbatim."""
    result=subprocess.run(
        ["ruff","check",file_path,"--output-format=json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10
    )
    
    return result.stdout.strip() or "no issues found"
    
    # for file in changed_files:
    #     language = _detect_language(file)
        
    #     if language is None:
    #         results.append({
    #             "file": file,
    #             "status": "skipped",
    #             "reason": "Unsupported file type",
    #         })
    #         continue
            
    #     command = _get_command(language,file_path)
        
    #     if command is None:
    #         continue
            
    #     try:
    #         completed=subprocess.run(
    #             command,
    #             cwd=REPO,
    #             capture_output=True,
    #             text=True
    #             )
    #         results.append({
    #             "file": file,
    #             "language": language,
    #             "return_code": completed.returncode,
    #             "stdout": completed.stdout.strip(),
    #             "stderr": completed.stderr.strip(),
    #         })
    #     except subprocess.TimeoutExpired :
    #         results.append({
    #             "file": file,
    #             "language": language,
    #             "status": "timeout",
    #         })
    #     except Exception as e:
    #         results.append({
    #             "file": file,
    #             "language": language,
    #             "status": "error",
    #             "error": str(e),
    #         })
    
    # return {
    #     "results": results
    # }
    

if __name__=="__main__":
    mcp.run(transport="stdio")