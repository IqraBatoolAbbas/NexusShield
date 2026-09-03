"""Request models shared by the API route modules."""

from pydantic import BaseModel, Field


class Credentials(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(default="Security Admin", min_length=2, max_length=120)
    role: str = Field(default="admin", pattern="^(admin|developer|auditor)$")


class RoleUpdate(BaseModel):
    role: str = Field(pattern="^(admin|developer|auditor)$")


class TeamInvite(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    role: str = Field(pattern="^(admin|developer|auditor)$")


class ScanRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=10000)
    session_id: str = "default-session"
    client_id: str = "dashboard-user"


class FeedbackRequest(BaseModel):
    event_id: str
    verdict: str = Field(pattern="^(safe|attack|false_positive|confirmed_attack)$")


class PolicyUpdate(BaseModel):
    similarity_threshold: float = Field(ge=0.5, le=0.99)
    enable_honeypot: bool
    strict_pii: bool
    strict_toxicity: bool
    auto_block_dos: bool


class KeyRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
