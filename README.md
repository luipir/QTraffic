QTraffic
========
Traffic Emission and Energy Consumption Model for open-source QGIS

QTraffic model is able to quantify traffic emission and energy consumption on the urban level.
It has been developed based on the updated European methodology for emission factors and
a novel technology for producing dynamic interactive data visualization. 
The emission and energy consumption model is implemented as a plugin for open-source QGIS and
integrates D3.js library with the Python programming.

Developped by Luigi Pirelli inside EMSURE project with technical support by Oxana Tchepel, Daniela Dias

EMSURE Project in Coimbra Univerity: http://www.uc.pt/en/efs/research/emsure/

LIMITATIONS: Due to algorithm structure, the plugin manages only shapefiles 

[![QTraffic Screenshot](https://github.com/luipir/QTraffic/blob/master/help/screenshots/QTrafficScreenshot.png)](https://github.com/luipir/QTraffic)

Quick Installation Guide
========================
NOTE for Linux users:
TEM Algoritm was developed and compied in Fortran under Win environment. To allow execution in a Linux environment
it's necessary to have [wine](https://www.winehq.org/) installed.

Qtraffic can be installed as qgis experimental plugin adding the following [repository](https://dl.dropboxusercontent.com/u/12837459/qgis_plugins/emsure.xml)

License
=======

For TEM algorithm license please contact EMSURE team.

QTraffic plugin is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License version 3 (GPLv3) as
published by the Free Software Foundation.

The full GNU General Public License is available in LICENSE.txt or
http://www.gnu.org/licenses/gpl.html

Disclaimer of Warranty (GPLv3)
==============================

There is no warranty for the program, to the extent permitted by
applicable law. Except when otherwise stated in writing the copyright
holders and/or other parties provide the program "as is" without warranty
of any kind, either expressed or implied, including, but not limited to,
the implied warranties of merchantability and fitness for a particular
purpose. The entire risk as to the quality and performance of the program
is with you. Should the program prove defective, you assume the cost of
all necessary servicing, repair or correction.


Limitation of Liability (GPLv3)
===============================

In no event unless required by applicable law or agreed to in writing
will any copyright holder, or any other party who modifies and/or conveys
the program as permitted above, be liable to you for damages, including any
general, special, incidental or consequential damages arising out of the
use or inability to use the program (including but not limited to loss of
data or data being rendered inaccurate or losses sustained by you or third
parties or a failure of the program to operate with any other programs),
even if such holder or other party has been advised of the possibility of
such damages.
