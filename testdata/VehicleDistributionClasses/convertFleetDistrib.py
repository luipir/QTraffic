import json

with open('./FleetSplit.json') as jsonFile:
	jsonData = json.load(jsonFile)

def parseDict(d):
	if not isinstance(d, dict):
		print "value = ", d
		return
	
	for key, values in d.items():
		print "name: ", key
		parseDict(values)
			
		

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
			 	   "children": [] }
	
	for fuelName, classes in fuels.items():
		if fuelName == "available" or fuelName == "value":
			continue
		
		fuelDict = {"name" : fuelName, 
					"description": fuelName,
					"available": classes["available"],
					"value": classes["value"],				
					"children": [] }
		
		for euroClass, euroSubClasses in classes.items():
			if euroClass == "available" or euroClass == "value":
				continue
			
			euroDict = {"name" : euroClass, 
						"description": euroClass,
						"available": euroSubClasses["available"],
						"value": euroSubClasses["value"],			
						"children": [] }
			
			for euroSubClass, value in euroSubClasses.items():
				if euroSubClass == "available" or euroSubClass == "value":
					continue
				
				subClass = {"name" : euroSubClass, 
							"description": euroSubClass,
							"available": value["available"],
							"value": value["value"]	}
				
				euroDict["children"].append(subClass)

			fuelDict["children"].append(euroDict)
			
		vehicleDict["children"].append(fuelDict)

	class1["children"].append(vehicleDict)

roadTypes["children"].append(class1)

with open('./FleetSplit-converted.json', 'w') as outfile:
    json.dump(roadTypes, outfile)



