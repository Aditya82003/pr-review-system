import os
import json
import anthropic
from mcp import ClinentSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from schema import RawFinding,RawReview
from contextlib import AsyncExitStack

SERVERS = {
    "diff": StdioServerParameters(command="python", args=["/app/mcp_servers/diff_server.py"]),
    "lint": StdioServerParameters(command="python", args=["/app/mcp_servers/lint_server.py"]),
    "tests": StdioServerParameters(command="python", args=["/app/mcp_servers/test_server.py"]),
}

with open("/app/agent/prompts/review_prompt.md","r") as f:
    SYSTEM_PROMPT = f.read()

MAX_ITERATIONS = 8


async def _connect_all(stack:AsyncExitStack)->dict[str,ClinentSession]:
    sessions={}
    for labels,params in SERVERS.items():
        read,write = await stack.enter_async_context(stdio_client(params))
        session = await stack.enter_async_context(ClinentSession(read,write))
        sessions[labels] = session
        #{"diff":ClinetSession(read,write),"lint":ClinetSession(read,write),"test":ClinentSession(read,write)}
    return sessions

def _to_anthropic_tools(mcp_tools,prefix:str)->list[dict]:
    return [ 
            {
                "name":f"{prefix}_{t.name}",
                "description":t.description or "",
                "parameters":t.parameters
            }
            for t in mcp_tools.tools
        ]
    
async def _run_review()->tuple[list[dict],dict]:
    """Return raw_finding,tool_call_log"""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    model = os.environ.get("REVIEW_MODEL","claude-sonnet-4-6")
    tool_call_log:dict[str,dict] = {}
    
    async with AsyncExitStack() as stack:
        sessions = await _connect_all(stack)
        
        anthropic_tools =[]
        for labels,session in sessions.items():
            lisiting = await session.list_tools()
            anthropic_tools.extend(_to_anthropic_tools(lisiting,labels))
        
        messages=[{
            "role":"user",
            "content":(
                "Review this pull request. Use the available tools to inspect "
                "the diff, run lint, and run tests before making any claim."
            )
        }]
        
        for _ in range(MAX_ITERATIONS):
            resp = client.messages.create(
              model=model,
              max_tokens=4096,
              system=SYSTEM_PROMPT,
              tools=anthropic_tools,
              messages=messages,
            )

            messages.append({
              "role":"assistant",
              "content":resp.content
            })
          
            tool_uses = [b for b in resp.content if b.type == "tool_use"]
            if not tool_uses:
                text_block = next(b for b in resp.content if b.type == "text")
                parsed = RawReview.model_validate(json.loads(text_block.text))
                return [f.model_dump() for f in parsed.findings],tool_call_log

            tool_results=[]
            for call in tool_uses:
                label,tool_name = call.name.split("_",1)
                result = await sessions[label].run_tool(tool_name,call.input)
    