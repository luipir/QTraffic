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

from qgis.utils import iface
from qgis.core import QgsMapLayerRegistry

from project_tab_manager import ProjectTabManager
from fleet_composition_tab_manager import FleetCompositionTabManager
from input_network_tab_manager import InputNetworkTabManager
from fuel_properties_tab_manager import FuelPropertiesTabManager
from output_tab_manager import OutputTabManager

# FORM_CLASS, _ = uic.loadUiType(os.path.join(
#     os.path.dirname(__file__), 'ui', 'qtraffic_dialog_base.ui'))
# 
# class QTrafficDockWidget(FORM_CLASS):
from ui.qtraffic_dialog_base_ui import Ui_qtraffic_dockWidget

class QTrafficDockWidget(QtGui.QDockWidget, Ui_qtraffic_dockWidget):
    
    def __init__(self, parent=None, pluginInstance=None):
        """Constructor."""
        super(QTrafficDockWidget, self).__init__(parent)
        self.parent = pluginInstance
        
        # init some globals
        self.applicationPath = os.path.dirname(os.path.realpath(__file__))
        self.defaultProjectFileName = os.path.join(self.applicationPath, 'config','defaultProject.ini')
        self.defaultVehicleClassesFileName = os.path.join(self.applicationPath, 'config', 'VehicleDistributionClasses', 'FleetDistribution.json')
        self.defaultNewFuelFormulaFileName = os.path.join(self.applicationPath, 'config', 'NewFuelFormulas.json')
        
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        
        # init tab managers
        self.inputNetworkTabManager = None
        self.fleetCompostionTabManager = None
        self.fuelPropertiesTabManager = None
        self.outputTabManager = None
        self.initTabs()
        
        # add listener that monitorise if layer is removed
        try:
            QgsMapLayerRegistry.instance().layerRemoved.disconnect(self.checkLayerDeletion)
        except:
            pass
        QgsMapLayerRegistry.instance().layerRemoved.connect(self.checkLayerDeletion)
    
    def initTabs(self):
        """ init all tab managers
        """
        # I decided to avoid strict class derivation and use aggregation 
        # to facilitate maintenance to other peaple not practical in OOP
        
        # init project tab manager
        self.projectTabManager = ProjectTabManager(self)
        self.projectTabManager.projectLoaded.connect(self.setTabsOnCurrentProject)
        
        # init Input Network tab manager
        if self.inputNetworkTabManager:
            self.inputNetworkTabManager.deleteLater()
        self.inputNetworkTabManager = InputNetworkTabManager(self)
        self.inputNetworkTabManager.projectModified.connect(self.projectTabManager.setProjectModified)
        
        # init Fleet Composition tab Manager
        if self.fleetCompostionTabManager:
            self.fleetCompostionTabManager.deleteLater()
        self.fleetCompostionTabManager = FleetCompositionTabManager(self)
        self.fleetCompostionTabManager.projectModified.connect(self.projectTabManager.setProjectModified)
        
        # fuel properties tab manager
        if self.fuelPropertiesTabManager:
            self.fuelPropertiesTabManager.deleteLater()
        self.fuelPropertiesTabManager = FuelPropertiesTabManager(self)
        self.fuelPropertiesTabManager.projectModified.connect(self.projectTabManager.setProjectModified)
        
        # output tab manager
        if self.outputTabManager:
            self.outputTabManager.deleteLater()
        self.outputTabManager = OutputTabManager(self)
        self.outputTabManager.projectModified.connect(self.projectTabManager.setProjectModified)
            
    def checkLayerDeletion(self, layerId):
        ''' Notify that road layer has been deletad and plugin can't be operative
        '''
        # don't fo forward if listener is not related to any instance
        if not iface:
            return
        
        roadLayerId = self.inputNetworkTabManager.getRoadLayerId()
        if not roadLayerId:
            return
        
        if layerId != roadLayerId:
            return
        
        # notify layer has been removed
        iface.messageBar().pushCritical('QTraffic', self.tr(u"Removed road layer. Please reload the plugin project!"))
        
        # reinitialize all tabs
        self.initTabs()
        
    def setTabsOnCurrentProject(self):
        ''' A new project has loaded => set all tabs basing on that project
        '''
        # get project
        project = self.projectTabManager.getProject()
        
        # set status for all tabls
        self.inputNetworkTabManager.setProject(project)
        self.fleetCompostionTabManager.setProject(project)
        self.fuelPropertiesTabManager.setProject(project)
        self.outputTabManager.setProject(project)
    
    def getRoadLayer(self):
        ''' Bridge method to get the current road layer
        '''
        return self.inputNetworkTabManager.getRoadLayer()
    
    def getRoadTypes(self):
        ''' Bridge method to get list of roadTypes edited in the fleetDistribution tab
        '''
        if not self.fleetCompostionTabManager:
            return []
        
        return self.fleetCompostionTabManager.currentRoadTypes()

    def validate(self):
        ''' Bridge method to allow inter tab validation
        '''
        if not self.projectTabManager.validate():
            return False
        
        if not self.inputNetworkTabManager.validate():
            return False
        
        if not self.fleetCompostionTabManager.validate():
            return False
        
        if not self.fuelPropertiesTabManager.validate():
            return False
        
        if not self.outputTabManager.validate():
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
    