from pydantic import BaseModel

class RunnerEvent(BaseModel):
    vehicleId: str
    customerId: str


class SseEvents(BaseModel):
    vehicle: dict
    event_type: str

class ScenarioParameters(BaseModel):
    vehicles: int
    customers: int
    speed: int