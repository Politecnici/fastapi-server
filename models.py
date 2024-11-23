from pydantic import BaseModel
from typing import List

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