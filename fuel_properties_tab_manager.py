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

class FuelPropertiesTabManager(QtCore.QObject):
    ''' Class to hide managing of relative tab
    '''
    projectModified = QtCore.pyqtSignal()
        
    def __init__(self, parent=None):
        '''constructor'''
        super(FuelPropertiesTabManager, self).__init__(parent)

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
        
    def initTabTabIndex(self):
        ''' Retrieve what tab index refer the current tab manager
        '''
        for tabIndex in range(self.gui.tabWidget.count()):
            if self.gui.tabWidget.tabText(tabIndex) == "Fuel properties":
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
        e.g 
        [Processing.Parameters.FuelProperties.Gasoline]
        Sulphur_contents=165 # in ppm
        Pb_contents=0.005\t # in g/l
        Volatility=0.1
        
        [Processing.Parameters.FuelProperties.Diesel]
        Sulphur_contents=400    # in ppm
        Pb_contents=0.005 # in g/l
        Volatility=0.2
        '''
        if not self.project:
            return
        
        # get conf parameters
        gasoline_sulphur_contents = int(self.project.value('Processing/Parameters/FuelProperties/Gasoline/Sulphur_contents', 0))
        gasoline_pb_contents = float(self.project.value('Processing/Parameters/FuelProperties/Gasoline/Pb_contents', 0.0))
        gasoline_volatility = float(self.project.value('Processing/Parameters/FuelProperties/Gasoline/Volatility', 0.0))
        diesel_sulphur_contents = int(self.project.value('Processing/Parameters/FuelProperties/Diesel/Sulphur_contents', 0))
        diesel_pb_contents = float(self.project.value('Processing/Parameters/FuelProperties/Diesel/Pb_contents', 0.0))
        diesel_volatility = float(self.project.value('Processing/Parameters/FuelProperties/Diesel/Volatility', 0.0))
        
        # avoid emitting signal in case of reset of indexes
        try:
            # to avoid add multiple listener, remove previous listener
            self.gui.gasolineSulphureContent_SBox.valueChanged.disconnect(self.saveTabOnProject)
            self.gui.gasolinePbContents_SBox.valueChanged.disconnect(self.saveTabOnProject)
            self.gui.gasolineVolatility_SBox.valueChanged.disconnect(self.saveTabOnProject)
            self.gui.dieselSulphureContent_SBox.valueChanged.disconnect(self.saveTabOnProject)
            self.gui.dieselPbContents_SBox.valueChanged.disconnect(self.saveTabOnProject)
            self.gui.dieselVolatility_SBox.valueChanged.disconnect(self.saveTabOnProject)
        except (Exception) as ex:
            pass
        
        # now populare spin boxes
        self.gui.gasolineSulphureContent_SBox.setValue( gasoline_sulphur_contents )
        self.gui.gasolinePbContents_SBox.setValue( gasoline_pb_contents )
        self.gui.gasolineVolatility_SBox.setValue( gasoline_volatility )
        self.gui.dieselSulphureContent_SBox.setValue( diesel_sulphur_contents )
        self.gui.dieselPbContents_SBox.setValue( diesel_pb_contents )
        self.gui.dieselVolatility_SBox.setValue( diesel_volatility )
        
        # add all modification events to notify project modification
        self.gui.gasolineSulphureContent_SBox.valueChanged.connect(self.saveTabOnProject)
        self.gui.gasolinePbContents_SBox.valueChanged.connect(self.saveTabOnProject)
        self.gui.gasolineVolatility_SBox.valueChanged.connect(self.saveTabOnProject)
        self.gui.dieselSulphureContent_SBox.valueChanged.connect(self.saveTabOnProject)
        self.gui.dieselPbContents_SBox.valueChanged.connect(self.saveTabOnProject)
        self.gui.dieselVolatility_SBox.valueChanged.connect(self.saveTabOnProject)
    
    def saveTabOnProject(self):
        ''' Save tab configuration in the project basing on GUI values
        '''
        # get values from the GUI
        gasoline_sulphur_contents = int(self.gui.gasolineSulphureContent_SBox.value())
        gasoline_pb_contents = float(self.gui.gasolinePbContents_SBox.value())
        gasoline_volatility = float(self.gui.gasolineVolatility_SBox.value())
        diesel_sulphur_contents = int(self.gui.dieselSulphureContent_SBox.value())
        diesel_pb_contents = float(self.gui.dieselPbContents_SBox.value())
        diesel_volatility = float(self.gui.dieselVolatility_SBox.value())
        
        # set conf parameters
        self.project.setValue('Processing/Parameters/FuelProperties/Gasoline/Sulphur_contents', gasoline_sulphur_contents)
        self.project.setValue('Processing/Parameters/FuelProperties/Gasoline/Pb_contents', gasoline_pb_contents)
        self.project.setValue('Processing/Parameters/FuelProperties/Gasoline/Volatility', gasoline_volatility)
        self.project.setValue('Processing/Parameters/FuelProperties/Diesel/Sulphur_contents', diesel_sulphur_contents)
        self.project.setValue('Processing/Parameters/FuelProperties/Diesel/Pb_contents', diesel_pb_contents)
        self.project.setValue('Processing/Parameters/FuelProperties/Diesel/Volatility', diesel_volatility)
            
        # notify project modification
        self.projectModified.emit()
