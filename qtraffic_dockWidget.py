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
import sys
import traceback
import json
import collections
import time
from PyQt4 import QtCore, QtGui, QtWebKit, uic
from qgis.core import QgsLogger

from sunburst_d3_editor.sunburst_editor_bridge import SunburstEditorBridge 

# FORM_CLASS, _ = uic.loadUiType(os.path.join(
#     os.path.dirname(__file__), 'ui', 'qtraffic_dialog_base.ui'))
# 
# class QTrafficDockWidget(FORM_CLASS):
from ui.qtraffic_dialog_base_ui import Ui_qtraffic_dockWidget
from Crypto import SelfTest

class DebugWebPage(QtWebKit.QWebPage):
    ''' custom webpage used to avoid interruption of messagebox by QT during debugging
    '''
    def __init__(self, parent):
        super(DebugWebPage, self).__init__(parent)
    
    @QtCore.pyqtSlot()
    def shouldInterruptJavaScript(self):
        return False

class QTrafficDockWidget(QtGui.QDockWidget, Ui_qtraffic_dockWidget):
    
    # events to coordinate interface
    configurationLoaded = QtCore.pyqtSignal()
    jsInitialised = QtCore.pyqtSignal()
    
    def __init__(self, parent=None, pluginInstance=None):
        """Constructor."""
        super(QTrafficDockWidget, self).__init__(parent)
        self.parent = pluginInstance
        
        # TODO: need reorganization to hide each tab management in specified class
        
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        parent.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self)
        
        # load configuration buttons
        self.loadDefaultConfiguration_button.clicked.connect(self.loadDefaultConfiguration)
        self.loadConfiguration_button.clicked.connect(self.loadNewConfiguration)
        
        # load configuration event listeners
        self.vehicleClassesDict = None
        self.configurationLoaded.connect(self.setConfigGui_step1)
        self.jsInitialised.connect(self.setConfigGui_step2)
        self.jsInitialised.connect(self.injectBridge)
        
        # set event selecting roadClasses
        self.roadTypes_listWidget.currentItemChanged.connect(self.showRoadClassDistribution)
        
        # init some globals
        self.vehicleClassesDict = None # it will be a dict
        self.applicationPath = os.path.dirname(os.path.realpath(__file__))
        self.sunburstEditorBridge = None

        # set webView setting
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.JavascriptCanAccessClipboard, False)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.SpatialNavigationEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.PrintElementBackgrounds, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.OfflineStorageDatabaseEnabled, False)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.LocalStorageEnabled, False)
        #QtWebKit.QWebSettings.globalSettings().globalSettings().enablePersistentStorage(QtCore.QDir.tempPath())
        
        # load last saved conf pointed in settings
        # emit configurationLoaded if successfully loaded
        self.loadConfiguration()
        
        # because configuration has been loaded and not modfied, then set save button to Unavailable
        self.saveConfiguration_button.setEnabled(False)
    
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
                self.configurationLoaded.emit()
        except Exception as ex:
            self.vehicleClassesDict = None
            
            traceback.print_exc()
            raise ex
    
    def loadDefaultConfiguration(self):
        ''' set the curret configuration as the default one get from plugin confg data
        '''
        defaultVehicleClasses = os.path.join(self.applicationPath, 'config', 'VehicleDistributionClasses', 'FleetDistribution.json')
        settings = QtCore.QSettings()
        settings.setValue('/QTraffic/vehicleClasses', defaultVehicleClasses)
        
        self.loadConfiguration()
    
    def loadNewConfiguration(self):
        ''' load a new configuration asking it's reference to the user
        '''
        # get last conf to start from its path
        defaultVehicleClasses = os.path.join(self.applicationPath, 'config', 'VehicleDistributionClasses', 'FleetDistribution.json')
        settings = QtCore.QSettings()
        vehicleClassesJson = settings.value('/QTraffic/vehicleClasses', defaultVehicleClasses)
        
        startPath = os.path.abspath( vehicleClassesJson )
        
        # ask for the new conf file
        newConfFile = QtGui.QFileDialog.getOpenFileName(self, "Select a JSON conf file", startPath, 
                                                        self.parent.tr("Json (*.json);;All (*)"))
        if not newConfFile:
            return
        
        # set new conf file as default
        vehicleClassesJson = settings.setValue('/QTraffic/vehicleClasses', newConfFile)
        
        self.loadConfiguration()
    
    def setConfigGui_step1(self):
        ''' first step to set configuration GUI basing on loaded configration
            this procedure start resetting the webpages
        '''
        if not self.vehicleClassesDict:
            return
        
        # reset all JS webpages to load new configuration
        self.initJsInWebview()
    
    def setConfigGui_step2(self):
        ''' second step to set configuration GUI basing on loaded configration
            this terminate loading road types
        '''
        # remove itemChanged event to avoid triggering during population
        try:
            self.roadTypes_listWidget.itemChanged.disconnect(self.manageItemChanged)
        except:
            pass
        
        # clean previous roadTypes to load the new ones
        self.roadTypes_listWidget.clear()
        
        roadTypes = self.vehicleClassesDict['children']
        for roadType in roadTypes:
            # create editable Item
            item = QtGui.QListWidgetItem(roadType['name'])
            
            # memorize roadType statistic in the UserRole of the item
            # to mantain the memory of modification
            # from this moment only the itemData is used and not self.vehicleClassesDict
            item.setData(QtCore.Qt.UserRole, roadType)

            # set editable
            item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
            
            # add class in the list of classes
            self.roadTypes_listWidget.addItem(item)

        # reconnect listener of item changes
        self.roadTypes_listWidget.itemChanged.connect(self.manageItemChanged)
    
    def manageItemChanged(self, item):
        ''' manage action to do when a item in roadTypes_listWidget is changed
            changes can be related to:
            A) road type rename
            B) road type insertion or deletion
            C) road type statistic update
            
            Actions are:
            A) enable Save button
        '''
        self.saveConfiguration_button.setEnabled(True)
    
    def injectBridge(self):
        ''' Iniect the class/object in JS used to receive json modification of the 
            statistic on a specific vehicle class
        '''
        # create bridge aqnd link event listener
        if self.sunburstEditorBridge:
            self.sunburstEditorBridge.deleteLater()
            
        self.sunburstEditorBridge = SunburstEditorBridge()
        self.sunburstEditorBridge.modified.connect(self.updateVehicleClassDistribution)
        
        for tabIndex in range(self.fleetComposition_tabs.count()):
            # get tab name
            tabWidget = self.fleetComposition_tabs.widget(tabIndex)
            webView = tabWidget.findChildren(QtWebKit.QWebView)[0] # assume only a webview is present in the tab

            webView.page().mainFrame().addToJavaScriptWindowObject("sunburstEditorBridge", self.sunburstEditorBridge)
    
    def initJsInWebview(self):
        ''' Load sunburst JS code for each webview. JSOn file will be loaded
            separately
        '''
        self.loadCounter = 0
        webPage = os.path.join(self.applicationPath, "sunburst_d3_editor", "sunburstEditor.html")
        
        for tabIndex in range(self.fleetComposition_tabs.count()):
            # get tab name
            tabWidget = self.fleetComposition_tabs.widget(tabIndex)
            webView = tabWidget.findChildren(QtWebKit.QWebView)[0] # assume only a webview is present in the tab
            
            # create a curstom webpage to avoid interruption by qt during debugging
            # have to be removed in production and leaved the default QWebPage
            debugWebPage = DebugWebPage(webView)
            webView.setPage(debugWebPage)
            
            webView.loadFinished.connect( self.loadFinishedCounter )
            webView.load(QtCore.QUrl(webPage))
        
        self.waitJSLoading()
    
    def loadFinishedCounter(self):
        ''' a countwer function to count how many webpages are loaded '''
        self.loadCounter += 1
    
    def waitJSLoading(self):
        ''' a tiem executed function that wait asynchronously the end of wep page loading
            At the end emit jsInitialised signal
        '''  
        if (self.loadCounter < self.fleetComposition_tabs.count()):
            timer = QtCore.QTimer.singleShot(100, self.waitJSLoading)
        else:
            # disconnect events for the load counter
            for tabIndex in range(self.fleetComposition_tabs.count()):
                # get tab name
                tabWidget = self.fleetComposition_tabs.widget(tabIndex)
                webView = tabWidget.findChildren(QtWebKit.QWebView)[0] # assume only a webview is present in the tab
                
                webView.loadFinished.disconnect( self.loadFinishedCounter )
            
            # notify that webpages are correctly initialised
            self.jsInitialised.emit()        
    
    def updateVehicleClassDistribution(self, vehicleDistribution):
        ''' Function to update the road configuration json basing on values
            set in the sunburst editor
        '''
        # get curret roadType distribution
        currentItem = self.roadTypes_listWidget.currentItem()
        vehicleClasses = currentItem.data(QtCore.Qt.UserRole)
        
        # update self.vehicleClassesDict basig on new distribution
        vechicleClassName = vehicleDistribution['name']
        vehicleClassConf = self.getChildrensByName(vehicleClasses, vechicleClassName)
        vehicleClassConf['children'] = vehicleDistribution['children']
        
        # then memorize new vehicleClasses in the item data (UserRole)
        currentItem.setData(QtCore.Qt.UserRole, vehicleClasses)
    
    def showRoadClassDistribution(self, currentRoadTypeItem, previousRoadTypeItem):
        ''' Set sunbust UI for each tab category
        '''
        # get classes from itemData (UserRole)
        vehicleClasses = currentRoadTypeItem.data(QtCore.Qt.UserRole)
        
        # then load config for each vehicle tab
        # for each tab get it's specific configuration to load in the webview tab
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
                QgsLogger.debug(self.parent.tr("Load config with with JS command: %s" % JsCommand), 3)
                
                webView.page().mainFrame().evaluateJavaScript(JsCommand)
    
    def getChildrensByName(self, input, name):
        ''' Traverse a dict to get children
            related to a specified name field value
            The algorithm assume there is univoque name to find =>
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
