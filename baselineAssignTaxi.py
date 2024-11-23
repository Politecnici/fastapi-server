import math
import random
import matplotlib.pyplot as plt
import time

random.seed(42)

GRID_HEIGHT = 100
GRID_WIDTH = 100

TAXI_NUMBER = 500
CUSTOMER_NUMBER = 3000

# parameters for space quantization
nYcells = 10
nXcells = 10

# divide the grid into cells
cellWidth = GRID_WIDTH/nXcells
cellHeight = GRID_HEIGHT/nYcells



# helper functions

def get_distance(taxi_pos, customer_start_pos):
    x0 = (taxi_pos[0] - customer_start_pos[0]) ** 2
    x1 = (taxi_pos[1] - customer_start_pos[1]) ** 2
    return math.sqrt(x0 + x1)

def getTaxiCell(taxi_pos):
    xCell = int(math.floor(taxi_pos[0]/cellWidth))
    yCell = int(math.floor(taxi_pos[1]/cellHeight))
    return (xCell, yCell)
def getTaxiCell(taxi_pos):
    xCell = int(math.floor(taxi_pos[0]/cellWidth))
    yCell = int(math.floor(taxi_pos[1]/cellHeight))
    return (xCell, yCell)

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

# 1. Assign the closest customer to each taxi
def baseline_assign_customer_to_taxi(taxi, waiting_customer_list):

    min_distance = float('inf')
    min_customer = None

    # Find the closest customer
    for customer in waiting_customer_list:
        distance = get_distance(taxi, customer)
        if distance < min_distance:
            min_distance = distance
            min_customer = customer

    return min_customer, min_distance

def space_quantization_assign_customer_to_taxi(taxi, customerCells):

    # Get the cell of the taxi
    taxiCell = getTaxiCell(taxi)
    # print(f"Taxi at {taxi} in cell {taxiCell}")

    # Get the closest customer in the same cell
    min_distance = float('inf')
    min_customer = None

    if taxiCell in customerCells:
        for customer in customerCells[taxiCell]:
            distance = get_distance(taxi, customer)
            if distance < min_distance:
                min_distance = distance
                min_customer = customer

    # If there are no customers in the same cell, get random customers from the surrounding cells, return when found
    if not min_customer:
        # check surrounding cells start with step 1 and increase until a customer is found
        step = 1
        while not min_customer:
            # check the cells at the step away
            for x in range(taxiCell[0] - step, taxiCell[0] + step + 1):
                for y in range(taxiCell[1] - step, taxiCell[1] + step + 1):
                    if (x, y) in customerCells:
                        for customer in customerCells[(x, y)]:
                            distance = get_distance(taxi, customer)
                            if distance < min_distance:
                                min_distance = distance
                                min_customer = customer
                                taxiCell = (x, y)
            step += 1
        
    # remove selected customer from the cell
    assert(min_customer)
    customerCells[taxiCell].remove(min_customer)

    return min_customer, min_distance



# Main simulation loop
def run_simulation():

    available_taxi_list = []
    waiting_customer_list = []

    # Fill lists with random values inside the grid
    for i in range(TAXI_NUMBER):
        available_taxi_list.append([random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1)])

    for i in range(CUSTOMER_NUMBER):
        waiting_customer_list.append([random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1)])


    # assign each customer to a cell - used only for space quantization

    customerCells = {}

    for customer in waiting_customer_list:
        xCell = math.floor(customer[0]/cellWidth)
        yCell = math.floor(customer[1]/cellHeight)
        if (xCell, yCell) in customerCells:
            customerCells[(xCell, yCell)].append(customer)
        else:
            customerCells[(xCell, yCell)] = [customer]

    # for all keys print list
    # for key in customerCells:
    #     print(key, ' : ', customerCells[key])

    # Simulation loop
    step = 0
    tripsCounter = 0
    totalDistance = 0

    # start timer
    start = time.time()

    while len(waiting_customer_list) > 0:
        # print(f"Step {step}")

        assignments = []
        for taxi in available_taxi_list[:]:  # Iterate over a copy of the list
            if len(waiting_customer_list) == 0:
                break

            tripDistance = 0
            
            customer, distToCustomer = baseline_assign_customer_to_taxi(taxi, waiting_customer_list)

            # customer, distToCustomer = space_quantization_assign_customer_to_taxi(taxi, customerCells)

            # Assign customer to taxi
            if customer:
                # print(f"Taxi at {taxi} assigned to customer at {customer}")
                waiting_customer_list.remove(customer)

                # Move taxi to a new random position
                new_taxi_position = [random.randint(0, GRID_WIDTH), random.randint(0, GRID_HEIGHT)]
                assignments.append((taxi, customer, new_taxi_position))
                available_taxi_list[available_taxi_list.index(taxi)] = new_taxi_position
                # print(f"Taxi moved to {new_taxi_position}")
                # print(f"Remaining customers: {len(waiting_customer_list)}")

                # Update total distance
                tripDistance = distToCustomer + get_distance(new_taxi_position, customer)
                totalDistance += tripDistance

                # print(f"Trip distance: {tripDistance}")
                # print(f"Total distance: {totalDistance}")
                # print(f"Trips counter: {tripsCounter}")
                # print("\n")

                # Update trips counter
                tripsCounter += 1

        
        # Plot new state with all assignments for this step
        plot_state(available_taxi_list, waiting_customer_list, step, assignments)
        step += 1

    # end timer
    end = time.time()

    print(f"Total trips: {tripsCounter}")
    print(f"Total time: {end - start}")
    print(f"Total distance: {totalDistance}")

    # print(waiting_customer_list)
    # print(customerCells)

# run the simulation
if __name__ == "__main__":
    for i in range(10):
        run_simulation()