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
from qgis.core import (QgsLogger,
                       QgsMessageLog)
from qgis.gui import (QgsMessageBar)

from sunburst_d3_editor.sunburst_editor_bridge import SunburstEditorBridge 

# FORM_CLASS, _ = uic.loadUiType(os.path.join(
#     os.path.dirname(__file__), 'ui', 'qtraffic_dialog_base.ui'))
# 
# class QTrafficDockWidget(FORM_CLASS):
from ui.qtraffic_dialog_base_ui import Ui_qtraffic_dockWidget

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
    configurationLoaded = QtCore.pyqtSignal(bool)
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
        
        # init some globals
        self.applicationPath = os.path.dirname(os.path.realpath(__file__))
        self.defaultVehicleClasses = os.path.join(self.applicationPath, 'config', 'VehicleDistributionClasses', 'FleetDistribution.json')
        self.currentConfFile = None
        self.vehicleClassesDict = None # it will be a dict
        self.sunburstEditorBridge = None
        
        # create or remove new RoadTypes
        self.newRoadType_button.setEnabled(False)
        self.removeRoadType_button.setEnabled(False)
        self.newRoadType_button.clicked.connect(self.createNewRoadType)
        self.removeRoadType_button.clicked.connect(self.removeRoadType)

        # load configuration buttons
        self.loadDefaultConfiguration_button.clicked.connect(self.loadDefaultConfiguration)
        self.loadConfiguration_button.clicked.connect(self.loadNewConfiguration)
        
        # load configuration event listeners
        self.configurationLoaded.connect(self.setConfigGui_step1)
        self.jsInitialised.connect(self.injectBridge)
        self.jsInitialised.connect(self.setConfigGui_step2)
        
        # set event selecting roadClasses
        self.roadTypes_listWidget.currentItemChanged.connect(self.showRoadClassDistribution)
        
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
        # emit configurationLoaded with the status of loading
        self.loadConfiguration()
        
        # add listener to save actual configuration
        self.saveConfiguration_button.clicked.connect(self.saveConfiguration)
    
    def createNewRoadType(self):
        ''' Method to add a new road type starting from the default road tyep configuration
        '''
        if not self.vehicleClassesDict:
            return
        
        # load default json conf
        defaultVehicleClassesDict = None
        try:
            with open(self.defaultVehicleClasses) as confFile:
                # loaded in and OrderedDict to allow maintaining the order of classes
                # contained in the json file. This will be reflected in the order
                # shown in the sunburst visualization/editor
                defaultVehicleClassesDict = json.load(confFile, object_pairs_hook=collections.OrderedDict)
        except Exception as ex:
            message = self.parent.tr("Error loading Default conf JSON file %s") % self.defaultVehicleClasses
            self.parent.iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return
        
        # assume that the default roadType class is the fist one of the loaded configuration
        if not defaultVehicleClassesDict or len(defaultVehicleClassesDict['children']) == 0:
            message = self.parent.tr("No road types set in the default configuration file: %s") % self.defaultVehicleClasses
            self.parent.iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return 
            
        defaultRoadType = defaultVehicleClassesDict['children'][0]
        
        # clone roadType dict and rename it's roadTpe name witha a default name
        newRoadType = collections.OrderedDict(defaultRoadType)
        newRoadType['name'] = defaultRoadType['name'] + "_%d" % len(self.vehicleClassesDict['children'])
        newRoadType['description'] = newRoadType['name']
        
        # add the new roadType to the actual self.vehicleClassesDict
        self.vehicleClassesDict['children'].append(newRoadType)
        
        # because current config has modifed => set save button enabled
        self.saveConfiguration_button.setEnabled(True)
    
        # reset GUI basing on new roadType
        self.setConfigGui_step1()
    
    def removeRoadType(self):
        ''' Remove a road type doing some check.
            A) At least a road type would be present
        '''
        if not self.vehicleClassesDict:
            return
        
        # check if there are at least two road type
        if len(self.vehicleClassesDict['children']) < 2:
            message = self.parent.tr("At least a road type would be present")
            self.parent.iface.messageBar().pushMessage(message, QgsMessageBar.WARNING)
            return
        
        # check if current Fleet distribution has been modified to 
        # avoid to remove modifications
        if self.isModified():
            title = self.parent.tr("Warning")
            message = self.parent.tr("Fleet distribution modified, if you continue you can overwrite modifications. Continue?")
            ret = QtGui.QMessageBox.question(None, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        # get the name of selected row type
        selectedItem = self.roadTypes_listWidget.currentItem()
        selectedRoadTypeName = selectedItem.text()
        
        # remove the selected Roat Type from self.vehicleClassesDict
        for index, roadType in enumerate( self.vehicleClassesDict['children'] ):
            if roadType['name'] == selectedRoadTypeName:
                # remove
                self.vehicleClassesDict['children'].pop(index)
                
                # reset GUI basing on new roadType
                # i do it inside the for loop to avoid reset interface if the element is not found
                self.setConfigGui_step1()
                break
    
    def isModified(self):
        ''' Return true if the curret fleet distribution is marked as modified
            The modified status is based on the status of Save button
        '''
        return self.saveConfiguration_button.isEnabled()
                
    def saveConfiguration(self):
        ''' Method to save configuration contained in teh QWidgetList
            QWidgetList contain a list of RoadTypes and every Item belong in it's UserRole data
            a dictionary of statistic of the lreated roadType
        '''
        settings = QtCore.QSettings()
        vehicleClassesJson = settings.value('/QTraffic/vehicleClasses', self.defaultVehicleClasses)
        startPath = os.path.abspath( vehicleClassesJson )
        
        # ask for the new conf file
        newConfFile = QtGui.QFileDialog.getSaveFileName(self, "Save as JSON file", startPath, self.parent.tr("Json (*.json);;All (*)"))
        if not newConfFile:
            return
        
        # now iterate on all roadTypes to create the dictionary to save
        newVehicleClassesDict = collections.OrderedDict( self.vehicleClassesDict )
        newVehicleClassesDict['children'] = []
        
        allItems = self.roadTypes_listWidget.findItems('*', QtCore.Qt.MatchWrap | QtCore.Qt.MatchWildcard)
        for item in allItems:
            roadTypeDistribution = item.data(QtCore.Qt.UserRole)
            
            newVehicleClassesDict['children'].append(roadTypeDistribution)
        
        # now save newVehicleClassesDict in the selected file
        try:
            message = self.parent.tr('Saving conf on file %s' % newConfFile)
            QgsMessageLog.logMessage(message, self.parent.pluginTag, QgsMessageLog.INFO)
            
            with open(newConfFile, 'w') as outFile:
                json.dump(newVehicleClassesDict, 
                          outFile, 
                          ensure_ascii=False, 
                          check_circular=True, 
                          allow_nan=True, 
                          cls=None, 
                          indent=2, # allow pretty formatting of the json
                          separators=None, 
                          encoding="utf-8", 
                          default=None, 
                          sort_keys=False) # to mantaine the oreding of the OrdererdDict
                
        except Exception as ex:
            QgsMessageLog.logMessage(traceback.format_exc(), self.parent.pluginTag, QgsMessageLog.CRITICAL)
            self.parent.iface.messageBar().pushMessage(self.parent.tr("Error saving Conf JSON file. Please check the log"), QgsMessageBar.CRITICAL)
            return
        
        # set new conf file as default
        settings.setValue('/QTraffic/vehicleClasses', newConfFile)
        
        # set save button status
        self.saveConfiguration_button.setEnabled(False)
    
    def loadConfiguration(self):
        ''' Function to load last conf get from settings
        '''
        settings = QtCore.QSettings()
        vehicleClassesJson = settings.value('/QTraffic/vehicleClasses', self.defaultVehicleClasses)
        
        # load json conf
        try:
            with open(vehicleClassesJson) as confFile:
                # loaded in and OrderedDict to allow maintaining the order of classes
                # contained in the json file. This will be reflected in the order
                # shown in the sunburst visualization/editor
                self.vehicleClassesDict = json.load(confFile, object_pairs_hook=collections.OrderedDict)
                
                # remember current conf file
                self.currentConfFile = vehicleClassesJson
                settings.setValue('/QTraffic/vehicleClasses', self.defaultVehicleClasses)
                
                self.configurationLoaded.emit(True)
        except Exception as ex:
            self.vehicleClassesDict = None
            
            QgsMessageLog.logMessage(traceback.format_exc(), self.parent.pluginTag, QgsMessageLog.CRITICAL)
            self.parent.iface.messageBar().pushMessage(self.parent.tr("Error loading Conf JSON file. Please check the log"), QgsMessageBar.CRITICAL)
            return
    
    def loadDefaultConfiguration(self):
        ''' set the curret configuration as the default one get from plugin confg data
        '''
        # check if current Fleet distribution has been modified to 
        # avoid to remove modifications
        if self.isModified():
            title = self.parent.tr("Warning")
            message = self.parent.tr("Fleet distribution modified, if you continue you can overwrite modifications. Continue?")
            ret = QtGui.QMessageBox.question(None, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        settings = QtCore.QSettings()
        settings.setValue('/QTraffic/vehicleClasses', self.defaultVehicleClasses)
        
        self.loadConfiguration()
    
    def loadNewConfiguration(self):
        ''' load a new configuration asking it's reference to the user
        '''
        # check if current Fleet distribution has been modified to 
        # avoid to remove modifications
        if self.isModified():
            title = self.parent.tr("Warning")
            message = self.parent.tr("Fleet distribution modified, if you continue you can overwrite modifications. Continue?")
            ret = QtGui.QMessageBox.question(None, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        # get last conf to start from its path
        settings = QtCore.QSettings()
        vehicleClassesJson = settings.value('/QTraffic/vehicleClasses', self.defaultVehicleClasses)
        
        startPath = os.path.abspath( vehicleClassesJson )
        
        # ask for the new conf file
        newConfFile = QtGui.QFileDialog.getOpenFileName(self, "Select a JSON conf file", startPath, 
                                                        self.parent.tr("Json (*.json);;All (*)"))
        if not newConfFile:
            return
        
        # set new conf file as default
        settings.setValue('/QTraffic/vehicleClasses', newConfFile)
        
        self.loadConfiguration()
    
    def setConfigGui_step1(self, configurationLoaded=False):
        ''' first step to set configuration GUI basing on loaded configration
            this procedure start resetting the webpages
        '''
        if not self.vehicleClassesDict:
            return
        
        # because loaded configuration we can add and remove road type classes
        self.newRoadType_button.setEnabled(True)
        self.removeRoadType_button.setEnabled(True)
        
        # if new config is loaded, then save button is disabled
        self.saveConfiguration_button.setEnabled(not configurationLoaded)
        
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
            A) manage if current Item has bee renamed
            B) enable Save button
        '''
        # udate roadType name in case evend is due to renaming class
        # TODO: check that road type name is not duplicated
        vehicleClasses = item.data(QtCore.Qt.UserRole)
        vehicleClasses['name'] = item.text()
        vehicleClasses['description'] = item.text() # TODO: for the moment name and description are equal
        item.setData(QtCore.Qt.UserRole, vehicleClasses)
        
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
        QtWebKit.QWebSettings.clearMemoryCaches()
        
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
            webView.load(QtCore.QUrl.fromLocalFile(webPage))
        
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
        roadTypeDistribution = currentItem.data(QtCore.Qt.UserRole)
        
        # update self.vehicleClassesDict basig on new distribution
        vechicleClassName = vehicleDistribution['name']
        vehicleClassConf = self.getChildrensByName(roadTypeDistribution, vechicleClassName)
        vehicleClassConf['children'] = vehicleDistribution['children']
        
        # then memorize new vehicleClasses in the item data (UserRole)
        currentItem.setData(QtCore.Qt.UserRole, roadTypeDistribution)
    
    def showRoadClassDistribution(self, currentRoadTypeItem, previousRoadTypeItem):
        ''' Set sunbust UI for each tab category
        '''
        # manage event in case of list clear
        if not currentRoadTypeItem:
            return
        
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
