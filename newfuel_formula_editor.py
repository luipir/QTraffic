# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SearchPlus - A QGIS plugin Toponomastic searcher
                              -------------------
        begin                : 2015-06-19
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Luigi Pirelli
        email                : luipir@gmail.com
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
import sys
import json
import traceback
import collections
from qgis.core import (QgsApplication,
                       QgsMessageLog)
from qgis.utils import iface
from PyQt4 import QtGui, QtCore
from ui.newfuel_formula_editor_dialog_ui import Ui_newFuelFormula_dialog

class NewFuelFormulaEditor(QtGui.QDialog, Ui_newFuelFormula_dialog):
    
    def __init__(self, parent=None, project=None):
        """Constructor."""
        super(NewFuelFormulaEditor, self).__init__(parent)
        
        # parent is the dock widget with all graphical elements
#         self.plugin = parent.parent

        # init some globals
        self.applicationPath = os.path.dirname(os.path.realpath(__file__))
        self.project = project
        
        self.projectPath = os.path.dirname( self.project.fileName() )
        self.formulaDict = None

        # Set up the user interface from Designer.
        self.setupUi(self)
        
        # load formula file
        self.readFormulaConf()
        if not self.formulaDict:
            return
        
        # set up interface basing on formula config file
        self.setUpGuiBasingOnConf()
    
    def readFormulaConf(self):
        ''' Read the JSON configuration file where are set all emission functions for New Fuels
        '''
        if not project:
            return
        
        # get the conf filename
        key = 'FuelProperties/FormulasConfig'
        confFileName = self.project.value(key, './NewFuelFormulas.json')
        if not confFileName:
            message = self.plugin.tr("No formula file specified in the project for the key %s" % key)
            self.plugin.iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return
        
        if not os.path.isabs(confFileName):
            confFileName = os.path.join(self.projectPath, confFileName)
        
        # laod it
        try:
            with open(confFileName) as confFile:
                # loaded in and OrderedDict to allow maintaining the order of classes
                # contained in the json file. This will be reflected in the order
                # shown in the sunburst visualization/editor
                self.formulaDict = json.load(confFile, object_pairs_hook=collections.OrderedDict)
                
        except Exception as ex:
#             QgsMessageLog.logMessage(traceback.format_exc(), self.plugin.pluginTag, QgsMessageLog.CRITICAL)
            QgsMessageLog.logMessage(traceback.format_exc(), 'QTraffic', QgsMessageLog.CRITICAL)
#             self.plugin.iface.messageBar().pushMessage(self.plugin.tr("Error loading formula conf file. Error: %s" % str(ex)), QgsMessageBar.CRITICAL)
            return
    
    def setUpGuiBasingOnConf(self):
        ''' Update current dialog interface adding tabs depending on json config
        '''
        if not self.formulaDict:
            return
        
        # add tabs only if vehicles are available
        if len(self.formulaDict) == 0:
            return
        
        # set function validator to allow only math functions and restricted variables
        simpleFormulaValidator = QtGui.QRegExpValidator( QtCore.QRegExp('^(\(|\)|-|\+|/|\*|\.|,|\d|V|\^|E)+$') )
        
        # get where to add tabs
        vehicleTab = QtGui.QTabWidget()
                
        # create fist level of tab related to VehicleType
        for vehicleType, vechicleData in self.formulaDict.items():
            vehicleTabWidgetLayout = QtGui.QVBoxLayout()
            
            vehicleTabWidget = QtGui.QWidget()
            vehicleTabWidget.setLayout(vehicleTabWidgetLayout)            
            
            # create subTab
            euroClassTab = QtGui.QTabWidget()
            
            # add sub tabs for EURO classes
            euroClasses = vechicleData['New fuel']
            for euroClass, polluntantFunctions in euroClasses.items():
                euroClassTabWidgetLayout = QtGui.QVBoxLayout()
                euroClassTabWidgetLayout.setSpacing(0)
                
                euroClassTabWidget = QtGui.QWidget()
                euroClassTabWidget.setLayout(euroClassTabWidgetLayout)
                
                # add QLineEdit for each pollutant
                for pollutantName, pollutantfunction in polluntantFunctions.items():
                    hLayout = QtGui.QHBoxLayout()
                    hLayout.setContentsMargins(0, 0, 0, 0)
                    
                    editWidget = QtGui.QWidget()
                    editWidget.setLayout(hLayout)
                    
                    label = QtGui.QLabel( '{} ='.format(pollutantName) )
                    lineEdit = QtGui.QLineEdit()
                    lineEdit.setObjectName( '{}_{}_{}_{}'.format(vehicleType, 'New fuel', euroClass, pollutantName) )
                    lineEdit.setValidator( simpleFormulaValidator )
                    lineEdit.setText( pollutantfunction )
                    
                    hLayout.addWidget(label, 0)
                    hLayout.addWidget(lineEdit, 1)

                    euroClassTabWidgetLayout.addWidget(editWidget)
                
                # add tab
                euroClassTab.addTab(euroClassTabWidget, euroClass)
            
            # add sub tab in the widget
            vehicleTabWidgetLayout.addWidget(euroClassTab)           
            
            # add tab
            vehicleTab.addTab(vehicleTabWidget, vehicleType)
        
        self.layoutContainer.addWidget(vehicleTab)
    

if __name__ == '__main__':
    # add current running path in the searching path
    srcpath = os.path.dirname(os.path.realpath(sys.argv[0]))
    sys.path.append(srcpath)
    
    try:
        # init qgis env and application
        app = QgsApplication(sys.argv, True)    
        QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX'], True)
        QgsApplication.initQgis()
    
        # load project
        projectFile = os.path.join( os.path.dirname(os.path.realpath(__file__)), 'config', 'defaultProject.cfg')
        project = QtCore.QSettings(projectFile, QtCore.QSettings.IniFormat)
        project.setIniCodec("UTF-8")
        
        # run gui
        gui = NewFuelFormulaEditor(iface, project)
        gui.show()
    
        app.exec_()
     
    finally:
        QgsApplication.exitQgis()
