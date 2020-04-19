#Tests written for helper functions
from helpers import can_contaminate,get_distance,schedule_delivery
from test_api import order_body
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
print(schedule_delivery(order_body))