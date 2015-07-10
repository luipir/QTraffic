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

from PyQt4 import QtCore, QtGui

from qgis.utils import iface
from qgis.core import (QgsMessageLog)
from qgis.gui import (QgsMessageBar)

import newfuel_functions_utils
import fleet_distribution_utils
import traffic_volume_utils

class Algorithm:
    ''' Class that hide:
    A) algorithm runner
    B) running context prepare
    C) result preparation
    '''
    def __init__(self):
        ''' constructor '''
        self.layer = None
        self.project = None
        self.projectPath = None
        self.fleetDistributionJsonFileName = None
        self.algFleetDistributionFileName = None
        self.newFuelFormulaJsonFile = None
        self.algNewFuelFormulasFileName = None
 
    def run(self):
        ''' QTraffic executable runner '''
        # create message bar to show progress
        progressMessageBar = iface.messageBar().createMessage(self.tr('Executing {}'.format(self.executable)))
        progress = QtGui.QProgressBar()
        progress.setMaximum(10)
        progress.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        progressMessageBar.layout().addWidget(progress)
        iface.messageBar().pushWidget(progressMessageBar, QgsMessageBar.INFO)
        
        success = False
        try:
            if platform.system() == 'Linux':
                command = ['wine', self.executable]
            if platform.system() == 'Windows':
                command = [self.executable]
            
            print(command)
            
            proc = subprocess.Popen(command,
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    cwd=self.projectPath)
            counter = 0
            for line in iter(proc.stdout.readline, ''):
                QgsMessageLog.logMessage(line, 'QTraffic', QgsMessageLog.INFO)
                print(line)
                progress.setValue(counter)
                counter += 1
                
                # check the end of processing controlling the final keyword... seems
                # that subprocess.popen.returncode return always None when run with Wine
                if "END OF CALCULATION" in line:
                    success = True
            
        except Exception as ex:
            traceback.print_exc()
            QgsMessageLog.logMessage(str(ex), 'QTraffic', QgsMessageLog.CRITICAL)
            iface.messageBar().pushCritical('QTraffic', "Error executing algorithm")
        else:
            iface.messageBar().popWidget()
            if success:
                iface.messageBar().pushSuccess('QTraffic', 'Alg terminated successfully', 10)            
            else:
                QgsMessageLog.logMessage('Failed execution', 'QTraffic', QgsMessageLog.CRITICAL)
                iface.messageBar().pushCritical('QTraffic', "Error executing algorithm")
                
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
    
    def init(self):
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

        # check configuration
        if not self.executable:
            raise Exception("No QTraffic executable specified")
        if not self.layer:
            raise Exception("No layer specified")
        if not self.project:
            raise Exception("No project specified")
        if not self.fleetDistributionJsonFileName:
            raise Exception("No fleet disitrbution configruration file specified")
        if not self.algFleetDistributionFileName:
            raise Exception("No fleet distribution filename specified for algorithm input")
        if not self.newFuelFormulaJsonFile:
            raise Exception("No formula configuration json file name specified")
        if not self.algNewFuelFormulasFileName:
            raise Exception("No formula configuration file name specified for algorithm input")

    def prepareRun(self):
        ''' prepare running context starting from project
        '''
        # generate v_traffic.txt
        traffic_volume_utils.layerToVolumeTxt(self.layer, self.project)
        
        # generate newfuel_formulas.txt
        newfuel_functions_utils.jsonToTxt(self.newFuelFormulaJsonFile, self.algNewFuelFormulasFileName, self.fleetDistributionJsonFileName)
        
        # generate v_fleet_distribution.txt
        fleet_distribution_utils.jsonToTxt(self.fleetDistributionJsonFileName, self.algFleetDistributionFileName)        
    
    def prepareResult(self):
        ''' prepare results to be integrated in gis context
        '''
        pass
    
    def tr(self, string, context=''):
        if not context:
            context = 'QTraffic'
        return QtCore.QCoreApplication.translate(context, string)

    