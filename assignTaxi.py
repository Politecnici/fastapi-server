from models import Customer, Vehicle, Scenario, ScenarioParameters, Event
import math

def get_distance(p0, q0):
    x0 = (p0[0] - q0[0]) ** 2
    x1 = (p0[1] - q0[1]) ** 2
    return math.sqrt(x0 + x1)

# Assign the closest customer to each taxi
def baseline_assign_vehicle_to_customer(vehicles, customers, events):

    
    if not vehicles or not customers:
        return
    
    for vehicle in vehicles:

        print("Vehicle: ", vehicle.id, vehicle.isAvailable)

        # can be improved by considering full vehicle list
        if vehicles.isAvailable:

            min_distance = float('inf')
            min_customer = None

            # Find the closest customer
            for customer in customers:
                if customer.awaitingService:
                    
                    distance = get_distance((vehicle.coordX, vehicle.coordY), (customer.coordX, customer.coordY))
                    if distance < min_distance:
                        min_distance = distance
                        min_customer = customer

            vehicle.customerId = min_customer.id
            vehicle.isAvailable = False
            customer.awaitingService = False

            events.append(Event(vehicleId=vehicle.id, customerId=min_customer.id, eventType='pickup', eta=(min_distance * math.pow(10, 5))/vehicle.vehicleSpeed))


        
        