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
file. in the format of NewFuelFormulas.json in the Sequencial and
positional file format as in newfuel_formulas.txt.
Because of format exception has been difficult to create modular code and this
created a really low quality code with a high probability to be modified every
time organization of the v_fleet_distribution change of a different kind of
original fleet distribution json change because change the the domain of the
problem.
I tried to convince to use more robust format about but I wasn't able, so 
this is the result of the adaptation. 
So reader, please don't shame me about the quality of this code!
'''
#############################################################################

import json
import collections

euroKeyConvert = {
    'PRE EURO':'Euro0',
    'CONVENTIONAL':'Euro0',
    'EURO 1':'Euro1',
    'EURO 2':'Euro2',
    'EURO 3':'Euro3',
    'EURO 4':'Euro4',
    'EURO 5':'Euro5',
    'EURO 6':'Euro6',
}

def getKCodes(fleetDistributionDict, vehicleType, euroClassName):
    ''' recover Kcode from FleetDistribution.json default class
    '''
    vehicleList = fleetDistributionDict['children'][0]['children']
    
    # look for vehicle
    for vehicle in vehicleList:
        
        if vehicle['name'] == vehicleType:
            
            # look for New Fuel class
            for fuel in vehicle['children']:
                
                if fuel['name'] == 'New fuel':
                    
                    # look for the euro class
                    for euroClass in fuel['children']:
                        
                        if euroClass['name'] == euroClassName:
                            
                            if len(euroClass['children']) == 0:
                                return ['----']
                            else:
                                kCodes = []
                                for euroSubClass in euroClass['children']:
                                    kCodes.append( euroSubClass['converted'] )
                                
                                return kCodes
    return ['----']

def jsonToTxt(jsonFileName, outTxtFileName, fleetDistributionFileName):
    ''' convert from new fuel functions json to txt format necessary for the algorithm
    '''
    # open and read the json file
    with open(jsonFileName) as jsonFile:
        jsonData = json.load(jsonFile, object_pairs_hook=collections.OrderedDict)
    
    # open and read the fleet distribution json file
    with open(fleetDistributionFileName) as fleetDistributionJsonFile:
        fleetDistributionDict = json.load(fleetDistributionJsonFile, object_pairs_hook=collections.OrderedDict)
    
    with open(outTxtFileName, 'w') as outfile:
        # CATEGORY    EURO_CLASS     CAPACITY_CLASS     POLLUTANT    Formula
        print('CATEGORY\tEURO_CLASS\tCAPACITY_CLASS\tPOLLUTANT\tFormula', file=outfile)
        
        # get list of available pollutants
        # assume that the list of pollutants is the same for each vechicle and euroclass
        pollutantDict = jsonData.values()[0]['New fuel'].values()[0]
        
        # write the entry followinf pollutant order, then vehicle and then euro class
        for pollutant in pollutantDict.keys():
            
            # for each vehicleType
            for vehicleType, vehicleData in jsonData.items():
                
                vehicleTypeName = vehicleData['name']
                euroClasses = vehicleData['New fuel']
                
                # for each euro class
                for euroClass, pollutants in euroClasses.items():
                    
                    # get k code
                    kCodes = getKCodes(fleetDistributionDict, vehicleType, euroClass)
                    formula = pollutants[ pollutant ]
                    
                    # write the line, as many as kcodes encontered
                    for kCode in kCodes:
                        values = [ vehicleTypeName, euroKeyConvert[euroClass], kCode, pollutant, formula ]
                        print( '\t'.join(values), file=outfile)

if __name__ == '__main__':
    import os
    import sys
    
    # add current running path in the searching path
    srcpath = os.path.dirname(os.path.realpath(sys.argv[0]))
    sys.path.append(srcpath)
    
    jsonFileName = os.path.join(srcpath, 'config', 'NewFuelFormulas.json')
    outTxtFileName = os.path.join(srcpath, 'newfuel_formulas.txt')
    fleetDistributionFileName = os.path.join(srcpath, 'config', 'VehicleDistributionClasses', 'FleetDistribution.json')
    
    jsonToTxt(jsonFileName, outTxtFileName, fleetDistributionFileName)        
