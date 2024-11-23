# import math
# import random

# # taxiPos, customerStartPos are array with distances
# def getDistance(taxiPos, customerStartPos):

#     x0 = (taxiPos[0] - customerStartPos[0]) ** 2
#     x1 = (taxiPos[1] - customerStartPos[1]) ** 2

#     return math.sqrt(x0 + x1)


# GRID_HEIGHT = 100
# GRID_WIDTH = 100

# TAXI_NUMBER = 5
# CUSTOMER_NUMBER = 20

# availableTaxiList = []
# waitingCustomerList = []

# # fill lists with random values inside the grid
# for i in range(TAXI_NUMBER):
#     availableTaxiList.append([random.randint(0, GRID_WIDTH), random.randint(0, GRID_HEIGHT)])

# for i in range(CUSTOMER_NUMBER):
#     waitingCustomerList.append([random.randint(0, GRID_WIDTH), random.randint(0, GRID_HEIGHT)])


# # for all taxis, find the closest customer, assign it and remove it from the list
# # move the taxi to random position in the grid
# # repeat until no customers are left

# # oss: this is a greedy algorithm, it may not be the best solution
# # oss: hypothesis: no travel time

# while len(waitingCustomerList) > 0:
#     for taxi in availableTaxiList:
#         minDistance = 1000000
#         minCustomer = None
#         for customer in waitingCustomerList:
#             distance = getDistance(taxi, customer)
#             if distance < minDistance:
#                 minDistance = distance
#                 minCustomer = customer
#         print("Taxi at", taxi, "assigned to customer at", minCustomer)
#         availableTaxiList.remove(taxi)
#         waitingCustomerList.remove(minCustomer)
#         taxi = [random.randint(0, GRID_WIDTH), random.randint(0, GRID_HEIGHT)]
#         availableTaxiList.append(taxi)
#         print("Taxi moved to", taxi)
#         print("Remaining customers", len(waitingCustomerList))


import math
import random
import matplotlib.pyplot as plt

def get_distance(taxi_pos, customer_start_pos):
    x0 = (taxi_pos[0] - customer_start_pos[0]) ** 2
    x1 = (taxi_pos[1] - customer_start_pos[1]) ** 2
    return math.sqrt(x0 + x1)

GRID_HEIGHT = 100
GRID_WIDTH = 100

TAXI_NUMBER = 5
CUSTOMER_NUMBER = 20

available_taxi_list = []
waiting_customer_list = []

# Fill lists with random values inside the grid
for i in range(TAXI_NUMBER):
    available_taxi_list.append([random.randint(0, GRID_WIDTH), random.randint(0, GRID_HEIGHT)])

for i in range(CUSTOMER_NUMBER):
    waiting_customer_list.append([random.randint(0, GRID_WIDTH), random.randint(0, GRID_HEIGHT)])

# Plot the initial state
def plot_state(taxis, customers, step, assignments=None):
    plt.figure(figsize=(10, 10))
    plt.xlim(0, GRID_WIDTH)
    plt.ylim(0, GRID_HEIGHT)
    
    # Plot taxis
    taxi_x, taxi_y = zip(*taxis)
    plt.scatter(taxi_x, taxi_y, c='blue', marker='s', label='Taxis')
    
    # Plot customers
    if customers:
        customer_x, customer_y = zip(*customers)
        plt.scatter(customer_x, customer_y, c='red', marker='o', label='Customers')
    
    # Plot assignments (arrows from taxis to customers)
    if assignments:
        for taxi, customer, new_taxi_position in assignments:
            # Arrow from taxi to customer (initial assignment)
            plt.arrow(taxi[0], taxi[1], customer[0] - taxi[0], customer[1] - taxi[1], 
                      head_width=1.5, head_length=2, fc='green', ec='green', linestyle='dotted', length_includes_head=True)
            
            # Arrow from customer to new taxi position (different color)
            plt.arrow(customer[0], customer[1], new_taxi_position[0] - customer[0], new_taxi_position[1] - customer[1], 
                      head_width=1.5, head_length=2, fc='orange', ec='orange', linestyle='solid', length_includes_head=True)
    
    plt.title(f"Step {step}: Taxis and Customers")
    plt.legend()
    plt.grid(True)
    plt.savefig(f'step_{step}.png')
    plt.close()

# Simulation loop
step = 0
tripsCounter = 0
totalDistance = 0

while len(waiting_customer_list) > 0:
    assignments = []
    for taxi in available_taxi_list[:]:  # Iterate over a copy of the list
        if len(waiting_customer_list) == 0:
            break
        
        min_distance = float('inf')
        min_customer = None
        tripDistance = 0
        
        # Find the closest customer
        for customer in waiting_customer_list:
            distance = get_distance(taxi, customer)
            if distance < min_distance:
                min_distance = distance
                min_customer = customer
        
        # Assign customer to taxi
        if min_customer:
            print(f"Taxi at {taxi} assigned to customer at {min_customer}")
            waiting_customer_list.remove(min_customer)
            
            # Move taxi to a new random position
            new_taxi_position = [random.randint(0, GRID_WIDTH), random.randint(0, GRID_HEIGHT)]
            assignments.append((taxi, min_customer, new_taxi_position))
            available_taxi_list[available_taxi_list.index(taxi)] = new_taxi_position
            print(f"Taxi moved to {new_taxi_position}")
            print(f"Remaining customers: {len(waiting_customer_list)}")

            # Update total distance
            tripDistance = min_distance + get_distance(new_taxi_position, min_customer)
            totalDistance += tripDistance

            print(f"Trip distance: {tripDistance}")
            print(f"Total distance: {totalDistance}")
            print(f"Trips counter: {tripsCounter}")
            print("\n")

            # Update trips counter
            tripsCounter += 1

    
    # Plot new state with all assignments for this step
    plot_state(available_taxi_list, waiting_customer_list, step, assignments)
    step += 1