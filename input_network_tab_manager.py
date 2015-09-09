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
                       QgsErrorMessage,
                       QgsMapLayerRegistry,
                       QgsVectorLayer,
                       QgsLogger)
from qgis.gui import (QgsMessageBar,
                      QgsMapLayerComboBox,
                      QgsMapLayerProxyModel)
from qgis.utils import iface

from select_layer_dialog import SelectLayerDialog

class InputNetworkTabManager(QtCore.QObject):
    ''' Class to hide managing of relative tab
    '''
    projectModified = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        '''constructor'''
        super(InputNetworkTabManager, self).__init__(parent)

        # parent is the dock widget with all graphical elements
        self.gui = parent
        
        # init some globals
        self.applicationPath = os.path.dirname(os.path.realpath(__file__))
        self.project = None
        self.projectPath = None
        self.roadLayer = None
        self.roadLayerId = None
        
        # retrieve the current tab index
        self.initTabTabIndex()
        
        # disable tab at the beginning
        self.gui.tabWidget.setTabEnabled(self.tabIndex, False)
        
        # set basic events
        self.gui.inputLayer_lineEdit.returnPressed.connect(self.loadLayer)
        self.gui.selectLayer_TButton.clicked.connect(self.askLayer)
        self.gui.selectFile_TButton.clicked.connect(self.askLayerFile)
        self.gui.inputNetwork_validate_PButton.clicked.connect(self.validate)

    def initTabTabIndex(self):
        ''' Retrieve what tab index refer the current tab manager
        '''
        for tabIndex in range(self.gui.tabWidget.count()):
            if self.gui.tabWidget.tabText(tabIndex) == "Input Network":
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
    
    def setTabGUIBasingOnProject(self):
        '''Set tab basing on project conf 
        '''
        if not self.project:
            return
        
        # get conf parameters
        inputLayerFile = self.project.value('InputNetwork/inputLayer', '')
        columnRoadType = self.project.value('InputNetwork/columnRoadType', '')
        columnRoadLenght = self.project.value('InputNetwork/columnRoadLenght', '')
        columnRoadSlope = self.project.value('InputNetwork/columnRoadSlope', '')
        
        # if layer exist load it otherwise only reset comboboxes
        if os.path.exists(inputLayerFile):
            # check if layer is already loaded in layer list checking it's source
            # that would be equal to the inputLayerFile (for this reason is not simple 
            # to work with db data)
            found = False
            for layerName, layer in QgsMapLayerRegistry.instance().mapLayers().items():
                if inputLayerFile == layer.publicSource():
                    # set the found layer as roadLayer
                    self.roadLayer = layer
                    found = True
                    break
            
            # if layer is not loaded... load it
            if not found:
                # get layer name to set as public name in the legend
                layerName = os.path.splitext( os.path.basename(inputLayerFile) )[0]
                
                # load layer
                self.roadLayer = QgsVectorLayer(inputLayerFile, layerName, 'ogr')
                if not self.roadLayer.isValid():
                    message = self.tr("Error loading layer: %s" % self.roadLayer.error().message(QgsErrorMessage.Text))
                    iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
                    return
                
                # show layer in the canvas
                QgsMapLayerRegistry.instance().addMapLayer(self.roadLayer)
            
            # now layer is available
            self.roadLayerId = self.roadLayer.id()
        else:
            self.roadLayer = None
            self.roadLayerId = None
        
        # avoid emitting signal in case of reset of indexes
        try:
            # to avoid add multiple listener, remove previous listener
            self.gui.inputLayer_lineEdit.returnPressed.disconnect(self.saveTabOnProject)
            self.gui.roadType_CBox.currentIndexChanged.disconnect(self.saveTabOnProject)
            self.gui.roadLenght_CBox.currentIndexChanged.disconnect(self.saveTabOnProject)
            self.gui.roadGradient_CBox.currentIndexChanged.disconnect(self.saveTabOnProject)
        except (Exception) as ex:
            pass
        
        # set text of loaded layer
        if self.roadLayer:
            self.gui.inputLayer_lineEdit.setText(self.roadLayer.publicSource())
        else:
            self.gui.inputLayer_lineEdit.setText('')
            
        # now populare combo boxes with layer colums
        if self.roadLayer:
            fieldNames = sorted([field.name() for field in self.roadLayer.pendingFields().toList()])
        else:
            fieldNames = []
        unknownIndex = -1
        
        self.gui.roadType_CBox.clear()
        self.gui.roadLenght_CBox.clear()
        self.gui.roadGradient_CBox.clear()
        
        self.gui.roadType_CBox.addItems(fieldNames)
        self.gui.roadLenght_CBox.addItems(fieldNames)
        self.gui.roadGradient_CBox.addItems(fieldNames)
        
       # select the combobox item as in the project file... if not available then "Please select"
        index = self.gui.roadType_CBox.findText(columnRoadType)
        self.gui.roadType_CBox.setCurrentIndex( index if index >= 0 else unknownIndex )
        
        index = self.gui.roadLenght_CBox.findText(columnRoadLenght)
        self.gui.roadLenght_CBox.setCurrentIndex( index if index >= 0 else unknownIndex )
        
        index = self.gui.roadGradient_CBox.findText(columnRoadSlope)
        self.gui.roadGradient_CBox.setCurrentIndex( index if index >= 0 else unknownIndex )
        
        # add all modification events to notify project modification
        self.gui.inputLayer_lineEdit.returnPressed.connect(self.saveTabOnProject)
        self.gui.roadType_CBox.currentIndexChanged.connect(self.saveTabOnProject)
        self.gui.roadLenght_CBox.currentIndexChanged.connect(self.saveTabOnProject)
        self.gui.roadGradient_CBox.currentIndexChanged.connect(self.saveTabOnProject)
        
        
        #
        #  set parameters for vechicle count/speed columns
        #
        # get parameters fron project
        columnPassengerCars = self.project.value('VehicleCountSpeed/columnPassengerCars', '')
        columnLightDutyVehicle = self.project.value('VehicleCountSpeed/columnLightDutyVehicle', '')
        columnHeavyDutyVechicle = self.project.value('VehicleCountSpeed/columnHeavyDutyVechicle', '')
        columnUrbanBuses = self.project.value('VehicleCountSpeed/columnUrbanBuses', '')
        
        columnMotorcycle = self.project.value('VehicleCountSpeed/columnMotorcycle', '')
        columnCouch = self.project.value('VehicleCountSpeed/columnCouch', '')
        columnAverageSpeed = self.project.value('VehicleCountSpeed/columnAverageSpeed', '')
        
        # avoid emitting signal in case of reset of indexes
        try:
            # to avoid add multiple listener, remove previous listener
            self.gui.passengerCarsCount_CBox.currentIndexChanged.disconnect(self.saveTabOnProject)
            self.gui.lightDutyVehicleCount_CBox.currentIndexChanged.disconnect(self.saveTabOnProject)
            self.gui.heavyDutyVehicleCount_CBox.currentIndexChanged.disconnect(self.saveTabOnProject)
            self.gui.urbanBusesCount_CBox.currentIndexChanged.disconnect(self.saveTabOnProject)
            self.gui.coachesCount_CBox.currentIndexChanged.disconnect(self.saveTabOnProject)
            self.gui.motorcycleCount_CBox.currentIndexChanged.disconnect(self.saveTabOnProject)
            self.gui.averageVehicleSpeed_Cbox.currentIndexChanged.disconnect(self.saveTabOnProject)
        except (Exception) as ex:
            pass
        
        # now populare combo boxes with layer colums
        self.gui.passengerCarsCount_CBox.clear()
        self.gui.lightDutyVehicleCount_CBox.clear()
        self.gui.heavyDutyVehicleCount_CBox.clear()
        self.gui.urbanBusesCount_CBox.clear()
        self.gui.coachesCount_CBox.clear()
        self.gui.motorcycleCount_CBox.clear()
        self.gui.averageVehicleSpeed_Cbox.clear()
        
        self.gui.passengerCarsCount_CBox.addItems(fieldNames)
        self.gui.lightDutyVehicleCount_CBox.addItems(fieldNames)
        self.gui.heavyDutyVehicleCount_CBox.addItems(fieldNames)
        self.gui.urbanBusesCount_CBox.addItems(fieldNames)
        self.gui.coachesCount_CBox.addItems(fieldNames)
        self.gui.motorcycleCount_CBox.addItems(fieldNames)
        self.gui.averageVehicleSpeed_Cbox.addItems(fieldNames)
        
        # select the combobox item as in the project file... if not available then "Please select"
        index = self.gui.passengerCarsCount_CBox.findText(columnPassengerCars)
        self.gui.passengerCarsCount_CBox.setCurrentIndex( index if index >= 0 else unknownIndex )
        
        index = self.gui.lightDutyVehicleCount_CBox.findText(columnLightDutyVehicle)
        self.gui.lightDutyVehicleCount_CBox.setCurrentIndex( index if index >= 0 else unknownIndex )
        
        index = self.gui.heavyDutyVehicleCount_CBox.findText(columnHeavyDutyVechicle)
        self.gui.heavyDutyVehicleCount_CBox.setCurrentIndex( index if index >= 0 else unknownIndex )
        
        index = self.gui.urbanBusesCount_CBox.findText(columnUrbanBuses)
        self.gui.urbanBusesCount_CBox.setCurrentIndex( index if index >= 0 else unknownIndex )
        
        index = self.gui.coachesCount_CBox.findText(columnCouch)
        self.gui.coachesCount_CBox.setCurrentIndex( index if index >= 0 else unknownIndex )
        
        index = self.gui.motorcycleCount_CBox.findText(columnMotorcycle)
        self.gui.motorcycleCount_CBox.setCurrentIndex( index if index >= 0 else unknownIndex )
        
        index = self.gui.averageVehicleSpeed_Cbox.findText(columnAverageSpeed)
        self.gui.averageVehicleSpeed_Cbox.setCurrentIndex( index if index >= 0 else unknownIndex )
    
        # add all modification events to notify project modification
        self.gui.passengerCarsCount_CBox.currentIndexChanged.connect(self.saveTabOnProject)
        self.gui.lightDutyVehicleCount_CBox.currentIndexChanged.connect(self.saveTabOnProject)
        self.gui.heavyDutyVehicleCount_CBox.currentIndexChanged.connect(self.saveTabOnProject)
        self.gui.urbanBusesCount_CBox.currentIndexChanged.connect(self.saveTabOnProject)
        self.gui.coachesCount_CBox.currentIndexChanged.connect(self.saveTabOnProject)
        self.gui.motorcycleCount_CBox.currentIndexChanged.connect(self.saveTabOnProject)
        self.gui.averageVehicleSpeed_Cbox.currentIndexChanged.connect(self.saveTabOnProject)
    
    def saveTabOnProject(self):
        ''' Save tab configuration in the project basing on GUI values
        '''
        if self.sender():
            message = "QTraffic: saveTabOnProject by sender {}".format(self.sender().objectName())
            QgsLogger.debug(message, debuglevel=3)
        
        # get values from the GUI
        inputLayerFile = self.gui.inputLayer_lineEdit.text()
        columnRoadType = self.gui.roadType_CBox.currentText()
        columnRoadLenght = self.gui.roadLenght_CBox.currentText()
        columnRoadSlope = self.gui.roadGradient_CBox.currentText()
        
        # set conf parameters
        self.project.setValue('InputNetwork/inputLayer', inputLayerFile)
        self.project.setValue('InputNetwork/columnRoadType', columnRoadType)
        self.project.setValue('InputNetwork/columnRoadLenght', columnRoadLenght)
        self.project.setValue('InputNetwork/columnRoadSlope', columnRoadSlope)
        
        #
        #  save parameters for vechicle count/speed columns
        #
        # get values from the GUI
        columnPassengerCars = self.gui.passengerCarsCount_CBox.currentText()
        columnLightDutyVehicle = self.gui.lightDutyVehicleCount_CBox.currentText()
        columnHeavyDutyVechicle = self.gui.heavyDutyVehicleCount_CBox.currentText()
        columnUrbanBuses = self.gui.urbanBusesCount_CBox.currentText()
        
        columnCouch = self.gui.coachesCount_CBox.currentText()
        columnMotorcycle = self.gui.motorcycleCount_CBox.currentText()
        columnAverageSpeed = self.gui.averageVehicleSpeed_Cbox.currentText()
        
        # set conf parameters
        self.project.setValue('VehicleCountSpeed/columnPassengerCars', columnPassengerCars)
        self.project.setValue('VehicleCountSpeed/columnLightDutyVehicle', columnLightDutyVehicle)
        self.project.setValue('VehicleCountSpeed/columnHeavyDutyVechicle', columnHeavyDutyVechicle)
        self.project.setValue('VehicleCountSpeed/columnUrbanBuses', columnUrbanBuses)
        self.project.setValue('VehicleCountSpeed/columnMotorcycle', columnMotorcycle)
        self.project.setValue('VehicleCountSpeed/columnCouch', columnCouch)
        self.project.setValue('VehicleCountSpeed/columnAverageSpeed', columnAverageSpeed)
        
        # notify project modification
        self.projectModified.emit()
    
    def askLayer(self):
        ''' Ask for the layer to load
            Look for layer already loaded in the layer list 
        '''
        # create dialog to select layer
        dlg = SelectLayerDialog(self.gui)
        ret = dlg.exec_()
        if ret:
            # get selected layer
            newLayer = dlg.selectLayer_CBox.currentLayer()
            
            # set gui with the new layer name
            self.gui.inputLayer_lineEdit.setText(newLayer.publicSource())
            
            # then load layer
            self.loadLayer()
        
    def askLayerFile(self):
        ''' Ask for the layer file to load
            Don't load it if already loaded comparing source of tre layer
        '''
        if not self.project:
            return
        
        # if a layer is present in the project start from the path of that layer
        oldLayer = self.project.value('InputNetwork/inputLayer', '')
        if oldLayer:
            startPath = os.path.dirname(oldLayer)
        else:
            startPath = self.projectPath
        
        # get porject path
        layerFileName = QtGui.QFileDialog.getOpenFileName(self.gui, "Select road layer", startPath, 
                                                          self.tr("Shp (*.shp);;All (*)"))
        if not layerFileName:
            return
        
        # set gui with the new layer name
        self.gui.inputLayer_lineEdit.setText(layerFileName)
        
        # then load layer
        self.loadLayer()
    
    def loadLayer(self):
        ''' Load a shape layer 
        '''
        # get layer filename
        layerFileName = self.gui.inputLayer_lineEdit.text()
        if not layerFileName:
            return
        if not os.path.exists(layerFileName):
            title = self.tr("Warning")
            message = self.tr("Layer does not exist")
            iface.messageBar().pushMessage(message, QgsMessageBar.WARNING)
            return
        
        currentLayerFile = self.project.value('InputNetwork/inputLayer', '')
        if currentLayerFile != layerFileName:
            self.project.setValue('InputNetwork/inputLayer', layerFileName)
        self.setTabGUIBasingOnProject()
        
        # notify project modification if layer source is modified
        if currentLayerFile != layerFileName:
            self.projectModified.emit()
    
    def getRoadLayer(self):
        return self.roadLayer
    
    def getRoadLayerId(self):
        return self.roadLayerId
    
    def removeRoadLayer(self):
        ''' Remove current road layer from canvas
        '''
        if self.roadLayer and self.roadLayer.isValid():
            # do nothing if layer already removed by user
            QgsMapLayerRegistry.instance().removeMapLayer(self.roadLayer.id())
    
    def validate(self):
        ''' Validate parameters inserted in the Input Network tab:
            Validation performed is:
            Mandatory parameters:
                Input layer
                Road Type
                Road lenght
                Road Gradient
                Average vehicle speed
                At least one of vehicle count
            Value validation:
                Road Type have to be integer
                Road lenght, lenght, Gradient have to be float
                Average vehicle speed have to be lfoat
                Count column have to be float or integer
            Inter tab validation
                Road type column values have to be present as categories in Fleet Distribution classes
            This method notify the error in case of validation failure
            This method notify success in case of correct validation
            @return: True is validated or False if not 
        '''
        if not self.project:
            return False
        
        inputLayerFile = self.gui.inputLayer_lineEdit.text()
        columnRoadType = self.gui.roadType_CBox.currentText()
        columnRoadLenght = self.gui.roadLenght_CBox.currentText()
        columnRoadSlope = self.gui.roadGradient_CBox.currentText()
        columnAverageSpeed = self.gui.averageVehicleSpeed_Cbox.currentText()

        columnPassengerCars = self.gui.passengerCarsCount_CBox.currentText()
        columnLightDutyVehicle = self.gui.lightDutyVehicleCount_CBox.currentText()
        columnHeavyDutyVechicle = self.gui.heavyDutyVehicleCount_CBox.currentText()
        columnUrbanBuses = self.gui.urbanBusesCount_CBox.currentText()
        columnCouch = self.gui.coachesCount_CBox.currentText()
        columnMotorcycle = self.gui.motorcycleCount_CBox.currentText()
        
        # mandatory fields
        if not inputLayerFile:
            message = self.tr("Validation error: Input shape have to be choosed")
            iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return False
        
        if not columnRoadType:
            message = self.tr("Validation error: Road type column have to be selected from input layer")
            iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return False
        
        if not columnRoadLenght:
            message = self.tr("Validation error: Road lenght column have to be selected from input layer")
            iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return False
        
        if not columnRoadLenght:
            message = self.tr("Validation error: Road slope column have to be selected from input layer")
            iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return False
        
        if not columnAverageSpeed:
            message = self.tr("Validation error: Average vechicle speed column have to be selected from input layer")
            iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return False
        
        # at least one column count have to be selected
        if (not columnPassengerCars and
            not columnLightDutyVehicle and
            not columnHeavyDutyVechicle and
            not columnUrbanBuses and
            not columnCouch and
            not columnMotorcycle):
            message = self.tr("Validation error: At least a vehicle count column have to be selected from input layer")
            iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return False
        
        # value validations
        fields = self.roadLayer.pendingFields()
        checkDict = {
            columnRoadType: [QtCore.QVariant.Int, QtCore.QVariant.LongLong],
            columnRoadLenght: [QtCore.QVariant.Int, QtCore.QVariant.Double, QtCore.QVariant.LongLong],
            columnRoadSlope: [QtCore.QVariant.Int, QtCore.QVariant.Double, QtCore.QVariant.LongLong],
            columnAverageSpeed: [QtCore.QVariant.Int, QtCore.QVariant.Double, QtCore.QVariant.LongLong],
            columnPassengerCars: [QtCore.QVariant.Int, QtCore.QVariant.Double, QtCore.QVariant.LongLong],
            columnLightDutyVehicle: [QtCore.QVariant.Int, QtCore.QVariant.Double, QtCore.QVariant.LongLong],
            columnHeavyDutyVechicle: [QtCore.QVariant.Int, QtCore.QVariant.Double, QtCore.QVariant.LongLong],
            columnUrbanBuses: [QtCore.QVariant.Int, QtCore.QVariant.Double, QtCore.QVariant.LongLong],
            columnCouch: [QtCore.QVariant.Int, QtCore.QVariant.Double, QtCore.QVariant.LongLong],
            columnMotorcycle: [QtCore.QVariant.Int, QtCore.QVariant.Double, QtCore.QVariant.LongLong],
        }
        
        for columnName, admissibleTypes in checkDict.items():
            if not columnName:
                continue
            
            field = fields.field(columnName)
            if not field.type() in admissibleTypes:
                message = self.tr("Validation error: column {} has incompatible type {}".format(columnName, field.typeName()))
                iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
                return False
        
        # inter tab validation
        index = self.roadLayer.fieldNameIndex(columnRoadType)
        roadTypes = self.roadLayer.uniqueValues(index, -1)
        if len(roadTypes) == 0:
            message = self.tr("Validation error: column {} has no values".format(columnRoadType))
            iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return False
        
        # check if each road type is present in the list of road types in the fleet distribution tab
        fleetDistributionRoadTypes = self.gui.getRoadTypes()
        for roadType in roadTypes:
            if not str(roadType) in fleetDistributionRoadTypes:
                message = self.tr("Validation error: Road type value {} is not defined in fleet distribution tab".format(roadType))
                iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
                return False
        
        return True
    
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QtCore.QCoreApplication.translate('QTraffic', message)
    