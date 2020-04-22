from haversine import haversine, Unit
from pymongo import MongoClient
from bson.objectid import ObjectId
from optimization import main
import datetime

uri = 'mongodb+srv://moiz:admin123@cluster0-hyg21.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE'
client = MongoClient(uri,
                     connectTimeoutMS=30000,
                     socketTimeoutMS=None,
                     socketKeepAlive=True)

db = client.Farmly

contamintation_categories = {
	'bread':[],
	'cereal':[],
	'rice':['wheat'],
	'pasta':[],
	'noodles':[],
	'grains':[],
	'vegetables':['meat','poultry'],
	'legumes':[],
	'fruit':['meat'],
	'meat':['vegetables','fruit','milk'],
	'fish':[],
	'poultry':['milk','fruits','vegetables'],
	'eggs':[],
	'nuts':[],
	'milk':['meat']
} 
#product(key) contaimnates when with product(value)

def get_distance(lat1,lng1,lat2,lng2):
	#find distance between two locations
	return haversine((lat1,lng1),(lat2,lng2))

def can_contaminate(inventory,category):
	#determine if the inventory of this truck can contaminate with this product
	if category in contamintation_categories:
		contaminants = contamintation_categories[category] #list of contaminants
		if not contaminants:
			return False 
		else:
			for product in inventory:
				if product['product']['category'] in contaminants:
					return True
	return False

def is_new(truck,date):
	#returns if this truck needs a new delivery scheduled for the date
	print(truck['_id'])
	if not 'deliveries' in truck:
		return True 
	else:
		for delivery in truck['deliveries']:
			if delivery['deliveryDate'] == date:
				return delivery['_id']
	return True

def prevent_contamination(potential_couriers,idealDelivery,food_category):
	#returns a list of couriers, that are safe to deliver without risk of cross-contamination
	result = potential_couriers[:]
	for courier in potential_couriers:
		if 'deliveries' in courier['truck']:
			for delivery in courier['truck']['deliveries']:
				inventory = delivery['inventory']
				if can_contaminate(inventory,food_category) and (delivery['deliveryDate']==idealDelivery) and (courier in result):
					result.remove(courier)
	return result

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
	contaminants = []
	if food_category in contamintation_categories:
		contaminants = contamintation_categories[food_category]
	idealDelivery = order['idealDeliveryDate']
	supplier_lat = order['product']['supplierLocation']['geolocation']['lat']
	supplier_lng = order['product']['supplierLocation']['geolocation']['lng']
	delivery_lat = order['product']['deliveryLocation']['geolocation']['lat']
	delivery_lng = order['product']['deliveryLocation']['geolocation']['lng']
	for truck in trucks:
		truck_lat = truck['truckLocation']['geolocation']['lat']
		truck_lng = truck['truckLocation']['geolocation']['lng']
		collection_radius = truck['collectionRadius']
		delivery_radius = truck['deliveryRadius']
		supplier_distance = get_distance(supplier_lat,supplier_lng,truck_lat,truck_lng)
		delivery_distance = get_distance(delivery_lat,delivery_lng,truck_lat,truck_lng)
		if supplier_distance <= collection_radius and delivery_distance <= delivery_radius:
			potential_couriers.append({'truck':truck,'delivery_distance':delivery_distance})
	if not potential_couriers:
		print('bitchhhh')
		return None
	potential_couriers = prevent_contamination(potential_couriers,idealDelivery,food_category)
	for courier in potential_couriers:
		#option 1:if the order's food category is suitable for this courier, add to this truck
		#option 2: if product is sensitive 
		delivery_distance = courier['delivery_distance']
		if delivery_distance < min_distance:
			optimal_truck = courier['truck']
			min_distance = delivery_distance
	#now we have the optimal truck
	#we can now add this order to the optimal trucks inventory for the ideal delivery date
	#find if truck has delivery scheduled idealDeliveryDate, if not then we can create a new delivery object, otherwise we add to the inventory
	if not optimal_truck:
		print('ah shit')
		return False
	new_delivery = is_new(optimal_truck,idealDelivery) #this truck has delivery object with deliveryDate set as idealDelivery
	if new_delivery == True:
		print('MOTHER FUCK')
		delivery_object = {
			'deliveryDate':idealDelivery,
			'route':main(optimal_truck['truckLocation'],[order]),
			'inventory':[order],
			'status':'scheduled'
		}
		delivery_inserted = db.deliveries.insert(delivery_object)
		delivery = db.deliveries.find_one({'_id':delivery_inserted})
		truck_updated =  db.trucks.update_one({'_id':optimal_truck['_id']},{"$push":{'deliveries':delivery}})
		if truck_updated.modified_count == 1:
			return delivery['deliveryDate']
		#add this delivery object to truck
	else:
		print('WTF')
		delivery = db.deliveries.find_one({'_id':new_delivery})
		added_inventory = db.deliveries.update_one({'_id':new_delivery},{"$push":{'inventory':order}})
		#inventory has now been added, we can now update the deliveries route
		#we do this by passing truck location, and the inventory
		route = main(optimal_truck['truckLocation'],delivery['inventory'])
		print(route)
		added_route = db.deliveries.update_one({'_id':new_delivery},{"$set":{'route':route}})
		delivery_now = db.db.deliveries.find_one({'_id':new_delivery})
		if added_route.modified_count == 1:
			print('hello',new_delivery)
			updated_truck = db.trucks.update_one({'_id':optimal_truck['_id'],"deliveries._id":new_delivery},{"$set":{"deliveries.$":delivery_now}})
			if updated_truck.modified_count == 1:
				return delivery['deliveryDate']
		else:
			print('BUCKETTTTS')
	return False

# print(db.trucks.find_one({})[''])
# print(db.trucks.update_one({"_id": ObjectId('5e9b6c4418eff95e887b0b7e'), "deliveries._id": ObjectId('5e9b6ce0e1b3d66267772ae6')},{"$set":{"deliveries.$":db.deliveries.find_one({'_id':ObjectId('5e9b6ce0e1b3d66267772ae6')})}}))
# print([db.deliveries.find_one({})['inventory'][0]])