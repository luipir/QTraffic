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

import collections
import traceback
import json
from PyQt4 import QtCore
from qgis.core import QgsLogger

class SunburstEditorBridge(QtCore.QObject):
    ''' Class used to receive statistic modification from JS and bridge to Python
    '''
    modified = QtCore.pyqtSignal(collections.OrderedDict)    
    
    def __init__(self):
        """Constructor."""
        super(SunburstEditorBridge, self).__init__()
        
        self.statistic = None
        
    @QtCore.pyqtSlot(str)
    def modifiedStatistic(self, statistic=None):
        '''
        slot emitted by JS to communicate that a vehicle class statistic
        has changed 
        '''
        QgsLogger.debug("Statistic = %s" % statistic, 3)
        
        self.statistic = None
        if statistic:
            try:
                # parse JSON
                self.statistic =   json.loads(statistic, object_pairs_hook=collections.OrderedDict)
                # notify new statistic
                self.modified.emit(self.statistic)
            except:
                traceback.print_exc()                
                
