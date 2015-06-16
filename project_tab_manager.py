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
    projectLoaded = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        '''constructor'''
        super(ProjectTabManager, self).__init__(parent)

        # parent is the dock widget with all graphical elements
        self.gui = parent
        self.plugin = parent.parent
        
        # init some globals
        self.applicationPath = os.path.dirname(os.path.realpath(__file__))
        self.defaultProjectFileName = os.path.join(self.applicationPath, 'config','defaultProject.cfg')
        self.project = None
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
    
    @QtCore.pyqtSlot()
    def setProjectModified(self):
        ''' Set status of project GUI because the project has been modified
            His method is a slot called everytime a gui element has been modified
        '''
        # do nothing if the project already marked as modified
        if self.isModified():
            return
        
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
        lastProjectIni = settings.value('/QTraffic/lastProject', self.defaultProjectFileName)
        
        startPath = os.path.abspath( lastProjectIni )
        
        # ask for the new conf file
        projectFile = QtGui.QFileDialog.getOpenFileName(self.gui, "Select a INI project file", startPath, 
                                                        self.plugin.tr("Ini (*.ini);;All (*)"))
        if not projectFile:
            return
        
        # if projectFile does not exist copy template from the default project file
        if not os.path.exists(projectFile):
            shutil.copyfile(self.defaultProjectFileName, projectFile)
        
        # set new conf file as default
        settings.setValue('/QTraffic/lastProject', projectFile)
        
        # load projectIni
        self.project = QtCore.QSettings(projectFile, QtCore.QSettings.IniFormat)
        
        # set text of loaded layer
        self.gui.projectName_lineEdit.setText(self.project.fileName())
        
        # notify project loaded
        self.projectLoaded.emit()
        
    def getProject(self):
        ''' Return the current project if any
        '''
        return self.project
    
    def isModified(self):
        ''' Return true if the curret project is marked as modified
            The modified status is based on the status of Save button
        '''
        return self.gui.saveProject_PButton.isEnabled()
