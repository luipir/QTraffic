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

import os
import traceback
from PyQt4 import QtCore, QtGui
from qgis.core import (QgsMessageLog,
                       QgsErrorMessage)
from qgis.gui import (QgsMessageBar)

class OutputTabManager(QtCore.QObject):
    ''' Class to hide managing of relative tab
    '''
    projectModified = QtCore.pyqtSignal()
        
    def __init__(self, parent=None):
        '''constructor'''
        super(OutputTabManager, self).__init__(parent)

        # parent is the dock widget with all graphical elements
        self.gui = parent
        self.plugin = parent.parent
        
        # init some globals
        self.applicationPath = os.path.dirname(os.path.realpath(__file__))
        self.project = None
        self.projectPath = None
        
        # retrieve the current tab index
        self.initTabTabIndex()
        
        # disable tab at the beginning
        self.gui.tabWidget.setTabEnabled(self.tabIndex, False)
        
        # add some gui events
        self.gui.createNewLayer_RButton.toggled.connect(self.setInputLayer)
        self.gui.selectOutfile_TButton.clicked.connect(self.selectNewOutFile)
        self.gui.calculate_PButton.clicked.connect(self.calculate)
        
    def initTabTabIndex(self):
        ''' Retrieve what tab index refer the current tab manager
        '''
        for tabIndex in range(self.gui.tabWidget.count()):
            if self.gui.tabWidget.tabText(tabIndex) == "Output":
                self.tabIndex = tabIndex
    
    def setProject(self, project=None):
        ''' setting the new project on which the tab is based
        '''
        self.project = project
        if self.project:
            # set some globals
            confFileName = self.project.fileName()
            self.projectPath = os.path.dirname(confFileName)
            
            # emit configurationLoaded with the status of loading
            self.setTabGUIBasingOnProject()
            
            # enable current tab because project has been loaded
            self.gui.tabWidget.setTabEnabled(self.tabIndex, True)
        
        else:
            # disable current tab because no project has been loaded yet
            self.gui.tabWidget.setTabEnabled(self.tabIndex, False)
    
    def selectNewOutFile(self):
        ''' Select the the file
        '''
        oldOutputLayer = self.gui.outFile_LEdit.text()
        
        # get last conf to start from its path
        startPath = self.projectPath
        newOutputLayer = self.project.value('Processing.OutputFileDefinition/newOutputLayer', '')
        if newOutputLayer:
            startPath = os.path.dirname( newOutputLayer )
        
        # ask for the new out file
        newOutputLayer = QtGui.QFileDialog.getSaveFileName(self.gui, "Select an autput file", startPath, 
                                                        self.plugin.tr("All (*)"))
        if not newOutputLayer:
            return
        
        if oldOutputLayer == newOutputLayer:
            return
        
        # update gui
        self.gui.outFile_LEdit.setText(newOutputLayer)
        
        self.saveTabOnProject()

    def setInputLayer(self):
        ''' Set GUI basing on toggled ComboBox to set if the layer is the input one 
        or have to select a new one 
        '''
        self.gui.outFile_LEdit.setEnabled( self.gui.createNewLayer_RButton.isChecked() )
        self.gui.selectOutfile_TButton.setEnabled( self.gui.createNewLayer_RButton.isChecked() )
            
    def setTabGUIBasingOnProject(self):
        '''Set tab basing on project conf
        '''
        if not self.project:
            return
        
        # get conf parameters
        addToInputLayer = self.project.value('Processing.OutputFileDefinition/addToInputLayer', False, bool)
        newOutputLayer = self.project.value('Processing.OutputFileDefinition/newOutputLayer', '')

        Gasoline_Consumption = self.project.value('Processing.Parameters/Gasoline_Consumption', False, bool)
        Diesel_Consumption = self.project.value('Processing.Parameters/Diesel_Consumption', False, bool)
        LPG_Consumption = self.project.value('Processing.ParameLPG_Consumptionn_LPG', False, bool)
        NewFuel_Consumption = self.project.value('Processing.Parameters/NewFuel_Consumption', False, bool)
        Fuel_Consumption_Total = self.project.value('Processing.Parameters/Fuel_Consumption_Total', False, bool)
        Energy_Consumption = self.project.value('Processing.Parameters/Energy_Consumption', False, bool)
        
        CO = self.project.value('Processing.Parameters/CO', False, bool)
        NOx = self.project.value('Processing.Parameters/NOx', False, bool)
        NMVOC = self.project.value('Processing.Parameters/NMVOC', False, bool)
        CO2 = self.project.value('Processing.Parameters/CO2', False, bool)
        CH4 = self.project.value('Processing.Parameters/CH4', False, bool)
        N2O = self.project.value('Processing.Parameters/N2O', False, bool)
        NH3 = self.project.value('Processing.Parameters/NH3', False, bool)
        SO2 = self.project.value('Processing.Parameters/SO2', False, bool)
        PM25 = self.project.value('Processing.Parameters/PM', False, bool)
        C6H6 = self.project.value('Processing.Parameters/C6H6', False, bool)
        
        # avoid emitting signal in case of reset of indexes
        try:
            # to avoid add multiple listener, remove previous listener
            self.gui.addToOriginaLayer_RButton.toggled.disconnect(self.saveTabOnProject)
            self.gui.createNewLayer_RButton.toggled.disconnect(self.saveTabOnProject)
            self.gui.outFile_LEdit.returnPressed.disconnect(self.saveTabOnProject)

            self.gui.fuelEnergyConsumptionGasoline_CBox.clicked.disconnect(self.saveTabOnProject)
            self.gui.fuelEnergyConsumptionDiesel_CBox.clicked.disconnect(self.saveTabOnProject)
            self.gui.fuelEnergyConsumptionLPG_CBox.clicked.disconnect(self.saveTabOnProject)
            self.gui.fuelEnergyConsumptionNewFuels_CBox.clicked.disconnect(self.saveTabOnProject)
            self.gui.totalFuelConsumption_CBox.clicked.disconnect(self.saveTabOnProject)
            self.gui.energyConsumption_CBox.clicked.disconnect(self.saveTabOnProject)

            self.gui.pollutantsCO_CBox.clicked.disconnect(self.saveTabOnProject)
            self.gui.pollutantsNOx_CBox.clicked.disconnect(self.saveTabOnProject)
            self.gui.pollutantsNMVOCs_CBox.clicked.disconnect(self.saveTabOnProject)
            self.gui.pollutantsCO2_CBox.clicked.disconnect(self.saveTabOnProject)
            self.gui.pollutantsCH4_CBox.clicked.disconnect(self.saveTabOnProject)
            self.gui.pollutantsN2O_CBox.clicked.disconnect(self.saveTabOnProject)
            self.gui.pollutantsNH3_CBox.clicked.disconnect(self.saveTabOnProject)
            self.gui.pollutantsSO2_CBox.clicked.disconnect(self.saveTabOnProject)
            self.gui.pollutantsPM25_CBox.clicked.disconnect(self.saveTabOnProject)
            self.gui.pollutantsC6H6_CBox.clicked.disconnect(self.saveTabOnProject)
        except (Exception) as ex:
            pass
        
        # now populate interface
        self.gui.addToOriginaLayer_RButton.setChecked( addToInputLayer )
        self.gui.createNewLayer_RButton.setChecked( not addToInputLayer )
        self.gui.outFile_LEdit.setText( newOutputLayer )

        self.gui.fuelEnergyConsumptionGasoline_CBox.setChecked( Gasoline_Consumption )
        self.gui.fuelEnergyConsumptionDiesel_CBox.setChecked( Diesel_Consumption )
        self.gui.fuelEnergyConsumptionLPG_CBox.setChecked( LPG_Consumption )
        self.gui.fuelEnergyConsumptionNewFuels_CBox.setChecked( NewFuel_Consumption )
        self.gui.totalFuelConsumption_CBox.setChecked( Fuel_Consumption_Total )
        self.gui.energyConsumption_CBox.setChecked( Energy_Consumption )

        self.gui.pollutantsCO_CBox.setChecked( CO )
        self.gui.pollutantsNOx_CBox.setChecked( NOx )
        self.gui.pollutantsNMVOCs_CBox.setChecked( NMVOC )
        self.gui.pollutantsCO2_CBox.setChecked( CO2 )
        self.gui.pollutantsCH4_CBox.setChecked( CH4 )
        self.gui.pollutantsN2O_CBox.setChecked( N2O )
        self.gui.pollutantsNH3_CBox.setChecked( NH3 )
        self.gui.pollutantsSO2_CBox.setChecked( SO2 )
        self.gui.pollutantsPM25_CBox.setChecked( PM25 )
        self.gui.pollutantsC6H6_CBox.setChecked( C6H6 )
        
        # add all modification events to notify project modification
        self.gui.addToOriginaLayer_RButton.toggled.connect(self.saveTabOnProject)
        self.gui.createNewLayer_RButton.toggled.connect(self.saveTabOnProject)
        self.gui.outFile_LEdit.returnPressed.connect(self.saveTabOnProject)

        self.gui.fuelEnergyConsumptionGasoline_CBox.clicked.connect(self.saveTabOnProject)
        self.gui.fuelEnergyConsumptionDiesel_CBox.clicked.connect(self.saveTabOnProject)
        self.gui.fuelEnergyConsumptionLPG_CBox.clicked.connect(self.saveTabOnProject)
        self.gui.fuelEnergyConsumptionNewFuels_CBox.clicked.connect(self.saveTabOnProject)
        self.gui.totalFuelConsumption_CBox.clicked.connect(self.saveTabOnProject)
        self.gui.energyConsumption_CBox.clicked.connect(self.saveTabOnProject)

        self.gui.pollutantsCO_CBox.clicked.connect(self.saveTabOnProject)
        self.gui.pollutantsNOx_CBox.clicked.connect(self.saveTabOnProject)
        self.gui.pollutantsNMVOCs_CBox.clicked.connect(self.saveTabOnProject)
        self.gui.pollutantsCO2_CBox.clicked.connect(self.saveTabOnProject)
        self.gui.pollutantsCH4_CBox.clicked.connect(self.saveTabOnProject)
        self.gui.pollutantsN2O_CBox.clicked.connect(self.saveTabOnProject)
        self.gui.pollutantsNH3_CBox.clicked.connect(self.saveTabOnProject)
        self.gui.pollutantsSO2_CBox.clicked.connect(self.saveTabOnProject)
        self.gui.pollutantsPM25_CBox.clicked.connect(self.saveTabOnProject)
        self.gui.pollutantsC6H6_CBox.clicked.connect(self.saveTabOnProject)
    
    def saveTabOnProject(self):
        ''' Save tab configuration in the project basing on GUI values
        '''
        # get values from the GUI
        addToInputLayer = self.gui.addToOriginaLayer_RButton.isChecked()
        newOutputLayer = self.gui.outFile_LEdit.text()

        Gasoline_Consumption = self.gui.fuelEnergyConsumptionGasoline_CBox.isChecked()
        Diesel_Consumption = self.gui.fuelEnergyConsumptionDiesel_CBox.isChecked()
        LPG_Consumption = self.gui.fuelEnergyConsumptionLPG_CBox.isChecked()
        NewFuel_Consumption = self.gui.fuelEnergyConsumptionNewFuels_CBox.isChecked()
        Fuel_Consumption_Total = self.gui.totalFuelConsumption_CBox.isChecked()
        Energy_Consumption = self.gui.energyConsumption_CBox.isChecked()
        
        CO = self.gui.pollutantsCO_CBox.isChecked()
        NOx = self.gui.pollutantsNOx_CBox.isChecked()
        NMVOC = self.gui.pollutantsNMVOCs_CBox.isChecked()
        CO2 = self.gui.pollutantsCO2_CBox.isChecked()
        CH4 = self.gui.pollutantsCH4_CBox.isChecked()
        N2O = self.gui.pollutantsN2O_CBox.isChecked()
        NH3 = self.gui.pollutantsNH3_CBox.isChecked()
        SO2 = self.gui.pollutantsSO2_CBox.isChecked()
        PM25 = self.gui.pollutantsPM25_CBox.isChecked()
        C6H6 = self.gui.pollutantsC6H6_CBox.isChecked()
        
        # set conf parameters
        self.project.setValue('Processing.OutputFileDefinition/addToInputLayer', addToInputLayer)
        self.project.setValue('Processing.OutputFileDefinition/newOutputLayer', newOutputLayer)
        
        self.project.setValue('Processing.Parameters/Gasoline_Consumption', Gasoline_Consumption)
        self.project.setValue('Processing.Parameters/Diesel_Consumption', Diesel_Consumption)
        self.project.setValue('Processing.Parameters/LPG_Consumption', LPG_Consumption)
        self.project.setValue('Processing.Parameters/NewFuel_Consumption', NewFuel_Consumption)
        self.project.setValue('Processing.Parameters/Fuel_Consumption_Total', Fuel_Consumption_Total)
        self.project.setValue('Processing.Parameters/Energy_Consumption', Energy_Consumption)
        
        self.project.setValue('Processing.Parameters/CO', CO)
        self.project.setValue('Processing.Parameters/NOx', NOx)
        self.project.setValue('Processing.Parameters/NMVOC', NMVOC)
        self.project.setValue('Processing.Parameters/CO2', CO2)
        self.project.setValue('Processing.Parameters/CH4', CH4)
        self.project.setValue('Processing.Parameters/N2O', N2O)
        self.project.setValue('Processing.Parameters/NH3', NH3)
        self.project.setValue('Processing.Parameters/SO2', SO2)
        self.project.setValue('Processing.Parameters/PM', PM25)
        self.project.setValue('Processing.Parameters/C6H6', C6H6)
            
        # notify project modification
        self.projectModified.emit()
    
    def calculate(self):
        ''' Prepare environment to run the alg and run it. After run, merge produced 
        data basing on plugin configuration
        '''
        # prepare environment
        
        # run the alg
        
        # check result
        
        # prepare result
