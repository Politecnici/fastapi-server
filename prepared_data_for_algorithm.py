import numpy as np
import math
# We basically create a matrix for the cost matrix aka the time that a certain taxi (even if occupied) has to travel 
# to reach a certain customer.

# The matrix we will use will have the following shape:
# m = number of taxis
# n = number of customers
# In the (1,1) position we will have the distance from the first taxi to the first customer

# We will get the position of all the taxis and the customers. To calculate the distance between the empty taxis and the customers
# we will use the euclidean distance formula: sqrt((x1 - x0)^2 + (y1 - y0)^2). We will then calculate the time to cover the distance.

# For the occupied taxis it's a bit more complicated. We will calculate the distance from the taxi to where the customer must be dropped, 
# we will then add the distance from the drop point to the other customers. We will then calculate the time to cover the distance.

taxi_pos = np.array([[1,2],[3,4],[5,6],[7,8],[9,10]])
customer_start_pos = np.array([[11,12],[13,14],[15,16],[17,18],[19,20]])

n_taxi = taxi_pos.shape[0]
m_customer = customer_start_pos.shape[0]

# We will calculate the distance from the taxi to the customer

distance_matrix = np.zeros((n_taxi,m_customer))

for i in range(n_taxi):
    for j in range(m_customer):
        distance_matrix[i,j] = get_distance(taxi_pos[i], customer_start_pos[j])



# np.asarray([[82,83,69,92],[77,37,49,92],[11,69,5,86],[8,9,98,23]]) example on how the data must be put in the class