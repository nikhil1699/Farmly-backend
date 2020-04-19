"""Simple Pickup Delivery Problem (PDP)."""
from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from haversine import haversine, Unit
import numpy

def get_distance(lat1,lng1,lat2,lng2):
	#find distance between two locations
	return haversine((lat1,lng1),(lat2,lng2))

def create_data_model(truck_location,inventory):
    """Stores the data for the problem."""
    locations = [truck_location]
    pickups_deliveries = []
    for product in inventory:
        locations.append(product['product']['supplierLocation'])
        locations.append(product['product']['deliveryLocation'])
    unmatched = list(range(1,len(locations)))
    for i in range(0, len(unmatched), 2):
        pickups_deliveries.append(unmatched[i:i+2])
    n = len(locations)
    initial_matrix = numpy.zeros((n,n),dtype=numpy.int)
    for i in range(len(initial_matrix)):
        for j in range(len(initial_matrix[i])):
            #calculate distance between location[i] and location[j]
            lat_1 = locations[i]['geolocation']['lat']
            lng_1 = locations[i]['geolocation']['lng']
            lat_2 = locations[j]['geolocation']['lat']
            lng_2 = locations[j]['geolocation']['lng']
            initial_matrix[i][j] = int(get_distance(lat_1,lng_1,lat_2,lng_2))
            # print(locations[i],locations[j])
            # initial_matrix[i][j] = 3
    distance_matrix = initial_matrix.tolist()


    data = {}
    data['distance_matrix'] = distance_matrix
    data['locations'] = locations
    data['pickups_deliveries'] = pickups_deliveries
    data['num_vehicles'] = 1
    data['depot'] = 0
    return data


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    total_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = ''
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(data['locations'][manager.IndexToNode(index)]['address'])
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += '{}\n'.format(data['locations'][manager.IndexToNode(index)]['address'])
        plan_output += 'Distance of the route: {}miles'.format(route_distance)
        return plan_output
        total_distance += route_distance
    print('Total Distance of all routes: {}m'.format(total_distance))


def main(truck_location,inventory):
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model(truck_location,inventory)

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)


    # Define cost of each arc.
    def distance_callback(from_index, to_index):
        """Returns the manhattan distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    dimension_name = 'Distance'
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        3000,  # vehicle maximum travel distance
        True,  # start cumul to zero
        dimension_name)
    distance_dimension = routing.GetDimensionOrDie(dimension_name)
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Define Transportation Requests.
    for request in data['pickups_deliveries']:
        pickup_index = manager.NodeToIndex(request[0])
        delivery_index = manager.NodeToIndex(request[1])
        routing.AddPickupAndDelivery(pickup_index, delivery_index)
        routing.solver().Add(
            routing.VehicleVar(pickup_index) == routing.VehicleVar(
                delivery_index))
        routing.solver().Add(
            distance_dimension.CumulVar(pickup_index) <=
            distance_dimension.CumulVar(delivery_index))

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        return print_solution(data, manager, routing, solution)


# if __name__ == '__main__':
#     main()

#Locations
	#0: Truck, 1: Pickup1 , 2:Delivery1,3:Delivery2,4:Pickup2
	#0:Fairview Mall,1: 10 Dundas,2:Carisbrooke,3:UTM,4:10 Dundas

	#pickup_deliveries
		#[1,2]
		#[4,3]
	
	#distance matrix
		# [
		# 	[0,11,9,28,11]
		# 	[11,0,18,18,0],
		# 	[9,18,0,36,18],
		# 	[28,18,36,0,18],
		# 	[11,0,18,18,0]
		# ]

		# dundas,utm = 18