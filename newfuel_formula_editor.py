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

import json
from PyQt4 import QtGui
from ui.newfuel_formula_editor_dialog import Ui_newFuelFormula_dialog

class NewFuelFormulaEditor(QtGui.QDialog, Ui_newFuelFormula_dialog):
    
    def __init__(self, parent=None, project=None):
        """Constructor."""
        super(SearchPlusDockWidget, self).__init__(parent)
        
        # parent is the dock widget with all graphical elements
        self.plugin = parent.parent

        # init some globals
        self.project = project
        self.applicationPath = os.path.dirname(os.path.realpath(__file__))
        self.project = None
        self.projectPath = os.path.dirname(  self.project.fileName() )
        self.formulaDict = None

        # Set up the user interface from Designer.
        self.setupUi(self)
        
        # load formula file
        self.readFormulaConf()
        if not self.formulaDict:
            return
        
        # set up interface basing on formula config file
    
    def readFormulaConf(self):
        ''' Read the JSON configuration file where are set all emission functions for New Fuels
        '''
        if not project:
            return
        
        # get the conf filename
        key = 'General.InputFileDefinition.gui/Formulas'
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
            QgsMessageLog.logMessage(traceback.format_exc(), self.plugin.pluginTag, QgsMessageLog.CRITICAL)
            self.plugin.iface.messageBar().pushMessage(self.plugin.tr("Error loading formula conf file. Error: %s" % str(ex)), QgsMessageBar.CRITICAL)
            return
    
    def setUpGuiBasingOnConf(self):
        ''' Update current dialog interface adding tabs depending on json config
        '''
        if not self.formulaDict:
            return
        
        # create fist level of tab related to VehicleType
        print(self.formulaDict)

# if __name__ == '__main__':
#     # for command-line arguments
#     import sys
# 
#     # Create the GUI application
#     app = QtGui.QApplication(sys.argv)
#     
#     # load project
#     
#     
# 
#     # start the Qt main loop execution, exiting from this script
#     # with the same return code of Qt application
#     sys.exit(app.exec_())
