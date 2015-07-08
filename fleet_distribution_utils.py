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
# 2To3 python compatibility
from __future__ import print_function
from __future__ import unicode_literals

#############################################################################
'''
NOTES FOR THE READER: This code has been created to convert a JSON hirarchical
file. in the format of FleetDistribution-converted.json in the Sequencial and
positional file format as in v_fleet_distribution-original-txt.
Because of format exception has been difficult to create modular code and this
created a really low quality code with a high probability to be modified every
time organization of the v_fleet_distribution change of a different kind of
original fleet distribution json change because change the the domain of the
problem.
I tried to convince to use more robust format about v_fleet_distribution but
I wasn't able, so this is the result of the adaptation. 
So reader, please don't shame me about the quality of this code!
'''
#############################################################################


import json
import collections

def jsonToTxt(jsonFileName, outTxtFileName):
    ''' convert from fleet distribution json to txt format necessary for the algorithm
    '''
    # open and read the json file
    with open(jsonFileName) as jsonFile:
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
    
    F_Types = jsonData['children']
    F_Type_converted = F_Types[0]['converted']
    F_Type_converted = F_Type_converted[:-2] # expected F_Type_1 => remove _1
    
    fleetTypesIndexs = [str(x+1) for x in range(len(F_Types))]
    
    with open(outTxtFileName, 'w') as outfile:
        #***Fleet composition (%)***        
        #F_Type    1    2
        print('''***Fleet composition (%)***''', file=outfile)
        print(F_Type_converted + '\t'+ '\t'.join(fleetTypesIndexs), file=outfile)
        
        # ****************************        
        # *LEVEL1 - FUEL distribution*        
        # ****************************
        print('''****************************''', file=outfile)
        print('''*LEVEL1 - FUEL distribution*''', file=outfile)
        print('''****************************''', file=outfile)
        
        # better using index that key:value due to print different values
        # for different fleets in the same row
        for (vehicleTypeIndex, vehicle) in enumerate(F_Types[0]['children']):
            # add vehicle name
            print('*{}'.format(vehicle['converted']), file=outfile)
            
            # manage Motorcycle exception
            # added this exception because Motorcycle seems
            # have different organization... have no fuel classes
            # because implicit Gasoline => it has one level less
            if vehicle['name'] == "Motorcycles":
                line = "Gasoline\t"
                values = ['100']*len(F_Types)
                line += '\t'.join(values)
                print(line, file=outfile)
                
                # write column totals
                totals = ['100.00%']*len(F_Types)
                print('Total\t'+ '\t'.join(totals), file=outfile)
                continue        
            
            for (fuelIndex, fuel) in enumerate(vehicle['children']):
                # get fuel converted
                fuelConverted = fuel['converted']
                
                # crete base string to show fuel values
                line = fuelConverted + '\t'
                
                # add to the baseString the values fro all fleet types
                values = []
                for fleetIndex in range(len(F_Types)):
                    currentFleet =  F_Types[fleetIndex]
                    currentVechicle = currentFleet['children'][vehicleTypeIndex]
                    currentFuel = currentVechicle['children'][fuelIndex]
                    
                    values.append( str(currentFuel['percentage']) )
            
                line += '\t'.join(values)
                
                # print complete line
                print(line, file=outfile)
    
            # write column totals
            totals = ['100.00%']*len(F_Types)
            print('Total\t'+ '\t'.join(totals), file=outfile)
            
        # ****************************        
        # *LEVEL2 - EURO classes******        
        # ****************************
        print('''****************************''', file=outfile)
        print('''*LEVEL2 - EURO classes******''', file=outfile)
        print('''****************************''', file=outfile)
        for (vehicleTypeIndex, vehicle) in enumerate(F_Types[0]['children']):
            # add vehicle name
            vehicleFuelLine = '*{} -'.format(vehicle['converted'])
            
            # exception regarding Motorcycle
            # added this exception because Motorcycle seems
            # have different organization... have no fuel classes
            # because implicit Gasoline => it has one level less
            if vehicle['name'] == "Motorcycles":
                # write vehicle/Fuel line
                print(vehicleFuelLine[:-2], file=outfile) # removing last ' -'
                
                # now loop for each Euro class
                for (euroIndex, euro) in enumerate(vehicle['children']):
                    # get Euro converted
                    euroConverted = euro['converted']
                    
                    # crete base string to show euro values
                    line = euroConverted + '\t'
                    
                   # add to the baseString the values for all fleet types
                    values = []
                    for fleetIndex in range(len(F_Types)):
                        currentFleet =  F_Types[fleetIndex]
                        currentVechicle = currentFleet['children'][vehicleTypeIndex]
                        currentEuro = currentVechicle['children'][euroIndex]
                        
                        values.append( str(currentEuro['percentage']) )
                
                    line += '\t'.join(values)
                    
                    # print complete line
                    print(line, file=outfile)
    
                # write column totals for the current Vehicle/Fuel
                totals = ['100.00%']*len(F_Types)
                print('Total\t'+ '\t'.join(totals), file=outfile)
                
                # then jump to the next vehicle
                continue
            
            # manage the other fuel classes as usual
            for (fuelIndex, fuel) in enumerate(vehicle['children']):
                # avoid add line if no children at all
                if len(fuel['children']) == 0:
                    continue
                
                # get fuel converted
                fuelConverted = fuel['converted']
                
                # write vehicle/Fuel line
                print(vehicleFuelLine+fuelConverted, file=outfile)
                
                # now loop for each Euro class
                for (euroIndex, euro) in enumerate(fuel['children']):
                    # get Euro converted
                    euroConverted = euro['converted']
                    
                    # crete base string to show euro values
                    line = euroConverted + '\t'
                    
                   # add to the baseString the values for all fleet types
                    values = []
                    for fleetIndex in range(len(F_Types)):
                        currentFleet =  F_Types[fleetIndex]
                        currentVechicle = currentFleet['children'][vehicleTypeIndex]
                        currentFuel = currentVechicle['children'][fuelIndex]
                        currentEuro = currentFuel['children'][euroIndex]
                        
                        values.append( str(currentEuro['percentage']) )
                
                    line += '\t'.join(values)
                    
                    # print complete line
                    print(line, file=outfile)
    
                # write column totals for the current Vehicle/Fuel
                totals = ['100.00%']*len(F_Types)
                print('Total\t'+ '\t'.join(totals), file=outfile)
        
        # ****************************        
        # *LEVEL3 - CAPACITY classes**        
        # ****************************
        print('''****************************''', file=outfile)
        print('''*LEVEL3 - CAPACITY classes**''', file=outfile)
        print('''****************************''', file=outfile)
        for (vehicleTypeIndex, vehicle) in enumerate(F_Types[0]['children']):
            # add vehicle name
            headerLine = '*{} -'.format(vehicle['converted'])
            
            # exception regarding Motorcycle
            # added this exception because Motorcycle seems
            # have different organization... have no fuel classes
            # because implicit Gasoline => it has one level less
            if vehicle['name'] == "Motorcycles":
                # now loop for each Euro class
                for (euroIndex, euro) in enumerate(vehicle['children']):
                    # avoid add line if no children at all
                    if len(euro['children']) == 0:
                        continue
                    
                    # get Euro converted
                    euroConverted = euro['converted']
                    
                    # write vehicleFuelEuroLine
                    print(headerLine+euroConverted, file=outfile)
    
                    # now loop for each subEuro class (if any)
                    for (subEuroIndex, subEuro) in enumerate(euro['children']):
                        # get subEuro converted
                        subeuroConverted = subEuro['converted']
                        
                        # crete base string to show subEuro values
                        line = subeuroConverted + '\t'
                    
                        # add to the baseString the values for all fleet types
                        values = []
                        for fleetIndex in range(len(F_Types)):
                            currentFleet =  F_Types[fleetIndex]
                            currentVechicle = currentFleet['children'][vehicleTypeIndex]
                            currentEuro = currentVechicle['children'][euroIndex]
                            currentSubEuro = currentEuro['children'][subEuroIndex]
                            
                            values.append( str(currentSubEuro['percentage']) )
                    
                        line += '\t'.join(values)
                        
                        # print complete line
                        print(line, file=outfile)
                
                    # write column totals for the current Vehicle/Fuel
                    totals = ['100.00%']*len(F_Types)
                    print('Total\t'+ '\t'.join(totals), file=outfile)
                    
                # then jump to the next vehicle
                continue
            
            for (fuelIndex, fuel) in enumerate(vehicle['children']):
                # get fuel converted
                fuelConverted = fuel['converted']
                
                # add vehicle/Fuel line
                vehicleFuelEuroLine = headerLine + fuelConverted+' -'
                
                # now loop for each Euro class
                for (euroIndex, euro) in enumerate(fuel['children']):
                    # avoid add line if no children at all
                    if len(euro['children']) == 0:
                        continue
                    
                    # get Euro converted
                    euroConverted = euro['converted']
                    
                    # write vehicleFuelEuroLine
                    print(vehicleFuelEuroLine+euroConverted, file=outfile)
    
                    # now loop for each subEuro class (if any)
                    for (subEuroIndex, subEuro) in enumerate(euro['children']):
                        # get subEuro converted
                        subeuroConverted = subEuro['converted']
                        
                        # crete base string to show subEuro values
                        line = subeuroConverted + '\t'
                    
                        # add to the baseString the values for all fleet types
                        values = []
                        for fleetIndex in range(len(F_Types)):
                            currentFleet =  F_Types[fleetIndex]
                            currentVechicle = currentFleet['children'][vehicleTypeIndex]
                            currentFuel = currentVechicle['children'][fuelIndex]
                            currentEuro = currentFuel['children'][euroIndex]
                            currentSubEuro = currentEuro['children'][subEuroIndex]
                            
                            values.append( str(currentSubEuro['percentage']) )
                    
                        line += '\t'.join(values)
                        
                        # print complete line
                        print(line, file=outfile)
        
                    # write column totals for the current Vehicle/Fuel
                    totals = ['100.00%']*len(F_Types)
                    print('Total\t'+ '\t'.join(totals), file=outfile)
            
        # print the end of file
        print('''****************************''', file=outfile)

if __name__ == '__main__':
    import os
    import sys
    
    # add current running path in the searching path
    srcpath = os.path.dirname(os.path.realpath(sys.argv[0]))
    sys.path.append(srcpath)
    
    jsonFileName = os.path.join(srcpath, 'config', 'VehicleDistributionClasses', 'FleetDistribution.json')
    outTxtFileName = os.path.join(srcpath, 'v_fleet_distribution.txt')
    
    jsonToTxt(jsonFileName, outTxtFileName)        
