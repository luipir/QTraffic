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

from PyQt4 import QtGui

from qgis.gui import QgsMapLayerProxyModel

from ui.qtraffic_select_layer_ui import Ui_selectLayer_dlg

class SelectLayerDialog(QtGui.QDialog, Ui_selectLayer_dlg):
    
    def __init__(self, parent=None, pluginInstance=None):
        """Constructor."""
        super(SelectLayerDialog, self).__init__(parent)
        self.setupUi(self)
        self.selectLayer_CBox.setFilters(QgsMapLayerProxyModel.VectorLayer)
        