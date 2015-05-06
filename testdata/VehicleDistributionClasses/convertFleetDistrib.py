import json
import collections

with open('./FleetSplit.json') as jsonFile:
	jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)

class1 = jsonData["fleetComposition"]
class1Value = class1["1"]

roadTypes = {
	"name": "Road Types",
	"description": "Road Types",
	"children": []
}

class1 = {
	"name": "Road Type 1",
	"description": "Road Type 1",
	"children": []
}

for vehicleType,fuels  in class1Value["Road Type 1"].items():
	
	vehicleDict = {"name" : vehicleType, 
				   "description": vehicleType,
				   "total" : 1000,
				   "percentage" : 100.0,
				   "locked" : 1,
			 	   "children": [] }
	
	for fuelName, classes in fuels.items():
		if fuelName == "value":
			continue
		
		fuelDict = {"name" : fuelName, 
					"description": fuelName,
					"locked": 0,
					"percentage": classes["value"],				
					"children": [] }
		
		for euroClass, euroSubClasses in classes.items():
			if euroClass == "value":
				continue
			
			euroDict = {"name" : euroClass, 
						"description": euroClass,
						"locked": 0,
						"percentage": euroSubClasses["value"],			
						"children": [] }
			
			for euroSubClass, value in euroSubClasses.items():
				if euroSubClass == "value":
					continue
				
				subClass = {"name" : euroSubClass, 
							"description": euroSubClass,
							"locked": 0,
							"percentage": value["value"]	}
				
				euroDict["children"].append(subClass)

			fuelDict["children"].append(euroDict)
			
		vehicleDict["children"].append(fuelDict)

	class1["children"].append(vehicleDict)

roadTypes["children"].append(class1)


# now calc value applying % to 1000 vehicles on each vehicle type
roadClasses = roadTypes["children"]
roadClassType1 = roadClasses[0]
vehicleTypes = roadClassType1["children"]

for veihicleType in vehicleTypes:	
	# for each internal category calc total basing on it's % on <upper container>["total"]
	fuelClasses = veihicleType["children"]
	for fuelClass in fuelClasses:
		fuelClass["total"] = veihicleType["total"] * fuelClass["percentage"] / 100.0
		
		# for each internal category calc total basing on it's % on <upper container>["total"]
		euroClasses = fuelClass["children"]
		for euroClass in euroClasses:
			euroClass["total"] = fuelClass["total"] * euroClass["percentage"] / 100.0
	
			# for each internal category calc total basing on it's % on <upper container>["total"]
			euroSubClasses = euroClass["children"]
			for euroSubClass in euroSubClasses:
				euroSubClass["total"] = euroClass["total"] * euroSubClass["percentage"] / 100.0


with open('./FleetSplit-converted.json', 'w') as outfile:
    json.dump(roadTypes, outfile)



