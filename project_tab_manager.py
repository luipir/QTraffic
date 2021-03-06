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
                       QgsErrorMessage,
                       QgsLogger)
from qgis.gui import (QgsMessageBar)
from qgis.utils import iface

from utils import setFileWindowsHidden

class ProjectTabManager(QtCore.QObject):
    ''' Class to hide managing of project load and save
    '''
    projectLoaded = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        '''constructor'''
        super(ProjectTabManager, self).__init__(parent)

        # parent is the dock widget with all graphical elements
        self.gui = parent
        
        # init some globals
        self.projectDir = None
        self.projectName =None
        self.projectFileName = None
        self.tempProjectFileName = '.temp.project'
        self.project = None
        self.roadLayer = None

        # create listeners to load, save and saveas
        self.gui.projectName_lineEdit.returnPressed.connect(self.loadProject)
        self.gui.selectProject_TButton.clicked.connect(self.askProject)
        self.gui.newProject_PButton.clicked.connect(self.createNewProject)
        self.gui.saveAsProject_PButton.clicked.connect(self.saveAsProject)
        self.gui.saveProject_PButton.clicked.connect(self.saveProject)
        
        # set save button disabled
        # the state of the button hide the status of the project
        # if it has been modified or not... no Project class has been created
        # to reduce code overhead du the fact that project is a .ini container
        self.gui.saveProject_PButton.setEnabled(False)
        self.gui.saveAsProject_PButton.setEnabled(False)
        
        # set gui when project is loaded
        self.projectLoaded.connect(self.setGuiProjectLoaded)
        self.projectLoaded.connect(self.setProjectSaved)
    
    @QtCore.pyqtSlot()
    def setProjectModified(self):
        ''' Set status of project GUI because the project has been modified
            This method is a slot called everytime a gui element has been modified
        '''
        message = "QTraffic: setProjectModified by sender {}".format(str(type(self.sender())))
        QgsLogger.debug(message, debuglevel=3)
        
        # do nothing if the project already marked as modified
        if self.isModified():
            return
        
        # enable Save button
        self.gui.saveProject_PButton.setEnabled(True)
        
        # set tab text = tab text + '*' to show that project has been modified
        self.gui.tabWidget.setTabText(0, self.gui.tabWidget.tabText(0) + '*')
    
    @QtCore.pyqtSlot()
    def setProjectSaved(self):
        ''' Set status of project GUI as saved = not modified
            This method is a slot called everytime a project is saved
        '''
        message = "QTraffic: setProjectSaved by sender {}".format(str(type(self.sender())))
        QgsLogger.debug(message, debuglevel=3)
        
        # do nothing if the project already marked as modified
        if not self.isModified():
            return
        
        # enable Save button
        self.gui.saveProject_PButton.setEnabled(False)
        
        # set tab text = tab text + '*' to show that project has been modified
        self.gui.tabWidget.setTabText(0, self.gui.tabWidget.tabText(0)[0:-1])
    
    @QtCore.pyqtSlot()
    def setGuiProjectLoaded(self):
        ''' Set GUI if a project has loaded
        '''
        message = "QTraffic: setGuiProjectLoaded by sender {}".format(str(type(self.sender())))
        QgsLogger.debug(message, debuglevel=3)
        
        self.gui.saveAsProject_PButton.setEnabled(True)
    
    def _reallyLoadProject(self):
        ''' Method to load the current project and save a copy and emit definetively that
            the project has loaded
        '''
        # get last conf to start from its path
        settings = QtCore.QSettings()
        settings.setIniCodec("UTF-8")
        lastProjectIni = settings.value('/QTraffic/lastProject', self.gui.defaultProjectFileName)
        
        # set some globals related with the project
        self.projectDir = os.path.dirname(lastProjectIni)
        self.projectName = os.path.basename(self.projectDir)
        self.projectFileName = os.path.basename(lastProjectIni)
        
        # make a copy of the current project file to work on the copy
        # allowing management of Save
        completeTempProjectFileName = os.path.join(self.projectDir, self.tempProjectFileName)
        shutil.copyfile(lastProjectIni, completeTempProjectFileName)
        
        # set tempfile hidden in windows
        # commented because hiding in Windows lock the file
        #setFileWindowsHidden(completeTempProjectFileName)

        # load the project ini from the saved copy instead from the original one
        self.project = QtCore.QSettings(completeTempProjectFileName, QtCore.QSettings.IniFormat)
        self.project.setIniCodec("UTF-8")
        
        # set text of loaded project (setting the original one and not the temp copy)
        self.gui.projectName_lineEdit.setText(lastProjectIni)
        
        # notify project loaded
        self.projectLoaded.emit()
    
    def createNewProject(self):
        ''' Create a new project getting an unexisting dir where to copy all default 
            configuration files, from project (with the same name of the dir) to 
            fleet distribution and formulas jsons
        '''
        # check if current project has been modified to 
        # avoid to override modifications
        if self.isModified():
            title = self.tr("Warning")
            message = self.tr("Project is modified, if you continue you can overwrite modifications. Continue?")
            ret = QtGui.QMessageBox.question(self.gui, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        # get last conf to start from its path
        settings = QtCore.QSettings()
        settings.setIniCodec("UTF-8")
        lastProjectIni = settings.value('/QTraffic/lastProject', self.gui.defaultProjectFileName)
        
        startPath = os.path.abspath( lastProjectIni )
        
        # ask for the project name
        newProjectName, ok = QtGui.QInputDialog.getText(self.gui, self.tr('New project name'), self.tr('Introduce the project name. \nNext step will be the base directory where to create the project') )
        if not ok or not newProjectName:
            return
        
        # ask for the new project name = directory name
        # if dir does not exist it will be createed automatically by getExistingDirectory
        projectDir = QtGui.QFileDialog.getExistingDirectory(self.gui, self.tr('Select the Project directory'), startPath)
        if not projectDir:
            return
        
        self.projectDir = os.path.join(projectDir, newProjectName)
        
        # if dowes not exist create dir
        if not os.path.exists(self.projectDir):
            os.makedirs(self.projectDir)
        
        # set project name
        self.projectName = newProjectName
        
        # set project config file 
        self.projectFileName = self.projectName + ".ini"
        
        # check if project is empty
        # ask to the user if he/she want to overwrite the project
        completeProjectFileName = os.path.join(self.projectDir, self.projectFileName)
        if os.path.exists(completeProjectFileName):
            title = self.tr("Warning")
            message = self.tr("Project config file already exist, continuing it will be overwrite! Continue?")
            ret = QtGui.QMessageBox.question(self.gui, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
            
        # then overwirte copyng all default files in the project dir
        # copy default project file
        shutil.copyfile(self.gui.defaultProjectFileName, completeProjectFileName)
        
        # copy fleet distribution file
        fleetBasename = os.path.basename(self.gui.defaultVehicleClassesFileName)
        completeFleetDistributionFileName = os.path.join(self.projectDir, fleetBasename)
        shutil.copyfile(self.gui.defaultVehicleClassesFileName, completeFleetDistributionFileName)
        
        # copy New Fuel formula file
        formulaBasename = os.path.basename(self.gui.defaultNewFuelFormulaFileName)
        completeFormulaFileName = os.path.join(self.projectDir, formulaBasename)
        shutil.copyfile(self.gui.defaultNewFuelFormulaFileName, completeFormulaFileName)
        
        # load project Ini
        self.project = QtCore.QSettings(completeProjectFileName, QtCore.QSettings.IniFormat)
        self.project.setIniCodec("UTF-8")

        # set new conf file as default
        settings.setValue('/QTraffic/lastProject', self.project.fileName())
        
        # init the current project
        self._reallyLoadProject()
    
    def askProject(self):
        ''' Ask for a a project file
        '''
        # check if current project has been modified to 
        # avoid to override modifications
        if self.isModified():
            title = self.tr("Warning")
            message = self.tr("Project is modified, if you continue you can overwrite modifications. Continue?")
            ret = QtGui.QMessageBox.question(self.gui, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        # get last conf to start from its path
        settings = QtCore.QSettings()
        settings.setIniCodec("UTF-8")
        lastProjectIni = settings.value('/QTraffic/lastProject', self.gui.defaultProjectFileName)
        
        startPath = os.path.dirname( lastProjectIni )
        
        # ask for the new conf file
        projectFile = QtGui.QFileDialog.getOpenFileName(self.gui, "Select a project file", startPath, 
                                                        self.tr("QTraffic project (*.ini);;All (*)"))
        if not projectFile:
            return
        
        # if projectFile does not exist do nothing
        if not os.path.exists(projectFile):
            title = self.tr("Warning")
            message = self.tr("Project does not exist")
            iface.messageBar().pushMessage(message, QgsMessageBar.WARNING)
            return            

        # set line edit value
        self.gui.projectName_lineEdit.setText(projectFile)
        
        # then load it
        self.loadProject()

    def loadProject(self):
        ''' Load a project
        '''
        # check if current project has been modified to 
        # avoid to override modifications
        if self.isModified():
            title = self.tr("Warning")
            message = self.tr("Project is modified, if you continue you can overwrite modifications. Continue?")
            ret = QtGui.QMessageBox.question(self.gui, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        # get last conf to start from its path
        settings = QtCore.QSettings()
        settings.setIniCodec("UTF-8")
        lastProjectIni = settings.value('/QTraffic/lastProject', self.gui.defaultProjectFileName)
        
        startPath = os.path.dirname( lastProjectIni )
        
        # check if something is wrote in the lineEdit
        projectFile = self.gui.projectName_lineEdit.text()

        if not os.path.exists(projectFile):
            # notify that what is in the line edit is a wrong project filename
            # don't do it if a empty string!
            if projectFile:
                message = self.tr('QTraffic: project {} does not exist! please select one'.format(projectFile))
                iface.messageBar().pushMessage(message, QgsMessageBar.WARNING, 6)
            # ask for the new conf file
            projectFile = QtGui.QFileDialog.getOpenFileName(self.gui, "Select a project file", startPath, 
                                                            self.tr("QTraffic project (*.ini);;All (*)"))
            if not projectFile:
                return
        
        # if projectFile does not exist do nothing
        if not os.path.exists(projectFile):
            title = self.tr("Warning")
            message = self.tr("Project does not exist")
            iface.messageBar().pushMessage(message, QgsMessageBar.WARNING)
            return            
        
        # set new conf file as default
        settings.setValue('/QTraffic/lastProject', projectFile)
        
        # init the current project
        self._reallyLoadProject()
        
    def saveProject(self):
        ''' Save the current project (e.g copy the temp ini in the original one)
        '''
        if not self.isModified():
            return
        
        # get last conf to start from its path
        settings = QtCore.QSettings()
        settings.setIniCodec("UTF-8")
        lastProjectIni = settings.value('/QTraffic/lastProject', self.gui.defaultProjectFileName)
        
        # copy the current temp ini on the original one
        completeTempProjectFileName = os.path.join(self.projectDir, self.tempProjectFileName)
        shutil.copyfile(completeTempProjectFileName, lastProjectIni)
        
        self.setProjectSaved()
    
    def saveAsProject(self):
        ''' Duplicate a project changing the name
        '''
        if not self.project:
            return
        
        # check if current project has been modified to 
        # avoid to save an outdated project
        if self.isModified():
            title = self.tr("Warning")
            message = self.tr("Project is modified, if you continue you duplicate an outdated version. Continue?")
            ret = QtGui.QMessageBox.question(self.gui, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        # get last conf to start from its path
        settings = QtCore.QSettings()
        settings.setIniCodec("UTF-8")
        lastProjectIni = settings.value('/QTraffic/lastProject', self.gui.defaultProjectFileName)
        
        startPath = os.path.dirname( lastProjectIni )
        
        # ask for the new project name = directory name
        # if dir does not exist it will be created automatically by getExistingDirectory
        projectDir = QtGui.QFileDialog.getExistingDirectory(self.gui, "Select the Project directory", startPath)
        if not projectDir:
            return
        
        # get project name as the name of the directory
        oldProjectName = self.projectName
        newProjectName = os.path.basename(projectDir)
        
        # check if projectDir is empty (e.g. created by getExistingDirectory) or not
        files = os.listdir(projectDir)
        if files:
            title = self.tr("Warning")
            message = self.tr("Project folder is not empty, if you continue it will be overwrite. Continue?")
            ret = QtGui.QMessageBox.question(self.gui, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        # remove projectDir to allow clean copy
        shutil.rmtree(projectDir)
        
        # duplicate current project as new one
        shutil.copytree(startPath, projectDir)
        
        # rename project files with the project name
        for filename in os.listdir(projectDir):
            if oldProjectName in filename:
                newName = filename.replace(oldProjectName, newProjectName)
                
                oldFileName = os.path.join(projectDir, filename)
                newFileName = os.path.join(projectDir, newName)
                
                os.rename(oldFileName, newFileName)
        
        # then change current project to the new one
        projectFile = os.path.join(projectDir, newProjectName + '.ini')
        
        # set new conf file as default
        settings.setValue('/QTraffic/lastProject', projectFile)
        
        # init the current project
        self._reallyLoadProject()
        
    def getProject(self):
        ''' Return the current project if any
        '''
        return self.project
    
    def isModified(self):
        ''' Return true if the curret project is marked as modified
            The modified status is based on the status of Save button
        '''
        return self.gui.saveProject_PButton.isEnabled()
    
    def validate(self):
        ''' tab validation
        Mandatory:
            project have to be saved
        '''
        if self.isModified():
            message = self.tr("Validation error: Project have to be saved")
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
    