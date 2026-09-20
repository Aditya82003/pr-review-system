from pydantic import BaseModel

class RawFinding(BaseModel):
    file:str
    line:int | None = None
    text:str
    evidence_tool_call_id:str
    
class RawReview(BaseModel):
    findings:list[RawFinding]=[]