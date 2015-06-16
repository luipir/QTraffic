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
                       QgsVectorLayer)
from qgis.gui import (QgsMessageBar)

class InputNetworkTabManager(QtCore.QObject):
    ''' Class to hide managing of project load and save
    '''
    projectModified = QtCore.pyqtSignal()
        
    def __init__(self, parent=None):
        '''constructor'''
        super(InputNetworkTabManager, self).__init__(parent)

        # parent is the dock widget with all graphical elements
        self.gui = parent
        self.plugin = parent.parent
        
        # init some globals
        self.applicationPath = os.path.dirname(os.path.realpath(__file__))
        self.project = None
        self.roadLayer = None
        
        # retrieve the current tab index
        self.initTabTabIndex()
        
        # disable tab at the beginning
        self.gui.tabWidget.setTabEnabled(self.tabIndex, False)

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
        
        # if layer exist load it
        if not os.path.exists(inputLayerFile):
            msg = self.plugin.tr('Layer file %s does not exist' % inputLayerFile)
            raise Exception(msg) 
        
        self.roadLayer = QgsVectorLayer(inputLayerFile, 'roadLayer', 'ogr')
        if not self.roadLayer.isValid():
            raise Exception( self.roadLayer.error().message(QgsErrorMessage.Text) )
        
        # show layer in the canvas
        QgsMapLayerRegistry.instance().addMapLayer(self.roadLayer)
        
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
            self.gui.inputLayer_lineEdit.editingFinished.disconnect(self.saveTabOnProject)
            self.gui.roadType_CBox.currentIndexChanged.disconnect(self.saveTabOnProject)
            self.gui.roadLenght_CBox.currentIndexChanged.disconnect(self.saveTabOnProject)
            self.gui.roadGradient_CBox.currentIndexChanged.disconnect(self.saveTabOnProject)
        except (Exception) as ex:
            pass
        
        self.gui.inputLayer_lineEdit.editingFinished.connect(self.saveTabOnProject)
        self.gui.roadType_CBox.currentIndexChanged.connect(self.saveTabOnProject)
        self.gui.roadLenght_CBox.currentIndexChanged.connect(self.saveTabOnProject)
        self.gui.roadGradient_CBox.currentIndexChanged.connect(self.saveTabOnProject)
    
    def saveTabOnProject(self):
        ''' Save tab configuration in the project basing on GUI values
        '''
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
        
        self.projectModified.emit()
        
    def getRoadLayer(self):
        return self.roadLayer
    
    def removeRoadLayer(self):
        ''' Remove current road layer from canvas
        '''
        if self.roadLayer and self.roadLayer.isValid():
            # do nothing if layer already removed by user
            QgsMapLayerRegistry.instance().removeMapLayer(self.roadLayer.id())