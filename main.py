import json
from contextlib import asynccontextmanager
import asyncio

import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from requests import request
import logging

from sse_starlette import EventSourceResponse

from assign_taxi import baseline_assign_vehicle_to_customer
from models import ScenarioParameters, SseEvents

runner_events = []

sse_events = []

vehicles = []

customers = []

scenario_id = ""

past_scenarios = set()

speed = 1

logger = logging.getLogger('uvicorn.error')


async def main_loop():
    global vehicles, customers, runner_events
    while True:
        logger.debug("ping")
        logger.debug(f"Vehicles {vehicles}")
        logger.debug(f"Customers {customers}")
        logger.debug(f"runner_events {runner_events}")
        baseline_assign_vehicle_to_customer()
        handle_runner_events()
        confirm_runner_termination()
        await asyncio.sleep(0.2)


def confirm_runner_termination():
    global customers, vehicles, scenario_id
    if not customers and vehicles and scenario_id not in past_scenarios:
        sse_events.append(SseEvents(vehicle={}, event_type="finish"))
        past_scenarios.add(scenario_id)
        print("Scenario finished")


def dropoff(vehicle, vehicle_id, customer_coordX, customer_coordY):
    global sse_events
    sse_events.append(SseEvents(vehicle=vehicle, event_type="dropoff"))
    if vehicle.get('id') == vehicle_id:
        vehicle['isAvailable'] = True
        vehicle['customerId'] = None
        vehicle['coordX'] = customer_coordX
        vehicle['coordY'] = customer_coordY


async def finished_trip(vehicle_id, customer_id, delay):
    global customers, runner_events, vehicles, speed
    await asyncio.sleep(delay / speed)
    customer_coordX = 0
    customer_coordY = 0
    for index, customer in enumerate(customers):
        if customer.get('id') == customer_id:
            customer_coordX = customer.get('destinationX')
            customer_coordY = customer.get('destinationY')
            customers.pop(index)
    logger.info(f"Customer {customer_id} has been dropped off")
    map(lambda vehicle: dropoff(vehicle, vehicle_id, customer_coordX, customer_coordY), vehicles)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(main_loop())
    yield
    print('Shutting down...')


app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


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


def handle_runner_events():
    global runner_events, vehicles, sse_events
    if runner_events:
        temp_vehicles_list = []
        for event in runner_events:
            temp_vehicles_list.append({"id": event.vehicleId, "customerId": event.customerId})
        update_scenario_response = request("PUT", f"http://localhost:8090/Scenarios/update_scenario/{scenario_id}",
                                           json={"vehicles": temp_vehicles_list})
        for updated_vehicle in update_scenario_response.json()['updatedVehicles']:
            for vehicle in vehicles:
                if vehicle['id'] == updated_vehicle['id']:
                    vehicle = updated_vehicle
                    vehicle['isAvailable'] = False
                    logger.info(f"Taxi {vehicle['id']} will drive for {vehicle['remainingTravelTime']}")
                    sse_events.append(SseEvents(vehicle=vehicle, event_type="pickup"))
                    asyncio.create_task(
                        finished_trip(vehicle['id'], updated_vehicle['customerId'], vehicle['remainingTravelTime']))


@app.get('/stream')
async def message_stream(request: Request):
    global sse_events
    def new_messages():
        yield sse_events
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            if new_messages():
                temp_sse_events = []
                for sse_event in sse_events:
                    temp_sse_events.append({"vehicle": sse_event.vehicle, "event_type": sse_event.event_type})
                yield {
                    "events": sse_events
                }
            await asyncio.sleep(1)
    return EventSourceResponse(event_generator())


@app.post("/scenario/start")
def read_item(scenario_parameters: ScenarioParameters):
    global vehicles, customers, runner_events, scenario_id, speed
    scenario_response = request("POST",
                                f"http://localhost:8080/scenario/create?numberOfVehicles={scenario_parameters.vehicles}&numberOfCustomers={scenario_parameters.customers}")
    if scenario_response.status_code == 200:
        runner_response = request("POST", "http://localhost:8090/Scenarios/initialize_scenario",
                                  json=scenario_response.json())
        if runner_response.status_code == 200:
            launch_response = request("POST",
                                      f"http://localhost:8090/Runner/launch_scenario/{runner_response.json()["scenario"]["id"]}?speed={scenario_parameters.speed}")
            if launch_response.status_code == 200:
                vehicles = scenario_response.json()["vehicles"]
                customers = scenario_response.json()["customers"]
                speed = scenario_parameters.speed
                scenario_id = scenario_response.json()["id"]
                return scenario_response.json()
            else:
                raise HTTPException(status_code=400, detail="Cannot launch scenario")
        else:
            raise HTTPException(status_code=400, detail="Cannot initialize scenario")
    else:
        raise HTTPException(status_code=400, detail="Cannot create scenario")
