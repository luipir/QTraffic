# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QTraffic
 A QGIS plugin Road contamination modelling for EMSURE Project
                              -------------------
        begin                : 2015-04-20
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Luigi Pirelli (for EMSURE project)
        email                : luipir@gmail.lcom
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import json
import collections

# init map conversion
convertionDict = {
	"fleetComposition": "",
	"Fleet Type": "F_Type_",
	"Passenger cars": "Passenger cars",
	"Light duty vehicles": "Light duty vehicles",
	"Heavy duty vehicles": "Heavy duty vehicles",
	"Urban buses": "Urban buses",
	"Coaches": "Coaches",
	"Motorcycles": "Motorcycles",
	"Gasoline": "Gasoline",
	"Diesel": "Diesel",
	"LPG": "LPG",
	"Hybrids": "Hybrids",
	"New fuel": "New",
	"PRE EURO": "Euro0",
	"EURO 1": "Euro1",
	"EURO 2": "Euro2",
	"EURO 3": "Euro3",
	"EURO 4": "Euro4",
	"EURO 5": "Euro5",
	"EURO 6": "Euro6",
	"CONVENTIONAL": "Euro0"
}
leafCounter = {
	"Fleet Type": 1,
	"Passenger cars": 1,
	"Heavy duty vehicles": 200,
	"Urban buses": 300,
	"Coaches": 400,
	"Motorcycles": 500
}

# open and read the json file
with open('./FleetSplit.json') as jsonFile:
	jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)

# start to create 
fleetCompositionValue = jsonData["fleetComposition"]
fleetCompostionDict = collections.OrderedDict({
	"name": "fleetComposition",
	"converted": "",
	"children": []
})

for fleatType, vehicleTypes in fleetCompositionValue.items():
	
	fleetTypeDict = collections.OrderedDict(
						{"name": fleatType,
						"converted": convertionDict["Fleet Type"] + str(leafCounter["Fleet Type"]),
						"children": []	}
					)
	leafCounter["Fleet Type"] += 1

	for vehicleType,fuels in vehicleTypes.items():
		
		vehicleDict = collections.OrderedDict(
						{"name" : vehicleType,
						"converted":  convertionDict[vehicleType],
						"total" : 1000,
						"percentage" : 100.0,
						"locked" : 1,
					 	"children": [] }
					)
		
		for fuelName, classes in fuels.items():
			if fuelName == "value":
				continue
			
			fuelDict = collections.OrderedDict(
						{"name" : fuelName, 
						"converted": convertionDict[fuelName],
						"locked": 0,
						"percentage": classes["value"],				
						"children": [] }
					)
			
			for euroClass, euroSubClasses in classes.items():
				if euroClass == "value":
					continue
				
				# check if Motorcycle because the JSOn does not have fuel subclasses but directly subclasses
				if vehicleType == "Motorcycles":
					converted = "k{:0>3d}".format( leafCounter[vehicleType] ) # e.g k055 = k + three 0 padding right justified
					leafCounter[vehicleType] += 1
				else:
					converted = convertionDict[euroClass]
				
				euroDict = collections.OrderedDict(
							{"name" : euroClass, 
							"converted": converted,
							"locked": 0,
							"percentage": euroSubClasses["value"],			
							"children": [] }
						)
				
				for euroSubClass, value in euroSubClasses.items():
					if euroSubClass == "value":
						continue
					
					subClass = collections.OrderedDict(
								{"name" : euroSubClass, 
								"converted": "k{:0>3d}".format( leafCounter[vehicleType] ), # e.g k055 = k + three 0 padding right justified
								"locked": 0,
								"percentage": value["value"]}
							)
					leafCounter[vehicleType] += 1
					
					euroDict["children"].append(subClass)
	
				fuelDict["children"].append(euroDict)
				
			vehicleDict["children"].append(fuelDict)
	
		fleetTypeDict["children"].append(vehicleDict)
	
	fleetCompostionDict["children"].append(fleetTypeDict)


# now calc value applying % to 1000 vehicles on each vehicle type
# do it for each fleetType
fleetTypes = fleetCompostionDict["children"]
for fleetType in fleetTypes:
	# for each vehicle type
	vehicleTypes = fleetType["children"]
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
	json.dump(fleetCompostionDict, 
			  outfile, 
			  ensure_ascii=False, 
			  check_circular=True, 
			  allow_nan=True, 
			  cls=None, 
			  indent=2, # allow pretty formatting of the json
			  separators=None, 
			  encoding="utf-8", 
			  default=None, 
			  sort_keys=False) # to mantaine the oreding of the OrdererdDict



