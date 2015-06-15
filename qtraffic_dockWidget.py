# -*- coding: utf-8 -*-
"""
/***************************************************************************
    A QGIS plugin for Road contamination modelling for EMSURE Project
                              -------------------
        begin                : 2015-04-20
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Luigi Pirelli (for EMSURE project)º
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

import os
from PyQt4 import QtCore, QtGui, uic

from project_tab_manager import ProjectTabManager
from fleet_composition_tab_manager import FleetCompositionTabManager

# FORM_CLASS, _ = uic.loadUiType(os.path.join(
#     os.path.dirname(__file__), 'ui', 'qtraffic_dialog_base.ui'))
# 
# class QTrafficDockWidget(FORM_CLASS):
from ui.qtraffic_dialog_base_ui import Ui_qtraffic_dockWidget
from bzrlib.doc_generate.conf import project

class QTrafficDockWidget(QtGui.QDockWidget, Ui_qtraffic_dockWidget):
    
    def __init__(self, parent=None, pluginInstance=None):
        """Constructor."""
        super(QTrafficDockWidget, self).__init__(parent)
        self.parent = pluginInstance
        
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        # init all tab managers
        # I decided to avoid strict class derivation and use aggregation 
        # to facilitate maintenance to other peaple not practical in OOP
        
        # init project tab manager
        self.projectTabManager = ProjectTabManager(self)
        self.projectTabManager.projectLoaded.connect(self.setTabsOnCurrentProject)
        
        # init Fleet Composition tab Manager
        self.fleetCompostionTabManager = FleetCompositionTabManager(self)
        self.fleetCompostionTabManager.projectModified.connect(self.projectTabManager.setProjectModified)
        
    def setTabsOnCurrentProject(self):
        ''' A new project has loaded => set all tabs basing on that project
        '''
        # get project
        project = self.projectTabManager.getProject()
        
        # set status for all tabls
        self.fleetCompostionTabManager.setProject(project)
        