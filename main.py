import logging
from contextlib import asynccontextmanager
from typing import List
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from requests import request

vehicles = []

customers = []
app = FastAPI()

logger = logging.getLogger('uvicorn.error')


class Customer(BaseModel):
    id: str
    coordX: int
    coordY: int
    destinationX: int
    destinationY: int
    awaitingService: bool

class Vehicle(BaseModel):
    id: str
    coordX: int
    coordY: int
    activeTime: int
    distanceTravelled: int
    numberOfTrips: int
    remainingTravelTime: int
    vehicleSpeed: int
    isAvailable: bool

class Scenario(BaseModel):
    id: str
    startTime: str
    endTime: str
    status: str
    vehicles: List[Vehicle]
    customers: List[Customer]
    
class ScenarioParameters(BaseModel):
    vehicles: int
    customers: int


@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>RoboTaxi Middleware</title>
        </head>
        <body>
            <h1 style="color: green">System is running 😃</h1>
        </body>
    </html>
    """


STREAM_DELAY = 1  # second
RETRY_TIMEOUT = 15000  # milisecond

@app.get('/events')
async def message_stream(request: Request):
    def new_messages():
        
        yield 'Hello World'
    async def event_generator():
        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break

            # Checks for new messages and return them to client if any
            if new_messages():
                yield {
                        "event": "new_message",
                        "id": "message_id",
                        "retry": RETRY_TIMEOUT,
                        "data": "message_content"
                }

            await asyncio.sleep(STREAM_DELAY)

    return EventSourceResponse(event_generator())

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(main_loop())

async def main_loop():
    while True:
        logger.info("kek")

@app.post("/scenario/start")
def read_item(scenario_parameters: ScenarioParameters):
    scenario_response = request("POST", f"http://localhost:8080/scenario/create?numberOfVehicles={scenario_parameters.vehicles}&numberOfCustomers={scenario_parameters.customers}")
    if scenario_response.status_code == 200:
        runner_response = request("POST", "http://localhost:8090/Scenarios/initialize_scenario", json=scenario_response.json())
        print(runner_response)
        if runner_response.status_code==200:
            return scenario_response.json()
        else: 
            raise HTTPException(status_code=400, detail="Cannot initialize scenario")
    else:
        raise HTTPException(status_code=400, detail="Cannot create scenario")
