import numpy as np
import math
# We basically create a matrix for the cost matrix aka the time that a certain taxi (even if occupied) has to travel 
# to reach a certain customer.

# The matrix we will use will have the following shape:
# n = number of taxis
# m = number of customers
# In the (1,1) position we will have the distance from the first taxi to the first customer

# We will get the position of all the taxis and the customers. To calculate the distance between the empty taxis and the customers
# we will use the euclidean distance formula: sqrt((x1 - x0)^2 + (y1 - y0)^2). We will then calculate the time to cover the distance.

# For the occupied taxis it's a bit more complicated. We will calculate the distance from the taxi to where the customer must be dropped, 
# we will then add the distance from the drop point to the other customers. We will then calculate the time to cover the distance.

taxi_distance # distance of the all the taxis to the customers, we get it from hungarian_algorithm.py 


times = taxi_distance/taxi_velocity

fast_time = min(times) # time to cover the distance

fast_index = #index of the taxi that will reach the customer first
fast_index = times.index(fast_time)

taxi_distance_to_destination = taxi_distance - taxi_velocity*fast_time
new_distances = taxi_distance_to_destination + destination_to_new_customer_distance

# Ributto poi in hungarian_algorithm.py che mi da tutte le seconde destinazioni 