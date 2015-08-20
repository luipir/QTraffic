# -*- coding: utf-8 -*-
"""
/***************************************************************************
    A QGIS plugin for Road contamination modelling for EMSURE Project
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

import subprocess
import time
import traceback
import platform
import os
import shutil

from PyQt4 import QtCore, QtGui

from qgis.utils import iface
from qgis.core import (QgsMessageLog,
                       QgsField)
from qgis.gui import (QgsMessageBar)

import newfuel_functions_utils
import fleet_distribution_utils
import traffic_volume_utils
from time import sleep

class Algorithm(QtCore.QObject):
    ''' Class that hide:
    A) algorithm run
    B) running context prepare
    C) result preparation
    '''
    started = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(int)
    message = QtCore.pyqtSignal(str, int)
    error = QtCore.pyqtSignal(Exception, basestring)
    finished = QtCore.pyqtSignal(object)
    
    def __init__(self):
        ''' constructor '''
        super(Algorithm, self).__init__()
        
        self.layer = None
        self.outLayer = None
        self.project = None
        self.projectPath = None
        self.fleetDistributionJsonFileName = None
        self.algFleetDistributionFileName = None
        self.newFuelFormulaJsonFile = None
        self.algNewFuelFormulasFileName = None
        self.algOutputFileName = None
        
        self.killed = False
 
    def run(self):
        ''' QTraffic executable runner '''
        self.started.emit()
        
        sleep(2)
        
        # get algorithm executable
        srcpath = os.path.dirname(os.path.realpath(__file__))        
        defaultExecutableLocation = os.path.join(srcpath, 'algorithm', 'QTraffic.exe')
        executable = self.project.value('Processing/Executable', defaultExecutableLocation)
        
        success = False
        try:
            if platform.system() == 'Linux':
                command = ['wine', executable]
            if platform.system() == 'Windows':
                command = [executable]
            
            strCommand = ' '.join(command)
            msg = self.tr('Executing command {}'.format(strCommand))
            #QgsMessageLog.logMessage(message, 'QTraffic', QgsMessageLog.INFO)
            self.message.emit(msg, QgsMessageLog.INFO)
            
            proc = subprocess.Popen(command,
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    cwd=self.projectPath)
            self.progress.emit(-1)
            for line in iter(proc.stdout.readline, ''):
                if self.killed:
                    break
                
                #QgsMessageLog.logMessage(line, 'QTraffic', QgsMessageLog.INFO)
                self.message.emit(line, QgsMessageLog.INFO)
                
                # check the end of processing controlling the final keyword... seems
                # that subprocess.popen.returncode return always None when run with Wine
                if "END OF CALCULATION" in line:
                    success = True
            
        except Exception as ex:
            self.error.emit(ex, traceback.format_exc())
        
        # resturn true or false
        self.finished.emit(success)
                
    def setProject(self, project=None):
        ''' setting the project on which the algorithm would be run
        '''
        self.project = project
        if self.project:
            # set some globals
            confFileName = self.project.fileName()
            self.projectPath = os.path.dirname(confFileName)
    
    def setLayer(self, layer):
        ''' set the layer from wich extract traffic count data
        '''
        self.layer = layer
    
    def initConfig(self):
        ''' set some configuration params basing on project
        '''
        # origin for fleet distribution json
        self.fleetDistributionJsonFileName = self.project.value('FleetComposition/fleetComposition', 'FleetDistribution.json')
        if not os.path.isabs(self.fleetDistributionJsonFileName):
            self.fleetDistributionJsonFileName = os.path.join(self.projectPath, self.fleetDistributionJsonFileName)
        
        # converted fleet distribuition filename to feed the algorithm
        self.algFleetDistributionFileName = self.project.value('General.InputFileDefinition/FleetDistribution', 'v_fleet_distribution.txt')
        if not os.path.isabs(self.algFleetDistributionFileName):
            self.algFleetDistributionFileName = os.path.join(self.projectPath, self.algFleetDistributionFileName)
            
        # get origin NewFuel formula json filename
        self.newFuelFormulaJsonFile = self.project.value('FuelProperties/FormulasConfig', 'NewFuelFormulas.json')
        if not os.path.isabs(self.newFuelFormulaJsonFile):
            self.newFuelFormulaJsonFile = os.path.join(self.projectPath, self.newFuelFormulaJsonFile)
        
        # converted NewFuel formula filename to feed the algorithm
        self.algNewFuelFormulasFileName = self.project.value('General.InputFileDefinition/Formulas', 'newfuel_formulas.txt')
        if not os.path.isabs(self.algNewFuelFormulasFileName):
            self.algNewFuelFormulasFileName = os.path.join(self.projectPath, self.algNewFuelFormulasFileName)
        
        # get algorithm executable
        srcpath = os.path.dirname(os.path.realpath(__file__))        
        defaultExecutableLocation = os.path.join(srcpath, 'algorithm', 'QTraffic.exe')
        self.executable = self.project.value('Processing/Executable', defaultExecutableLocation)
        
        # get outptu fiel of the algorith
        self.algOutputFileName = self.project.value('Processing.OutputFileDefinition/Emissions', 'output.txt')
        if not os.path.isabs(self.algOutputFileName):
            self.algOutputFileName = os.path.join(self.projectPath, self.algOutputFileName)
        
        # check configuration
        if not self.executable:
            raise Exception(self.tr("No QTraffic executable specified"))
        if not self.layer:
            raise Exception(self.tr("No layer specified"))
        if not self.project:
            raise Exception(self.tr("No project specified"))
        if not self.fleetDistributionJsonFileName:
            raise Exception(self.tr("No fleet disitrbution configruration file specified"))
        if not self.algFleetDistributionFileName:
            raise Exception(self.tr("No fleet distribution filename specified for algorithm input"))
        if not self.newFuelFormulaJsonFile:
            raise Exception(self.tr("No formula configuration json file name specified"))
        if not self.algNewFuelFormulasFileName:
            raise Exception(self.tr("No formula configuration file name specified for algorithm input"))
        if not self.algOutputFileName:
            raise Exception(self.tr("No alg output file name specified"))

    def prepareRun(self):
        ''' prepare running context starting from project
        '''
        # generate v_traffic.txt
        traffic_volume_utils.layerToVolumeTxt(self.layer, self.project)
        
        # generate newfuel_formulas.txt
        newfuel_functions_utils.jsonToTxt(self.newFuelFormulaJsonFile, self.algNewFuelFormulasFileName, self.fleetDistributionJsonFileName)
        
        # generate v_fleet_distribution.txt
        fleet_distribution_utils.jsonToTxt(self.fleetDistributionJsonFileName, self.algFleetDistributionFileName)
        
        # copy project to the fixed control file fopr the algorithm
        currentProjectFile =  self.project.fileName() 
        algProjectFileName =  os.path.join( self.projectPath, 'InputControl.cfg' )
        try:
            os.remove( algProjectFileName )
        except:
            pass
        shutil.copyfile(currentProjectFile, algProjectFileName)
    
    def addResultToLayer(self, newOutputLayer):
        ''' prepare results to be integrated in gis context
        '''
        try:
            # start editing
            newOutputLayer.startEditing()
            
            # read the out file and for each line update relative record in the result
            with open(self.algOutputFileName, 'r') as algOutputFile:
                
                # read all lines
                managedHeader = False
                fieldNameIndexMap = {}
                fieldNames = None
                for line in algOutputFile:
                    line = line.strip()
                    
                    # manage header
                    if not managedHeader:
                        managedHeader = True
                        
                        # add columns to the output layer
                        fieldNames = line.split('\t')
                        fieldNames = [x.split('(')[0] for x in fieldNames]
                        for fieldName in fieldNames:
                            # check if field is already available
                            if newOutputLayer.fieldNameIndex(fieldName) >= 0:
                                continue
                            
                            # add the new field
                            newField = QgsField(fieldName, QtCore.QVariant.Double)
                            newField.setLength(7)
                            newField.setPrecision(5)
                            added = newOutputLayer.addAttribute(newField)
                            if not added:
                               raise Exception(self.tr('Can not add fieldname {} to the output vector'.format(fieldName))) 
                            
                        newOutputLayer.updateFields()
                        
                        # add the fieldName in fieldNames
                        for fieldName in fieldNames:
                            fieldNameIndexMap[ fieldName ] = newOutputLayer.fieldNameIndex(fieldName)
                        
                        # jump to the next line = values
                        continue
                        
                    # map values with fieldnames
                    values = line.split('\t')
                    fieldValueMap = zip(fieldNames, values)
                    
                    # update record
                    id = None
                    for columnIndex, (fieldName, fieldValue) in enumerate(fieldValueMap):
                        
                        if columnIndex == 0:
                            id = int(fieldValue)
                            continue
                        
                        fieldValue = float(fieldValue)
                        newOutputLayer.changeAttributeValue(id-1, fieldNameIndexMap[fieldName], fieldValue)
            
        except Exception as ex:
            # rollback
            newOutputLayer.rollBack()
            
            traceback.print_exc()
            QgsMessageLog.logMessage(str(ex), 'QTraffic', QgsMessageLog.CRITICAL)
            iface.messageBar().pushCritical('QTraffic', self.tr("Error formatting alg result in the output layer"))
        
        else:
            if not newOutputLayer.commitChanges():
                raise Exception(self.tr('Error committing changes in the result layer'))
        
    
    def kill(self):
        self.killed = True
    
    def tr(self, string, context=''):
        if not context:
            context = 'QTraffic'
        return QtCore.QCoreApplication.translate(context, string)

    