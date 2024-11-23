import numpy as np
import math
import random
import matplotlib.pyplot as plt
import time
from scipy.optimize import linear_sum_assignment

random.seed(42)

GRID_HEIGHT = 100
GRID_WIDTH = 100

TAXI_NUMBER = 5
CUSTOMER_NUMBER = 20


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

def get_distance(taxi, customer):
    x0 = (taxi.x - customer.coordX) ** 2
    x1 = (taxi.y - customer.coordY) ** 2
    return math.sqrt(x0 + x1)

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

        # create a np matrix of distances. Rows: len(waiting_customer_list), Columns: len(available_taxi_list)
        cost_matrix = np.zeros((len(waiting_customer_list), len(taxi_list)))

        for i, customer in enumerate(waiting_customer_list):
            for j, taxi in enumerate(taxi_list):
                cost_matrix[i, j] = get_distance(taxi, customer)

        # Pad the matrix with zeros
        rows, cols = cost_matrix.shape
        if rows < cols:
            cost_matrix = np.vstack([cost_matrix, np.zeros((cols - rows, cols))])
        elif rows > cols:
            cost_matrix = np.hstack([cost_matrix, np.zeros((rows, rows - cols))])

        # Apply the Hungarian algorithm
        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        # Filter out dummy assignments (if any)
        assignments = [(r, c) for r, c in zip(row_ind, col_ind) if r < rows and c < cols]

        # Output the result
        print(f"Step {step}: Assignments: {assignments}")

        # tell which customer is assigned to which taxi
        for r, c in assignments:
            print(f"Customer {waiting_customer_list[r].id} assigned to Taxi {taxi_list[c].id}")
        
        # move the taxis to the new customer position
        for r, c in assignments:
            taxi_list[c].x = waiting_customer_list[r].coordX
            taxi_list[c].y = waiting_customer_list[r].coordY

        # remove the assigned customers from the list
        waiting_customer_list = [customer for i, customer in enumerate(waiting_customer_list) if i not in [r for r, c in assignments]]

        # Plot the state
        plot_state([(taxi.x, taxi.y) for taxi in taxi_list], [(customer.coordX, customer.coordY) for customer in waiting_customer_list], step, [(taxi_list[c].x, taxi_list[c].y) for r, c in assignments])





run_simulation()
