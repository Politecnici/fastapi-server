from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from sse_starlette.sse import EventSourceResponse
from requests import request
import json
import logging

from assignTaxi import baseline_assign_vehicle_to_customer
from models import Customer, Vehicle, Scenario, ScenarioParameters, Event
from runner import main_loop

events = []

vehicles = []

customers = []

logger = logging.getLogger('uvicorn.error')


async def main_loop():
    while True:
        logger.info("ping")
        baseline_assign_vehicle_to_customer(vehicles, customers, events)
        await asyncio.sleep(1)  # Non-blocking sleep for 1 second

def dropoff(vehicle, vehicle_id):
    if vehicle.id == vehicle_id:
        vehicle.isAvailable = True
        vehicle.customerId = None

async def finished_trip(vehicle_id, customer_id, delay):
    await asyncio.sleep(delay)
    customers = [customer for customer in customers if customer.id != customer_id]
    map(lambda vehicle: dropoff(vehicle), vehicles)
    events.append(Event(vehicleId=vehicle_id, customerId=customer_id, eventType='dropoff', eta=0))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run at startup
    asyncio.create_task(main_loop())
    yield
    # Run on shutdown (if required)
    print('Shutting down...')

app = FastAPI(lifespan=lifespan)


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
        yield events
        
    async def event_generator():
        while True:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break

            # Checks for new messages and return them to client if any
            if new_messages():
                for event in events:
                    json.dumps(event)

            await asyncio.sleep(STREAM_DELAY)

    return EventSourceResponse(event_generator())



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
