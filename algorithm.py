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

from qgis.utils import iface
from qgis.core import (QgsMessageLog,
                       QgsErrorMessage)

import newfuel_functions_utils
import fleet_distribution_utils
import traffic_volume_utils

class Algorithm():
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
#         # get actual work dir
#         oldCwd = os.getcwd()
#         
#         # set work dir 
#         os.chdir(self.projectPath)
        
        # create message bar to show progress
        iface.messageBar().createMessage(self.tr('Executing {}'.format(self.executable)))
        self.progress = QProgressBar()
        self.progress.setMaximum(10)
        self.progress.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.progressMessageBar.layout().addWidget(self.progress)
        iface.messageBar().pushWidget(self.progressMessageBar,
                                      iface.messageBar().INFO)
        
        try:
            command = [self.executable]
            proc = subprocess.Popen(command,
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    cwd=self.projectPath)
            counter = 0
            for line in iter(proc.stdout.readline, ''):
                QgsMessageLog.logMessage(line, 'QTraffic', QgsMessageLog.INFO)
                print(line)
                progress.setPercentage(counter)
                counter += 1
        except Exception as ex:
            traceback.print_exc()
            QgsMessageLog.logMessage(str(ex), 'QTraffic', QgsMessageLog.CRITICAL)
            iface.messageBar().pushCritical('QTraffic', "Error executing algorithm")
        finally:
#             os.chdir(oldCwd)
            iface.messageBar().popWidget()
            iface.messageBar().pushSuccess('QTraffic', 'Alg terminated successfully')            
    
    def setProject(self, project=None):
        ''' setting the project on which the algorithm would be run
        '''
        self.project = project
        if self.project:
            # set some globals
            confFileName = self.project.fileName()
            self.projectPath = os.path.dirname(confFileName)
            
            # emit configurationLoaded with the status of loading
            self.init()
    
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
        self.newFuelFormulaJsonFile = self.project.value('FuelProperties/Formulas', 'NewFuelFormulas.json')
        if not os.path.isabs(self.newFuelFormulaJsonFile):
            self.newFuelFormulaJsonFile = os.path.join(self.projectPath, self.newFuelFormulaJsonFile)
        
        # converted NewFuel formula filename to feed the algorithm
        self.algNewFuelFormulasFileName = self.project.value('General.InputFileDefinition/Formulas', 'newfuel_formulas.txt')
        if not os.path.isabs(self.algNewFuelFormulasFileName):
            self.algNewFuelFormulasFileName = os.path.join(self.projectPath, self.algNewFuelFormulasFileName)
        
        # get algorithm executable
        self.executable = self.project.value('Processing/Executable', 'QTraffic.exe')

        # check configuration
        if not self.executable:
            rais Exception("No QTraffic executable specified")
        if not self.layer:
            rais Exception("No layer specified")
        if not self.project:
            rais Exception("No project specified")
        if not self.fleetDistributionJsonFileName:
            rais Exception("No fleet disitrbution configruration file specified")
        if not self.algFleetDistributionFileName:
            rais Exception("No fleet distribution filename specified for algorithm input")
        if not self.newFuelFormulaJsonFile:
            rais Exception("No formula configuration json file name specified")
        if not self.algNewFuelFormulasFileName:
            rais Exception("No formula configuration file name specified for algorithm input")

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
        return QCoreApplication.translate(context, string)

    