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
import shutil
from PyQt4 import QtCore, QtGui
from qgis.core import (QgsVectorLayer,
                       QgsMessageLog,
                       QgsErrorMessage)
from qgis.gui import (QgsMessageBar)

class ProjectTabManager(QtCore.QObject):
    ''' Class to hide managing of project load and save
    '''
    tabModified = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        '''constructor'''
        super(ProjectTabManager, self).__init__(parent)

        # parent is the dock widget with all graphical elements
        self.gui = parent
        self.plugin = parent.parent
        
        # init some globals
        self.applicationPath = os.path.dirname(os.path.realpath(__file__))
        self.defaultProject = os.path.join(self.applicationPath, 'config','defaultProject.cfg')
        self.roadLayer = None

        # create listeners to load, save and saveas
#         self.gui.projectName_lineEdit.editingFinished.connect()
        self.gui.selectProject_TButton.clicked.connect(self.loadCreateProject)
#         self.gui.saveAsProject_PButton.clicked.connect()
#         self.gui.saveProject_PButton.clicked.connect()
        
        # set save button disabled
        # the state of the button hide the status of the project
        # if it has been modified or not... no Project class has been created
        # to reduce code overhead du the fact that project is a .ini container
        self.gui.saveProject_PButton.setEnabled(False)
        self.tabModified.connect(self.setProjectModified)
    
    @QtCore.pyqtSlot()
    def setProjectModified(self):
        ''' Set status of project GUI because the project has been modified
            His method is a slot called everytime a gui element has been modified
        '''
        # enable Save button
        self.gui.saveProject_PButton.setEnabled(True)
        
        # set tab text = tab text + '*' to show that project has been modified
        self.gui.tabWidget.setTabText(0, self.gui.tabWidget.tabText(0) + '*')        
    
    def loadCreateProject(self):
        ''' Load or create a new project if the selected project does not exist
        '''
        # check if current project has been modified to 
        # avoid to override modifications
        if self.isModified():
            title = self.plugin.tr("Warning")
            message = self.plugin.tr("Project is modified, if you continue you can overwrite modifications. Continue?")
            ret = QtGui.QMessageBox.question(self.gui, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        # get last conf to start from its path
        settings = QtCore.QSettings()
        lastProjectIni = settings.value('/QTraffic/lastProject', self.defaultProject)
        
        startPath = os.path.abspath( lastProjectIni )
        
        # ask for the new conf file
        projectFile = QtGui.QFileDialog.getOpenFileName(self.gui, "Select a INI project file", startPath, 
                                                        self.plugin.tr("Ini (*.ini);;All (*)"))
        if not projectFile:
            return
        
        # if projectFile does not exist copy template from the default project file
        if not os.path.exists(projectFile):
            shutil.copyfile(self.defaultProject, projectFile)
        
        # set new conf file as default
        settings.setValue('/QTraffic/lastProject', projectFile)
        
        # load projectIni
        self.project = QtCore.QSettings(projectFile, QtCore.QSettings.IniFormat)
        
        # set text of loaded layer
        self.gui.projectName_lineEdit.setText(self.project.fileName())
        
        # set GUI basing on project        
        self.setGuiFromProject()
    
    def setGuiFromProject(self):
        ''' Basing on project configuration set the plugin interface
        '''
        # set gui for each tab
        try:
            # manage input network
            self.manageInputNetwork()
            
            # manage vehicle count/speed
            self.manageVehicleCountSpeed()
            
            # manage fleet composition
            self.manageFleetComposition()
            
            # manage parameters
            
            # output
            
            # manage help
        except (Exception) as ex:
            QgsMessageLog.logMessage(str(ex), self.plugin.pluginTag, QgsMessageLog.CRITICAL)
            self.plugin.iface.messageBar().pushMessage(str(ex), QgsMessageBar.CRITICAL)
            return
    
    def manageInputNetwork(self):
        '''Set tab basing on project conf 
        '''
        # get conf parameters
        inputLayerFile = self.project.value('InputNetwork/inputLayer', '')
        columnRoadType = self.project.value('InputNetwork/columnRoadType', '')
        columnRoadLenght = self.project.value('InputNetwork/columnRoadLenght', '')
        columnRoadSlope = self.project.value('InputNetwork/columnRoadSlope', '')
        
        # if layer exist load it
        if not os.path.exists(inputLayerFile):
            msg = self.plugin.tr('Layer file %s does not exist' % inputLayerFile)
            raise Exception(msg) 
        
        self.roadLayer = QgsVectorLayer(inputLayerFile, 'roadLayer', 'ogr')
        if not self.roadLayer.isValid():
            raise Exception( self.roadLayer.error().message(QgsErrorMessage.Text) )
        
        # set text of loaded layer
        self.gui.inputLayer_lineEdit.setText(self.roadLayer.publicSource())
        
        # now populare combo boxes with layer colums
        fieldNames = sorted([field.name() for field in self.roadLayer.pendingFields().toList()])
        unknownIndex = -1
        
        self.gui.roadType_CBox.addItems(fieldNames)
        self.gui.roadLenght_CBox.addItems(fieldNames)
        self.gui.roadGradient_CBox.addItems(fieldNames)
        
        # select the combobox item as in the project file... if not available then "Please select"
        index = self.gui.roadType_CBox.findText(columnRoadType)
        self.gui.roadType_CBox.setCurrentIndex( index if index > 0 else unknownIndex )
        
        index = self.gui.roadLenght_CBox.findText(columnRoadLenght)
        self.gui.roadLenght_CBox.setCurrentIndex( index if index > 0 else unknownIndex )
        
        index = self.gui.roadGradient_CBox.findText(columnRoadSlope)
        self.gui.roadGradient_CBox.setCurrentIndex( index if index > 0 else unknownIndex )
        
        # add all modification events to notify project modification
        try:
            # to avoid add multiple listener, remove previous listener
            self.gui.inputLayer_lineEdit.editingFinished.disconnect(self.setProjectModified)
            self.gui.roadType_CBox.currentIndexChanged.disconnect(self.setProjectModified)
            self.gui.roadLenght_CBox.currentIndexChanged.disconnect(self.setProjectModified)
            self.gui.roadGradient_CBox.currentIndexChanged.disconnect(self.setProjectModified)
        except (Exception) as ex:
            pass
        
        self.gui.inputLayer_lineEdit.editingFinished.connect(self.setProjectModified)
        self.gui.roadType_CBox.currentIndexChanged.connect(self.setProjectModified)
        self.gui.roadLenght_CBox.currentIndexChanged.connect(self.setProjectModified)
        self.gui.roadGradient_CBox.currentIndexChanged.connect(self.setProjectModified)
    
    def manageVehicleCountSpeed(self):
        '''Set tab basing on project conf 
        '''
        # get parameters fron project
        columnPassengerCars = self.project.value('VehicleCountSpeed/columnPassengerCars', '')
        columnLightDutyVehicle = self.project.value('VehicleCountSpeed/columnLightDutyVehicle', '')
        columnHeavyDutyVechicle = self.project.value('VehicleCountSpeed/columnHeavyDutyVechicle', '')
        columnUrbanBuses = self.project.value('VehicleCountSpeed/columnUrbanBuses', '')
        columnMotorcycle = self.project.value('VehicleCountSpeed/columnMotorcycle', '')
        columnCouch = self.project.value('VehicleCountSpeed/columnCouch', '')
        columnAverageSpeed = self.project.value('VehicleCountSpeed/columnAverageSpeed', '')
        
        # now populare combo boxes with layer colums
        fieldNames = sorted([field.name() for field in self.roadLayer.pendingFields().toList()])
        unknownIndex = -1
        
        self.gui.passengerCarsCount_CBox.addItems(fieldNames)
        self.gui.lightDutyVehicleCount_CBox.addItems(fieldNames)
        self.gui.heavyDutyVehicleCount_CBox.addItems(fieldNames)
        self.gui.urbanBusesCount_CBox.addItems(fieldNames)
        self.gui.coachesCount_CBox.addItems(fieldNames)
        self.gui.motorcycleCount_CBox.addItems(fieldNames)
        self.gui.averageVehicleSpeed_Cbox.addItems(fieldNames)
        
        # select the combobox item as in the project file... if not available then "Please select"
        index = self.gui.passengerCarsCount_CBox.findText(columnPassengerCars)
        self.gui.passengerCarsCount_CBox.setCurrentIndex( index if index > 0 else unknownIndex )
        
        index = self.gui.lightDutyVehicleCount_CBox.findText(columnLightDutyVehicle)
        self.gui.lightDutyVehicleCount_CBox.setCurrentIndex( index if index > 0 else unknownIndex )
        
        index = self.gui.heavyDutyVehicleCount_CBox.findText(columnHeavyDutyVechicle)
        self.gui.heavyDutyVehicleCount_CBox.setCurrentIndex( index if index > 0 else unknownIndex )
        
        index = self.gui.urbanBusesCount_CBox.findText(columnUrbanBuses)
        self.gui.urbanBusesCount_CBox.setCurrentIndex( index if index > 0 else unknownIndex )
        
        index = self.gui.coachesCount_CBox.findText(columnCouch)
        self.gui.coachesCount_CBox.setCurrentIndex( index if index > 0 else unknownIndex )
        
        index = self.gui.motorcycleCount_CBox.findText(columnMotorcycle)
        self.gui.motorcycleCount_CBox.setCurrentIndex( index if index > 0 else unknownIndex )
        
        index = self.gui.averageVehicleSpeed_Cbox.findText(columnAverageSpeed)
        self.gui.averageVehicleSpeed_Cbox.setCurrentIndex( index if index > 0 else unknownIndex )
    
        # add all modification events to notify project modification
        try:
            # to avoid add multiple listener, remove previous listener
            self.gui.passengerCarsCount_CBox.currentIndexChanged.disconnect(self.setProjectModified)
            self.gui.lightDutyVehicleCount_CBox.currentIndexChanged.disconnect(self.setProjectModified)
            self.gui.heavyDutyVehicleCount_CBox.currentIndexChanged.disconnect(self.setProjectModified)
            self.gui.urbanBusesCount_CBox.currentIndexChanged.disconnect(self.setProjectModified)
            self.gui.coachesCount_CBox.currentIndexChanged.disconnect(self.setProjectModified)
            self.gui.motorcycleCount_CBox.currentIndexChanged.disconnect(self.setProjectModified)
            self.gui.averageVehicleSpeed_Cbox.currentIndexChanged.disconnect(self.setProjectModified)
        except (Exception) as ex:
            pass
        
        self.gui.passengerCarsCount_CBox.currentIndexChanged.connect(self.setProjectModified)
        self.gui.lightDutyVehicleCount_CBox.currentIndexChanged.connect(self.setProjectModified)
        self.gui.heavyDutyVehicleCount_CBox.currentIndexChanged.connect(self.setProjectModified)
        self.gui.urbanBusesCount_CBox.currentIndexChanged.connect(self.setProjectModified)
        self.gui.coachesCount_CBox.currentIndexChanged.connect(self.setProjectModified)
        self.gui.motorcycleCount_CBox.currentIndexChanged.connect(self.setProjectModified)
        self.gui.averageVehicleSpeed_Cbox.currentIndexChanged.connect(self.setProjectModified)
    
    def isModified(self):
        ''' Return true if the curret project is marked as modified
            The modified status is based on the status of Save button
        '''
        return self.gui.saveProject_PButton.isEnabled()
