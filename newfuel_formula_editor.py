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
import shutil
from qgis.core import (QgsApplication,
                       QgsMessageLog)
from qgis.utils import iface
from PyQt4 import QtGui, QtCore
from ui.newfuel_formula_editor_dialog_ui import Ui_newFuelFormula_dialog
from utils import setFileWindowsHidden

class NewFuelFormulaEditor(QtGui.QDialog, Ui_newFuelFormula_dialog):
    ''' Dynamic gui toedit Formula file
    '''
    projectModified = QtCore.pyqtSignal()
    
    def __init__(self, parent=None, project=None, gui=None):
        """Constructor."""
        super(NewFuelFormulaEditor, self).__init__(parent)
        
        # parent is the dock widget with all graphical elements
        self.gui = parent

        # init some globals
        self.applicationPath = os.path.dirname(os.path.realpath(__file__))
        self.project = project
        
        self.projectPath = os.path.dirname( self.project.fileName() )
        self.formulaDict = None
        self.formulaFileName = None
        self.temporaryFormulaFileName = None
        self.vehicleTab = None
        self.key = 'FuelProperties/FormulasConfig'

        # Set up the user interface from Designer.
        self.setupUi(self)
        
        # get the conf filename
        confFileName = self.project.value(self.key, './NewFuelFormulas.json')
        if not confFileName:
            message = self.tr("No formula file specified in the project for the key %s" % key)
            iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return
        
        if not os.path.isabs(confFileName):
            self.formulaFileName = os.path.join(self.projectPath, confFileName)
        
        # create temporary formulaFileName useful to manage save and reset
        basename = os.path.basename(confFileName)
        self.temporaryFormulaFileName = os.path.join(self.projectPath, '.temp.'+basename)
        shutil.copy(self.formulaFileName, self.temporaryFormulaFileName)
        
        # commented because hiding in Windows lock the file
        #setFileWindowsHidden(self.temporaryFormulaFileName)
        
        # set origin formula filename
        if not self.formulaFileName:
            return
        self.formulaFile_LEdit.setText(self.formulaFileName)
        
        # set listeners to creats new, save or saveas formula file
        self.formulaFile_LEdit.returnPressed.connect(self.loadFormulaConf)
        self.selectFunctionFile_TButton.clicked.connect(self.loadFormulaConf)
        self.loadDefaultFormulaFile_PButton.clicked.connect(self.setDefaultFormulaConf)
        self.saveAsFormulaFile_PButton.clicked.connect(self.saveAsFormulaConf)
        self.saveFormulaFile_PButton.clicked.connect(self.saveFormulaFile)
        
        # set save button disabled at the beginning
        self.saveFormulaFile_PButton.setEnabled(False)
        
        # create gui basing on conf
        self.reloadFormulaConf()
        
    def reject(self):
        ''' Reimplement reject to manage if ignore it in case unsaved Formula file
        '''
        if self.isModified():
            # ask what to do
            title = self.tr("Warning")
            message = self.tr("Formula file is modified, if you continue you can will discard modifications. Continue?")
            ret = QtGui.QMessageBox.question(self, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                # do nothing and don't close de Dialog
                return
        
        #self.done(QtGui.QDialog.Rejected)
        super(NewFuelFormulaEditor, self).done(QtGui.QDialog.Rejected)
    
    def manageCloseButton(self):
        ''' Reimplement closeEvent to manage if ignore it in case unsaved Formula file
        '''
        if self.isModified():
            # ask what to do
            title = self.tr("Warning")
            message = self.tr("Formula file is modified, if you continue you can will discard modifications. Continue?")
            ret = QtGui.QMessageBox.question(self, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
     
    def reloadFormulaConf(self):
        ''' Read conf file and set GUI basing on loaded conf
        '''
         # load formula file
        self.readFormulaConf()
        if not self.formulaDict:
            return
        
        # set up interface basing on formula config file
        self.setUpGuiBasingOnConf()
    
    def readFormulaConf(self):
        ''' Read the JSON configuration file where are set all emission functions for New Fuels
        '''
        if not self.project:
            return
        
        # laod it
        try:
            with open(self.temporaryFormulaFileName) as confFile:
                # loaded in and OrderedDict to allow maintaining the order of classes
                # contained in the json file. This will be reflected in the order
                # shown in the sunburst visualization/editor
                self.formulaDict = json.load(confFile, object_pairs_hook=collections.OrderedDict)
                
        except Exception as ex:
            QgsMessageLog.logMessage(traceback.format_exc(), 'QTraffic', QgsMessageLog.CRITICAL)
#             iface.messageBar().pushMessage(self.tr("Error loading formula conf file. Error: %s" % str(ex)), QgsMessageBar.CRITICAL)
            raise ex
    
    def setUpGuiBasingOnConf(self):
        ''' Update current dialog interface adding tabs depending on json config
        '''
        if not self.formulaDict:
            return
        
        # add tabs only if vehicles are available
        if len(self.formulaDict) == 0:
            return
        
        # set function validator to allow only math functions and restricted variables
        simpleFormulaValidator = QtGui.QRegExpValidator( QtCore.QRegExp('^(\(|\)|-|\+|/|\*|\.|,|\d|V|\^|E|\ )+$') )
        
        # get where to add tabs
        if self.vehicleTab:
            # remove every old tabs
            self.vehicleTab.deleteLater()
        
        self.vehicleTab = QtGui.QTabWidget()
                
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
                    
                    # add listener to modify dictionary when the line edit is edited(not necessity to type return)
                    lineEdit.textEdited.connect(self.updateTemporaryFormulaConf)
                    
                    hLayout.addWidget(label, 0)
                    hLayout.addWidget(lineEdit, 1)

                    euroClassTabWidgetLayout.addWidget(editWidget)
                
                # add tab
                euroClassTab.addTab(euroClassTabWidget, euroClass)
            
            # add sub tab in the widget
            vehicleTabWidgetLayout.addWidget(euroClassTab)           
            
            # add tab
            self.vehicleTab.addTab(vehicleTabWidget, vehicleType)
        
        # add new tabls        
        self.layoutContainer.addWidget(self.vehicleTab)
    
    def updateTemporaryFormulaConf(self, newFormula):
        '''update temporary formula dictionary basing on object name that
           emitted the 'textChanged' signal
        '''
        objectName = self.sender().objectName()
        if not objectName:
            return
        
        # get all componets of sender name to allow modification in the dictionary
        vehicleType, newFuel, euroClass, pollutantName = objectName.split('_')
        
        # update dict
        self.formulaDict[vehicleType][newFuel][euroClass][pollutantName] = newFormula
        
        # save on temporary formula file
        with open(self.temporaryFormulaFileName, 'w') as outfile:
            json.dump(self.formulaDict, 
                      outfile, 
                      ensure_ascii=False, 
                      check_circular=True, 
                      allow_nan=True, 
                      cls=None, 
                      indent=2, # allow pretty formatting of the json
                      separators=None, 
                      encoding="utf-8", 
                      default=None, 
                      sort_keys=False) # to mantain the oreding of the OrdererdDict
        
        # formula file is modified
        self.setFormulaFileModified()
    
    def loadFormulaConf(self):
        ''' Load or create a new formula file if the selected project does not exist
        '''
        if not self.formulaFileName:
            return

        # check if current project has been modified to 
        # avoid to override modifications
        if self.isModified():
            title = self.tr("Warning")
            message = self.tr("Formula file is modified, if you continue you can overwrite modifications. Continue?")
            ret = QtGui.QMessageBox.question(self, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        # get last conf to start from its path
        startPath = os.path.dirname( self.formulaFileName )
        
        # ask for the new conf file
        formulaFileName = QtGui.QFileDialog.getOpenFileName(self, "Select a Formula file. File will be copied in the project path", startPath, 
                                                            self.tr("Ini (*.json);;All (*)"))
        if not formulaFileName:
            return
        
        # check if file does not exist
        if not os.path.exists(formulaFileName):
            title = self.tr("Warning")
            message = self.tr("Formula file does not exist")
            iface.messageBar().pushMessage(message, QgsMessageBar.WARNING)
            return            
        
        # copy the selected file in the current project directory as new formula file
        basename = os.path.basename(formulaFileName)
        newFormulaFileName = os.path.join(self.projectPath, basename)
        shutil.copyfile(formulaFileName, newFormulaFileName)
        
        # load conf
        self.reloadFormulaConf()
        
        # set new conf file as default
        self.project.setValue(self.key, newFormulaFileName)
        
        # notify project modification
        self.projectModified.emit()

    def isModified(self):
        ''' Return true if the curret formula file is marked as modified
            The modified status is based on the status of Save button
        '''
        return self.saveFormulaFile_PButton.isEnabled()

    def setDefaultFormulaConf(self):
        ''' Set default formula conf getting the default one in the current project dir
        '''
        # check if current formula conf has been modified to 
        # avoid to override modifications
        if self.isModified():
            title = self.tr("Warning")
            message = self.tr("Forula conf is modified, if you continue you can overwrite modifications. Continue?")
            ret = QtGui.QMessageBox.question(self, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        # get default formula file
        formulaBasename = os.path.basename(self.gui.defaultNewFuelFormulaFileName)
        completeFormulaFileName = os.path.join(self.projectPath, formulaBasename)
        shutil.copyfile(self.gui.defaultNewFuelFormulaFileName, completeFormulaFileName)
                
        # create temporary formulaFileName useful to manage save and reset
        self.temporaryFormulaFileName = os.path.join(self.projectPath, '.temp.'+formulaBasename)
        shutil.copy(completeFormulaFileName, self.temporaryFormulaFileName)
        
        # commented because hiding in Windows lock the file
        #setFileWindowsHidden(self.temporaryFormulaFileName)
           
        # load conf
        self.reloadFormulaConf()
        
        # set new conf file as default
        self.project.setValue(self.key, formulaBasename)
        
        # notify project modification
        self.projectModified.emit()

    def saveAsFormulaConf(self):
        ''' Duplicate a fomrula file changing the name
        '''
        if not self.formulaDict:
            return
        
        # check if current formula conf has been modified to 
        # avoid to override modifications
        if self.isModified():
            title = self.tr("Warning")
            message = self.tr("Forula conf is modified, if you continue you will write the older version!. Continue?")
            ret = QtGui.QMessageBox.question(self, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        # get last conf to start from its path
        startPath = os.path.dirname( self.formulaFileName )
        
        # ask for the new formula filename
        newFormulaFileName = QtGui.QFileDialog.getSaveFileName(self, "Select the new Formula file. Project will remain unmodified", startPath)
        if not newFormulaFileName:
            return
        
        # copy current formula to new formulafilename
        # beaware that coping it does not modify current project basing on current formula file
        # This function allow only to create a copy of the current formula file
        shutil.copy(self.formulaFileName, newFormulaFileName)
        
    def saveFormulaFile(self):
        ''' Save the current formulafile (e.g copy the temp json on the original one)
        '''
        if not self.isModified():
            return
        
        # copy the current temp ini on the original one
        shutil.copyfile(self.temporaryFormulaFileName, self.formulaFileName)
        
        self.setFormulaFileSaved()
    
    @QtCore.pyqtSlot()
    def setFormulaFileModified(self):
        ''' Set status of formula file editor GUI because the formula file has been modified
            This method is a slot called everytime a gui element has been modified
        '''
        # do nothing if already marked as modified
        if self.isModified():
            return
        
        # enable Save button
        self.saveFormulaFile_PButton.setEnabled(True)
        
        # set tab text = tab text + '*' to show that project has been modified
        self.setWindowTitle(self.windowTitle() + '*')
    
    @QtCore.pyqtSlot()
    def setFormulaFileSaved(self):
        ''' Set status of formula file GUI as saved = not modified
            This method is a slot called everytime a formula file is saved
        '''
        # do nothing if marked as not modified
        if not self.isModified():
            return
        
        # enable Save button
        self.saveFormulaFile_PButton.setEnabled(False)
        
        # set tab text = tab text + '*' to show that project has been modified
        self.setWindowTitle(self.windowTitle()[0:-1])
    
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
