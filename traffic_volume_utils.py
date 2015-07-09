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

from qgis.core import (QgsFeatureRequest,
                       QgsVectorLayer)
from PyQt4 import QtCore

def layerToVolumeTxt(layer, project):
    ''' extract layer column to have only traffic count for the algoritm
    This utility is intended to generate v_traffic.txt
    Column of the layer are get from the project. If a column is not specified
    it will filled with 0 value
    '''
    # get out filename 
    confFileName = project.fileName()
    projectPath = os.path.dirname(confFileName)

    outFileName = project.value('General.InputFileDefinition/TrafficVolume', '')
    if not outFileName:
        raise Exception('No General.InputFileDefinition/TrafficVolume filename has bee specified')
    
    if not os.path.isabs( outFileName ):
        outFileName = os.path.join(projectPath, outFileName)
    
    # get columns to estract
    columnRoadType = project.value('InputNetwork/columnRoadType', '')
    columnRoadLenght = project.value('InputNetwork/columnRoadLenght', '')
    columnRoadSlope = project.value('InputNetwork/columnRoadSlope', '')
    
    columnPassengerCars = project.value('VehicleCountSpeed/columnPassengerCars', '')
    columnLightDutyVehicle = project.value('VehicleCountSpeed/columnLightDutyVehicle', '')
    columnHeavyDutyVechicle = project.value('VehicleCountSpeed/columnHeavyDutyVechicle', '')
    columnUrbanBuses = project.value('VehicleCountSpeed/columnUrbanBuses', '')
    columnMotorcycle = project.value('VehicleCountSpeed/columnMotorcycle', '')
    columnCouch = project.value('VehicleCountSpeed/columnCouch', '')
    columnAverageSpeed = project.value('VehicleCountSpeed/columnAverageSpeed', '')
    
    fields = ['id', 
               columnRoadType, 
               columnPassengerCars, 
               columnLightDutyVehicle, 
               columnHeavyDutyVechicle, 
               columnUrbanBuses,
               columnCouch,
               columnMotorcycle,
               columnAverageSpeed,
               columnRoadLenght,
               columnRoadSlope
               ]
    # create out file
    with open(outFileName, 'w') as outFile:
        
        # print header
        template = '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.5f}\t{:.5f}'
        header = 'ID\tTYPE\tPC\tLDV\tHDV\tBUS\tCOACHES\tMOTO\tSPEED\tLENGHT\tGRAD'
        print(header, file=outFile)
        
        # get all records
        fieldsToRetrieve = [x for x in fields if x] # remove not requested fields
        request = QgsFeatureRequest()
        request.setSubsetOfAttributes(fieldsToRetrieve, layer.pendingFields())
        request.setFlags( request.flags() | QgsFeatureRequest.NoGeometry)
        
        for feature in layer.getFeatures( request ):
            values = []
            for field in fields:
                value = 0 # defauklt value in case the column is not present or not requested
                try:
                    value = feature.attribute(field)
                except:
                    pass
                values.append( value )
             
            # then print feature
            print(template.format(*values), file=outFile)
    
if __name__ == '__main__':
    import os
    import sys
    import json
    from qgis.core import (QgsApplication)
    
    # add current running path in the searching path
    srcpath = os.path.dirname(os.path.realpath(sys.argv[0]))
    sys.path.append(srcpath)
    
    try:
        # init qgis env and application
        app = QgsApplication(sys.argv, True)    
        QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX'], True)
        QgsApplication.initQgis()
    
        # run application
        projectFileName = os.path.join(srcpath, 'testdata', 'TestProject', 'TestProject.cfg')
        project = QtCore.QSettings(projectFileName, QtCore.QSettings.IniFormat)
        
        layerPath = os.path.join(srcpath, 'testdata', 'shape', 'roadlinks.shp')
        layer = QgsVectorLayer(layerPath, 'layer', 'ogr')
        
        layerToVolumeTxt(layer, project)
     
    finally:
        QgsApplication.exitQgis()
    
