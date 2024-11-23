import logging

import main
from models import RunnerEvent
import math

logger = logging.getLogger('uvicorn.error')


def get_distance(p0, q0):
    x0 = (p0[0] - q0[0]) ** 2
    x1 = (p0[1] - q0[1]) ** 2
    return math.sqrt(x0 + x1)

# Assign the closest customer to each taxi
def baseline_assign_vehicle_to_customer():

    if not main.vehicles or not main.customers:
        return
    for vehicle in main.vehicles:
        # can be improved by considering full vehicle list
        if vehicle.get('isAvailable'):

            min_distance = float('inf')
            min_customer = None

            # Find the closest customer
            for customer in main.customers:
                if customer.get('awaitingService'):
                    distance = get_distance((vehicle.get('coordX'), vehicle.get('coordY')), (customer.get('coordX'), customer.get('coordY')))
                    if distance < min_distance:
                        min_distance = distance
                        min_customer = customer

            vehicle['customerId'] = min_customer.get('id')
            vehicle['isAvailable'] =  False
            min_customer['awaitingService'] = False
            main.runner_events.append(RunnerEvent(vehicleId=vehicle.get('id'), customerId=min_customer.get('id')))
            logger.info(f"Taxi {vehicle.get('id')} picked customer {min_customer.get('id')}")
