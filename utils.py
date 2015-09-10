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
# 2To3 python compatibility
from __future__ import print_function
from __future__ import unicode_literals

import traceback
import platform

if platform.system() == 'Windows':
    import win32api, win32con

def setFileWindowsHidden(fileName):
    ''' Set Hidden attribute in case of windows platform.
        Otherwise leave it unchanged
    '''
    if platform.system() == 'Windows':
        win32api.SetFileAttributes(fileName,win32con.FILE_ATTRIBUTE_HIDDEN)
