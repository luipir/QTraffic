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

import os
import sys
import traceback
import json
import collections
import time
import shutil
from PyQt4 import QtCore, QtGui, QtWebKit, uic
from qgis.core import (QgsLogger,
                       QgsMessageLog)
from qgis.gui import (QgsMessageBar)
from qgis.utils import iface

from sunburst_d3_editor.sunburst_editor_bridge import SunburstEditorBridge
from custom_widgets.spinbox_delegate import SpinBoxDelegate

class DebugWebPage(QtWebKit.QWebPage):
    ''' custom webpage used to avoid interruption of messagebox by QT during debugging
    '''
    def __init__(self, parent):
        super(DebugWebPage, self).__init__(parent)
    
    @QtCore.pyqtSlot()
    def shouldInterruptJavaScript(self):
        return False

class FleetCompositionTabManager(QtCore.QObject):
    ''' Class to hide managing of Fleet Compostion configuration
    '''
    # events to coordinate interface
    configurationLoaded = QtCore.pyqtSignal(bool)
    jsInitialised = QtCore.pyqtSignal()
    projectModified = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        '''constructor'''
        super(FleetCompositionTabManager, self).__init__(parent)
        
        # parent is the dock widget with all graphical elements
        self.gui = parent
        
        # init some globals
        self.vehicleClassesDict = None # it will be a dict
        self.sunburstEditorBridge = None
        self.project = None
        self.projectPath = None
        self.tabIndex = None
        
        # retrieve the current tab index
        self.initTabTabIndex()
        
        # create or remove new RoadTypes
        self.gui.newRoadType_button.setEnabled(False)
        self.gui.removeRoadType_button.setEnabled(False)
        self.gui.newRoadType_button.clicked.connect(self.createNewRoadType)
        self.gui.removeRoadType_button.clicked.connect(self.removeRoadType)

        # set item editable witha spinbox
        spinBoxDelegate = SpinBoxDelegate()
        self.gui.roadTypes_listWidget.setItemDelegate(spinBoxDelegate)

        # load configuration buttons
        self.gui.loadDefaultConfiguration_button.clicked.connect(self.loadDefaultConfiguration)
        self.gui.loadConfiguration_button.clicked.connect(self.loadNewConfiguration)
        
        # load configuration event listeners
        self.configurationLoaded.connect(self.setConfigGui_step1)
        self.jsInitialised.connect(self.injectBridge)
        self.jsInitialised.connect(self.setConfigGui_step2)
        
        # set event selecting roadClasses
        self.gui.roadTypes_listWidget.currentItemChanged.connect(self.showRoadClassDistribution)
        
        # set webView setting
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.JavascriptCanAccessClipboard, False)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.SpatialNavigationEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.PrintElementBackgrounds, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.OfflineStorageDatabaseEnabled, False)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.LocalStorageEnabled, False)
        #QtWebKit.QWebSettings.globalSettings().globalSettings().enablePersistentStorage(QtCore.QDir.tempPath())
        
        # add listener to save actual configuration
        self.gui.saveConfiguration_button.clicked.connect(self.saveConfiguration)
        self.gui.saveConfiguration_button.setEnabled(False)
        
        # disable current tab because no project has been loaded yet
        self.gui.tabWidget.setTabEnabled(self.tabIndex, False)
    
    def setFleetGUIModified(self, status=True):
        ''' Set fleet composition tab interface basing if fleet statistic has modified or not
            tab gui will have:
            1) Save button enabled
            2) tab name with a * tail
        '''
        # do nothing if the current status is the same
        if status == self.gui.saveConfiguration_button.isEnabled():
            return
        
        self.gui.saveConfiguration_button.setEnabled(status)
        
        # set tab text
        text = self.gui.tabWidget.tabText(self.tabIndex)
        if status:
            # set tab text = tab text + '*' to show that project has been modified
            self.gui.tabWidget.setTabText(self.tabIndex, text + '*')
        else:
            # set tab text = tab text - last '*' to show that project is not modifed
            self.gui.tabWidget.setTabText(self.tabIndex, text[0:-1])
            
    
    def initTabTabIndex(self):
        ''' Retrieve what tab index refer the current tab manager
        '''
        for tabIndex in range(self.gui.tabWidget.count()):
            if self.gui.tabWidget.tabText(tabIndex) == "Fleet Composition":
                self.tabIndex = tabIndex

    
    def setProject(self, project=None):
        ''' setting the new project on which the tab is based
        '''
        self.project = project
        if self.project:
            # set some globals
            confFileName = self.project.fileName()
            self.projectPath = os.path.dirname(confFileName)

            # emit configurationLoaded with the status of loading
            self.loadConfiguration()
            
            # enable current tab because project has been loaded
            self.gui.tabWidget.setTabEnabled(self.tabIndex, True)
        
        else:
            # disable current tab because no project has been loaded yet
            self.gui.tabWidget.setTabEnabled(self.tabIndex, False)
    
    def createNewRoadType(self):
        ''' Method to add a new road type starting from the default road tyep configuration
        '''
        if not self.vehicleClassesDict:
            return
        
        # load default json conf
        defaultVehicleClassesDict = None
        try:
            with open(self.gui.defaultVehicleClassesFileName) as confFile:
                # loaded in and OrderedDict to allow maintaining the order of classes
                # contained in the json file. This will be reflected in the order
                # shown in the sunburst visualization/editor
                defaultVehicleClassesDict = json.load(confFile, object_pairs_hook=collections.OrderedDict)
        except Exception as ex:
            message = self.tr("Error loading Default conf JSON file %s") % self.gui.defaultVehicleClassesFileName
            iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return
        
        # assume that the default roadType class is the fist one of the loaded configuration
        if not defaultVehicleClassesDict or len(defaultVehicleClassesDict['children']) == 0:
            message = self.tr("No road types set in the default configuration file: %s") % self.gui.defaultVehicleClassesFileName
            iface.messageBar().pushMessage(message, QgsMessageBar.CRITICAL)
            return 
            
        defaultRoadType = defaultVehicleClassesDict['children'][0]
        
        # get the maximum road type name to set the new name as max+1
        # specifications says that roadType have to be integer and not free string
        roadTypeNames = [ int(x['name']) for x in self.vehicleClassesDict['children'] ]
        newRoadTypeName = str( max(roadTypeNames) + 1 )

        # clone roadType dict and rename it's roadTpe name witha a default name
        newRoadType = collections.OrderedDict(defaultRoadType)
        newRoadType['name'] = newRoadTypeName
        newRoadType['converted'] = 'F_Type_' + newRoadType['name']
        #newRoadType['name'] = defaultRoadType['name'] + "_%d" % len(self.vehicleClassesDict['children'])
        
        # add the new roadType to the actual self.vehicleClassesDict
        self.vehicleClassesDict['children'].append(newRoadType)
        
        # because current config has modifed => set save button enabled
        self.setFleetGUIModified()
    
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
            message = self.tr("At least a road type would be present")
            iface.messageBar().pushMessage(message, QgsMessageBar.WARNING)
            return
        
        # check if current Fleet distribution has been modified to 
        # avoid to remove modifications
        if self.isModified():
            title = self.tr("Warning")
            message = self.tr("Fleet distribution modified, if you continue you can overwrite modifications. Continue?")
            ret = QtGui.QMessageBox.question(self.gui, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        # get the name of selected row type
        selectedItem = self.gui.roadTypes_listWidget.currentItem()
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
        return self.gui.saveConfiguration_button.isEnabled()
                
    def saveConfiguration(self):
        ''' Method to save configuration contained in teh QWidgetList
            QWidgetList contain a list of RoadTypes and every Item belong in it's UserRole data
            a dictionary of statistic of the lreated roadType
        '''
        currentVehicleClassesJson = self.project.value('/FleetComposition/fleetComposition', self.gui.defaultVehicleClassesFileName)

        # check if json is relative path or absolute
        if not os.path.isabs(currentVehicleClassesJson):
            currentVehicleClassesJson = os.path.join(self.projectPath, currentVehicleClassesJson)
        
        # now iterate on all roadTypes to create the dictionary to save
        newVehicleClassesDict = collections.OrderedDict( self.vehicleClassesDict )
        newVehicleClassesDict['children'] = []
        
        allItems = self.gui.roadTypes_listWidget.findItems('*', QtCore.Qt.MatchWrap | QtCore.Qt.MatchWildcard)
        for item in allItems:
            roadTypeDistribution = item.data(QtCore.Qt.UserRole)
            
            newVehicleClassesDict['children'].append(roadTypeDistribution)
        
        # now save newVehicleClassesDict in the selected file
        try:
            message = self.tr('Saving conf on file %s' % currentVehicleClassesJson)
            QgsMessageLog.logMessage(message, 'QTraffic', QgsMessageLog.INFO)
            
            with open(currentVehicleClassesJson, 'w') as outFile:
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
            QgsMessageLog.logMessage(traceback.format_exc(), 'QTraffic', QgsMessageLog.CRITICAL)
            iface.messageBar().pushMessage(self.tr("Error saving Conf JSON file. Please check the log"), QgsMessageBar.CRITICAL)
            return
        
        # set save button status
        self.setFleetGUIModified(False)
    
    def loadConfiguration(self):
        ''' Function to load last conf get from settings
        '''
        if not self.project:
            return
        
        # from th eproject, get JSON filename to load
        currentVehicleClassesJson = self.project.value('/FleetComposition/fleetComposition', self.gui.defaultVehicleClassesFileName)
        
        # check if json is relative path or absolute
        if not os.path.isabs(currentVehicleClassesJson):
            currentVehicleClassesJson = os.path.join(self.projectPath, currentVehicleClassesJson)
        
        # load json conf
        try:
            with open(currentVehicleClassesJson) as confFile:
                # loaded in and OrderedDict to allow maintaining the order of classes
                # contained in the json file. This will be reflected in the order
                # shown in the sunburst visualization/editor
                self.vehicleClassesDict = json.load(confFile, object_pairs_hook=collections.OrderedDict)
                
                self.configurationLoaded.emit(True)
                
        except Exception as ex:
            self.vehicleClassesDict = None
            
            QgsMessageLog.logMessage(traceback.format_exc(), 'QTraffic', QgsMessageLog.CRITICAL)
            iface.messageBar().pushMessage(self.tr("Error loading Conf JSON file. Please check the log"), QgsMessageBar.CRITICAL)
            return
    
    def loadDefaultConfiguration(self):
        ''' set the curret configuration as the default one get from plugin confg data
        '''
        # check if current Fleet distribution has been modified to 
        # avoid to remove modifications
        if self.isModified():
            title = self.tr("Warning")
            message = self.tr("Fleet distribution modified, if you continue you can overwrite modifications. Continue?")
            ret = QtGui.QMessageBox.question(self.gui, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        currentVehicleClassesJson = self.project.value('/FleetComposition/fleetComposition', '')
        
        # check if json is relative path or absolute
        if not os.path.isabs(currentVehicleClassesJson):
            currentVehicleClassesJson = os.path.join(self.projectPath, currentVehicleClassesJson)
        
        # copy default json file as current json file
        shutil.copyfile(self.gui.defaultVehicleClassesFileName, currentVehicleClassesJson)
        
        self.loadConfiguration()
    
    def loadNewConfiguration(self):
        ''' load a new configuration asking it's reference to the user
        '''
        # check if current Fleet distribution has been modified to 
        # avoid to remove modifications
        if self.isModified():
            title = self.tr("Warning")
            message = self.tr("Fleet distribution modified, if you continue you can overwrite modifications. Continue?")
            ret = QtGui.QMessageBox.question(self.gui, title, message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                return
        
        # get last conf to start from its path
        currentVehicleClassesJson = self.project.value('/FleetComposition/fleetComposition', self.gui.defaultVehicleClassesFileName)
        if not os.path.isabs(currentVehicleClassesJson):
            currentVehicleClassesJson = os.path.join(self.projectPath, currentVehicleClassesJson)
        
        startPath = os.path.abspath( currentVehicleClassesJson )
        
        # ask for the new conf file
        newConfFile = QtGui.QFileDialog.getOpenFileName(self.gui, "Select a JSON conf file", startPath, 
                                                        self.tr("Json (*.json);;All (*)"))
        if not newConfFile:
            return
        
        # copy the new one on the current one
        shutil.copyfile(newConfFile, currentVehicleClassesJson)
        
        self.loadConfiguration()
    
    def setConfigGui_step1(self, configurationLoaded=False):
        ''' first step to set configuration GUI basing on loaded configration
            this procedure start resetting the webpages
        '''
        if not self.vehicleClassesDict:
            return
        
        # because loaded configuration we can add and remove road type classes
        self.gui.newRoadType_button.setEnabled(True)
        self.gui.removeRoadType_button.setEnabled(True)
        
        # if new config is loaded, then save button is disabled
        self.setFleetGUIModified(not configurationLoaded)
        
        # reset all JS webpages to load new configuration
        self.initJsInWebview()
    
    def setConfigGui_step2(self):
        ''' second step to set configuration GUI basing on loaded configration
            this terminate loading road types
        '''
        # remove itemChanged event to avoid triggering during population
        try:
            self.gui.roadTypes_listWidget.itemChanged.disconnect(self.manageItemChanged)
        except:
            pass
        
        # clean previous roadTypes to load the new ones
        self.gui.roadTypes_listWidget.clear()
        
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
            self.gui.roadTypes_listWidget.addItem(item)

        # reconnect listener of item changes
        self.gui.roadTypes_listWidget.itemChanged.connect(self.manageItemChanged)
    

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
        vehicleClasses['converted'] = 'F_Type_' + item.text()
        item.setData(QtCore.Qt.UserRole, vehicleClasses)
        
        self.setFleetGUIModified()
    
    def injectBridge(self):
        ''' Iniect the class/object in JS used to receive json modification of the 
            statistic on a specific vehicle class
        '''
        # create bridge aqnd link event listener
        if self.sunburstEditorBridge:
            self.sunburstEditorBridge.deleteLater()
            
        self.sunburstEditorBridge = SunburstEditorBridge()
        self.sunburstEditorBridge.modified.connect(self.updateVehicleClassDistribution)
        
        for tabIndex in range(self.gui.fleetComposition_tabs.count()):
            # get tab name
            tabWidget = self.gui.fleetComposition_tabs.widget(tabIndex)
            webView = tabWidget.findChildren(QtWebKit.QWebView)[0] # assume only a webview is present in the tab

            webView.page().mainFrame().addToJavaScriptWindowObject("sunburstEditorBridge", self.sunburstEditorBridge)
    
    def initJsInWebview(self):
        ''' Load sunburst JS code for each webview. JSOn file will be loaded
            separately
        '''
        QtWebKit.QWebSettings.clearMemoryCaches()
        
        self.loadCounter = 0
        webPage = os.path.join(self.gui.applicationPath, "sunburst_d3_editor", "sunburstEditor.html")
        
        for tabIndex in range(self.gui.fleetComposition_tabs.count()):
            # get tab name
            tabWidget = self.gui.fleetComposition_tabs.widget(tabIndex)
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
        if (self.loadCounter < self.gui.fleetComposition_tabs.count()):
            timer = QtCore.QTimer.singleShot(100, self.waitJSLoading)
        else:
            # disconnect events for the load counter
            for tabIndex in range(self.gui.fleetComposition_tabs.count()):
                # get tab name
                tabWidget = self.gui.fleetComposition_tabs.widget(tabIndex)
                webView = tabWidget.findChildren(QtWebKit.QWebView)[0] # assume only a webview is present in the tab
                
                webView.loadFinished.disconnect( self.loadFinishedCounter )
            
            # notify that webpages are correctly initialised
            self.jsInitialised.emit()        
    
    def updateVehicleClassDistribution(self, vehicleDistribution):
        ''' Function to update the road configuration json basing on values
            set in the sunburst editor
        '''
        # get curret roadType distribution
        currentItem = self.gui.roadTypes_listWidget.currentItem()
        roadTypeDistribution = currentItem.data(QtCore.Qt.UserRole)
        
        # update self.vehicleClassesDict basig on new distribution
        vechicleClassName = vehicleDistribution['name']
        vehicleClassConf = self.getChildrensByName(roadTypeDistribution, vechicleClassName)
        vehicleClassConf['children'] = vehicleDistribution['children']
        
        # then memorize new vehicleClasses in the item data (UserRole)
        currentItem.setData(QtCore.Qt.UserRole, roadTypeDistribution)
    
    def showRoadClassDistribution(self, currentRoadTypeItem, previousRoadTypeItem):
        ''' Set sunburst UI for each tab category
        '''
        # manage event in case of list clear
        if not currentRoadTypeItem:
            return
        
        # get classes from itemData (UserRole)
        vehicleClasses = currentRoadTypeItem.data(QtCore.Qt.UserRole)
        
        # then load config for each vehicle tab
        # for each tab get it's specific configuration to load in the webview tab
        for tabIndex in range(self.gui.fleetComposition_tabs.count()):
            # get tab name
            tabWidget = self.gui.fleetComposition_tabs.widget(tabIndex)
            vehicleClass = self.gui.fleetComposition_tabs.tabText(tabIndex)
            
            # get confguration for the current vechicle class
            vehicleClassConf = self.getChildrensByName(vehicleClasses, vehicleClass)
            if vehicleClassConf:
                # convert in json string
                jsonString = json.dumps(vehicleClassConf)
                
                # init webview basing on json configuration
                webView = tabWidget.findChildren(QtWebKit.QWebView)[0] # assume only a webview is present in the tab
                print webView.objectName()

                JsCommand = "showJson(%s)" % jsonString
                QgsLogger.debug(self.tr("Load config with with JS command: %s" % JsCommand), 3)
                
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
    
    def currentRoadTypes(self):
        ''' Return the current list of roadType in the fleet distribution
            Beaware that this list comes from current memory status and could not
            reflect the json file if the fleet distribtion has been edited and not saved
        '''
        roadTypes = [ roadType['name'] for roadType in self.vehicleClassesDict['children'] ]
        return roadTypes

    def validate(self):
        ''' tab validation
        Mandatory:
            project have to be saved
        '''
        if self.isModified():
            message = self.tr("Validation error: Fleet distribution have to be saved")
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
    