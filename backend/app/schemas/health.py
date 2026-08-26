from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: str
    project_name: str
    environment: str
    database_connected: bool
    version: str = "1.0.0"
