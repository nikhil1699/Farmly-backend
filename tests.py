#Tests written for helper functions
import datetime
from helpers import can_contaminate,get_distance,schedule_delivery
from optimization import main
from test_api import order_body,truckLocation,supplierLocation,deliveryLocation
#can_contaminate tests
inventory = [
	{'category':'meat'},
	{'category':'poultry'},
	{'category':'vegetables'}
]

categories = ['meat','grains','vegetables']
"""
for category in categories:
	print(category,can_contaminate(inventory,category))
"""
#Expected Results
	#meat = True(vegetable)
	#grains = False
	#vegetables = True(meat)

#get distance tests
"""
print(get_distance(43.778149,-79.344138,43.816348,-79.214170))
"""

#schedule delivery tests
# print(schedule_delivery(order_body))

inventory = [
	{
		'idealDeliveryDate': datetime.datetime(2020, 4, 18, 17, 10, 55, 820000),
		 'product': {
			 'sharetribeid': 'fake-id', 
			 'name': 'apple', 
			 'category': 'fruit', 
			 'supplierLocation': 
			 {'address': '10 Dundas East,Toronto ON', 'geolocation': {'lat': 43.65686, 'lng': -79.380431}}, 
			 'deliveryLocation': 
			 {'address': '19 Carisbrooke SQ, Toronto ON', 'geolocation': {'lat': 43.816348, 'lng': -79.21417}}}
	},
	{
		'idealDeliveryDate': datetime.datetime(2020, 4, 18, 17, 10, 55, 820000),
		 'product': {
			 'sharetribeid': 'fake-id', 
			 'name': 'apple', 
			 'category': 'fruit', 
			 'supplierLocation': 
			 {'address': '10 Dundas East,Toronto ON', 'geolocation': {'lat': 43.65686, 'lng': -79.380431}}, 
			 'deliveryLocation': 
			 {'address': '3359 Mississauga Rd, Mississauga, ON', 'geolocation': {'lat':43.555661, 'lng': -79.662065}}}
	}
	]
	
e = main(truckLocation,inventory)
print(e)