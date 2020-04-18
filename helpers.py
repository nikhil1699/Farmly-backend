import datetime

contamintation_categories = {
	'bread':[],
	'cereal':[],
	'rice':['wheat'],
	'pasta':[],
	'noodles':[],
	'grains':[],
	'vegetables':['meat','poultry'],
	'legumes':[],
	'fruit':[],
	'meat':[],
	'fish':[],
	'poultry':[],
	'eggs':[],
	'nuts':[]
} 
#product(key) contaimnates when with product(value)

def get_distance(lat1,lng1,lat2,lng2):
	#find distance between two locations
	pass

def can_contaminate(inventory,category):
	#determine if the inventory of this truck can contaminate with this product
	pass 


def schedule_delivery(order):
	"""Push product to matched truck's deliveries array, and return a delivery date"""
	#Step 1: Find trucks that will match
		#Matching Step 1: Within supplier and delivery radius
		#Matching Step 2: Find trucks that don't risk cross contamination
		#Mathching Step 3: Add product to closest truck
	#Step 2: Add this order to the inventory
	#Step 3: Add the delivery date
	#Step 4: Add an optimized route
	trucks = db.trucks.find({})
	potential_couriers = []
	food_category = order['product']['category']
	min_distance = float('inf')
	optimal_truck = None
	contaminants = contamintation_categories[food_category]
	supplier_lat = order['product']['supplierLocation']['geolocation']['lat']
	supplier_lng = order['product']['supplierLocation']['geolocation']['lng']
	delivery_lat = order['product']['deliveryLocation']['geolocation']['lat']
	delivery_lng = order['product']['deliveryLocation']['geolocation']['lng']
	for truck in trucks:
		truck_lat = truck['truckLocation']['geoLocation']['lat']
		truck_lng = truck['truckLocation']['geoLocation']['lng']
		collection_radius = truck['collectionRadius']
		delivery_radius = truck['deliveryRadius']
		supplier_distance = get_distance(supplier_lat,supplier_lng,truck_lat,truck_lng)
		delivery_distance = get_distance(delivery_lat,delivery_lng,truck_lat,truck_lng)
		if supplier_distance <= collection_radius and delivery_distance <= delivery_radius:
			potential_couriers.append({'truck':truck,'delivery_distance':delivery_distance})
	for courier in potential_couriers:
		#option 1:if the order's food category is suitable for this courier, add to this truck
		#option 2: if product is sensitive 
		delivery_distance = courier['delivery_distance']
		if 'deliveries' in courier['truck']:
			inventory = courier['truck']['inventory']
			if can_contaminate(inventory,food_category):
				potential_couriers.remove(courier)
			else:
				if delivery_distance < min_distance:
					optimal_truck = courier['truck']
					min_distance = delivery_distance
		else:
			#no products in this truck
			if delivery_distance < min_distance:
				optimal_truck = courier['truck']
				min_distance = delivery_distance
	#now we have the optimal truck
	return datetime.datetime.now()