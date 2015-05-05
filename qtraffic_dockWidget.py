# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QTrafficDockWidget
                                 A QGIS plugin
 Road contamination modelling for EMSURE Project
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
import sys
import traceback
import json
import collections
from PyQt4 import QtCore, QtGui, QtWebKit, uic
from qgis.core import QgsLogger

# FORM_CLASS, _ = uic.loadUiType(os.path.join(
#     os.path.dirname(__file__), 'ui', 'qtraffic_dialog_base.ui'))
# 
# class QTrafficDockWidget(FORM_CLASS):

from ui.qtraffic_dialog_base_ui import Ui_qtraffic_dockWidget
from PyQt4.pyqtconfig import QtWebKitModuleMakefile

class DebugWebPage(QtWebKit.QWebPage):
    ''' custom webpage used to avoid interruption of messagebox by QT during debugging
    '''
    def __init__(self, parent):
        super(DebugWebPage, self).__init__(parent)
    
    @QtCore.pyqtSlot()
    def shouldInterruptJavaScript(self):
        return False

class QTrafficDockWidget(QtGui.QDockWidget, Ui_qtraffic_dockWidget):
    def __init__(self, parent=None):
        """Constructor."""
        super(QTrafficDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        parent.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self)
        
        # set event selecting roadClasses
        self.roadTypes_listWidget.itemClicked.connect(self.showRoadClassGui)
        
        # init some globals
        self.vehicleClassesDict = None # it will be a dict
        self.applicationPath = os.path.dirname(os.path.realpath(__file__))

        # set webView setting
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.JavascriptCanAccessClipboard, False)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.SpatialNavigationEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.PrintElementBackgrounds, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.OfflineStorageDatabaseEnabled, False)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.LocalStorageEnabled, False)
        #QtWebKit.QWebSettings.globalSettings().globalSettings().enablePersistentStorage(QtCore.QDir.tempPath())
        
        # load JS conde foreach webview to avoid syncronise with load signal
        self.initJsInWebview()
        
        # load last saved conf pointed in settings
        self.loadConfiguration()
        
        # set conf gui basing on settings
        self.setConfigGui()
    
    def loadConfiguration(self):
        ''' Function to load last conf get from settings
        '''
        defaultVehicleClasses = os.path.join(self.applicationPath, 'config', 'VehicleDistributionClasses', 'FleetDistribution.json')
        settings = QtCore.QSettings()
        vehicleClassesJson = settings.value('/QTraffic/vehicleClasses', defaultVehicleClasses)
        
        # load json conf
        try:
            with open(vehicleClassesJson) as confFile:
                # loaded in and OrderedDict to allow maintaining the order of classes
                # contained in the json file. This will be reflected in the order
                # shown in the sunburst visualization/editor
                self.vehicleClassesDict = json.load(confFile, object_pairs_hook=collections.OrderedDict)
        except Exception as ex:
            self.vehicleClassesDict = None
            
            traceback.print_exc()
            raise ex
    
    def setConfigGui(self):
        ''' set configuration GUI basing on loaded configration
        '''
        if not self.vehicleClassesDict:
            return
        
        roadTypes = self.vehicleClassesDict['children']
        for roadType in roadTypes:
            # add class in the list of classes
            self.roadTypes_listWidget.addItem(roadType['name'])
    
    def initJsInWebview(self):
        ''' Load sunburst JS code for each webview. JSOn file will be loaded
            separately
        '''
        webPage = os.path.join(self.applicationPath, "sunburst-d3-visualizator", "fiddle_BmW2q.html")

        for tabIndex in range(self.fleetComposition_tabs.count()):
            # get tab name
            tabWidget = self.fleetComposition_tabs.widget(tabIndex)
            webView = tabWidget.findChildren(QtWebKit.QWebView)[0] # assume only a webview is present in the tab
            
            # create a curstom webpage to avoid interruption by qt during debugging
            # have to be removed in production and leaved the default QWebPage
            debugWebPage = DebugWebPage(webView)
            webView.setPage(debugWebPage)
            
            webView.load(QtCore.QUrl(webPage))
        
    def showRoadClassGui(self, roadTypeItem):
        ''' Set sunbust UI for each tab category
        '''
        # first reload all web pages to reset them
        self.initJsInWebview()
        
        # then load config for each vehicle tab
        currentRoadType = roadTypeItem.text()
        
        vehicleClasses = self.getChildrensByName(self.vehicleClassesDict, currentRoadType)
        
        # for each tab get it's specific configuration toload in the webview tab
        for tabIndex in range(self.fleetComposition_tabs.count()):
            # get tab name
            tabWidget = self.fleetComposition_tabs.widget(tabIndex)
            vehicleClass = self.fleetComposition_tabs.tabText(tabIndex)
            
            # get confguration for the current vechicle class
            vehicleClassConf = self.getChildrensByName(vehicleClasses, vehicleClass)
            if vehicleClassConf:
                # convert in json string
                jsonString = json.dumps(vehicleClassConf)
                
                # init webview basing on json configuration
                webView = tabWidget.findChildren(QtWebKit.QWebView)[0] # assume only a webview is present in the tab
                print webView.objectName()

                JsCommand = "showJson(%s)" % jsonString
                QgsLogger.debug(self.tr("Load config with with JS command: %s" % JsCommand))
                
                webView.page().mainFrame().evaluateJavaScript(JsCommand)
    
    def getChildrensByName(self, input, name):
        ''' Traverse a dict to get children
            related to a specified name field value
            The algorith assume there is univoqe name to find =>
            if there are more, only the first will be get.
            For this reason it's imporant to pass a correct dict already
            purged of duplicated in the upper nodes
        '''
        if isinstance(input, dict):
            keys = input.keys()
            if 'name' in keys:
                if input['name'] == name:
                    return input
                
                elif 'children' in keys:
                    return self.getChildrensByName(input['children'], name)
                
                else:
                    return None
                
            else:
                return None
            
        elif isinstance(input, list):
            found = None
            for children in input:
                found = self.getChildrensByName(children, name)
                if found:
                    return found
            return found
