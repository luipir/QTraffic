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

from PyQt4 import QtGui, QtCore, uic

# FORM_CLASS, _ = uic.loadUiType(os.path.join(
#     os.path.dirname(__file__), 'ui', 'qtraffic_dialog_base.ui'))
# 
# class QTrafficDockWidget(FORM_CLASS):

import os
import sys
from PyQt4 import QtCore, QtGui, QtWebKit

from ui.qtraffic_dialog_base_ui import Ui_qtraffic_dockWidget

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

        # set webView setting
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.JavascriptCanAccessClipboard, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.SpatialNavigationEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.PrintElementBackgrounds, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.OfflineStorageDatabaseEnabled, True)
        QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.LocalStorageEnabled, True)
        QtWebKit.QWebSettings.globalSettings().globalSettings().enablePersistentStorage(QtCore.QDir.tempPath())
        
        self.loadPage()
        
    def loadPage(self):
        self.applicationPath = os.path.dirname(os.path.realpath(__file__))
        webPage = os.path.join(self.applicationPath, "sunburst-d3-visualizator", "fiddle_BmW2q.html")
        self.passengerCars_webView.load(QtCore.QUrl(webPage))
