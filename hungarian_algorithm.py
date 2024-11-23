import numpy as np
import math
import random
import matplotlib.pyplot as plt
import time
from scipy.optimize import linear_sum_assignment

random.seed(10)

GRID_HEIGHT = 100
GRID_WIDTH = 100

TAXI_NUMBER = 50
CUSTOMER_NUMBER = 300


class Taxi():
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.available = True

class Customer():
    def __init__(self, id, coordX, coordY, destinationX, destinationY):
        self.id = id
        self.coordX = coordX
        self.coordY = coordY
        self.destinationX = destinationX
        self.destinationY = destinationY
        self.awaitingService = True

# helper functions

def get_distance(p, q):
    x0 = (p[0] - q[0]) ** 2
    x1 = (p[1] - q[1]) ** 2
    return math.sqrt(x0 + x1)

# Plot the initial state
# input is a list of taxi objects, a list of customer objects, the current step and a list of assignments
def plot_state(taxis, customers, step, assignments=None):
    plt.figure(figsize=(10, 10))
    plt.xlim(0, GRID_WIDTH)
    plt.ylim(0, GRID_HEIGHT)
    
    # Plot taxis
    taxi_x, taxi_y = zip(*[(taxi.x, taxi.y) for taxi in taxis])
    plt.scatter(taxi_x, taxi_y, c='blue', marker='s', label='Taxis')
    
    # Plot customers
    if customers:
        customer_x, customer_y = zip(*[(customer.coordX, customer.coordY) for customer in customers])
        plt.scatter(customer_x, customer_y, c='red', marker='o', label='Customers')
    
    # Plot assignments (arrows from taxis to customers)
    if assignments:
        for taxi, customer in assignments:
            # Arrow from taxi to customer (initial assignment) starting from taxi position, ending at customer.coord
            plt.arrow(taxi.x, taxi.y, customer.coordX - taxi.x, customer.coordY - taxi.y,
                      head_width=1.5, head_length=2, fc='green', ec='green', linestyle='dotted', length_includes_head=True)            
            # Arrow from customer to new taxi position (different color) starting from customer.coord, ending at customer.destination
            plt.arrow(customer.coordX, customer.coordY, customer.destinationX - customer.coordX, customer.destinationY - customer.coordY,
                      head_width=1.5, head_length=2, fc='orange', ec='orange', linestyle='solid', length_includes_head=True)    
    plt.title(f"Step {step}: Taxis and Customers")
    plt.legend()
    plt.grid(True)
    plt.savefig(f'step_{step}.png')
    plt.close()


def run_simulation():

    taxi_list = []
    waiting_customer_list = []

    # Fill lists with random values inside the grid
    for i in range(TAXI_NUMBER):
        # create taxi object
        taxi = Taxi("t"+str(i), random.randint(0, GRID_WIDTH), random.randint(0, GRID_HEIGHT))
        taxi_list.append(taxi)

    for i in range(CUSTOMER_NUMBER):
        # create customer object
        customer = Customer("c"+str(i), random.randint(0, GRID_WIDTH), random.randint(0, GRID_HEIGHT), random.randint(0, GRID_WIDTH), random.randint(0, GRID_HEIGHT))
        waiting_customer_list.append(customer)

    # Simulation loop
    step = 0
    tripsCounter = 0
    totalDistance = 0

    # start timer
    start = time.time()

    while len(waiting_customer_list) > 0:

        # print(f"Step {step}: Taxis: {len(taxi_list)}, Customers: {len(waiting_customer_list)}")

        # create a np matrix of distances. Rows: len(waiting_customer_list), Columns: len(available_taxi_list)
        cost_matrix = np.zeros((len(waiting_customer_list), len(taxi_list)))

        for i, customer in enumerate(waiting_customer_list):
            for j, taxi in enumerate(taxi_list):
                cost_matrix[i, j] = get_distance((taxi.x, taxi.y), (customer.coordX, customer.coordY))

        # Pad the matrix with zeros
        rows, cols = cost_matrix.shape
        if rows < cols:
            cost_matrix = np.vstack([cost_matrix, np.zeros((cols - rows, cols))])
        elif rows > cols:
            cost_matrix = np.hstack([cost_matrix, np.zeros((rows, rows - cols))])

        # Apply the Hungarian algorithm
        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        # Filter out dummy assignments (if any) assignements (taxi, customer)
        assignments = [(taxi_list[j], waiting_customer_list[i]) for i, j in zip(row_ind, col_ind) if i < len(waiting_customer_list) and j < len(taxi_list)]

        # Output the result
        # print(f"Step {step}: Assignments: {assignments}")

        # increase number of trips
        tripsCounter += len(assignments)

        # calculate total distance
        for (taxi, customer) in assignments:
            totalDistance += get_distance((taxi.x, taxi.y), (customer.coordX, customer.coordY))
            totalDistance += get_distance((customer.coordX, customer.coordY), (customer.destinationX, customer.destinationY))
        
        print(f"Total distance: {totalDistance}")


        # remove the assigned customers from the list
        waiting_customer_list = [customer for customer in waiting_customer_list if customer not in [assignment[1] for assignment in assignments]]

        # Plot the state
        plot_state(taxi_list, waiting_customer_list, step, assignments)


        # move the taxis to the new customer position
        for taxi, customer in assignments:
            taxi.x = customer.destinationX
            taxi.y = customer.destinationY
            taxi.available = True

        

        # increase step
        step += 1
    
    # end timer
    end = time.time()

    print(f"Total trips: {tripsCounter}")
    print(f"Total time: {end - start}")
    print(f"Total distance: {totalDistance}")




run_simulation()
