# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/qtraffic_select_layer.ui'
#
# Created: Tue Sep  8 18:01:38 2015
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_selectLayer_dlg(object):
    def setupUi(self, selectLayer_dlg):
        selectLayer_dlg.setObjectName(_fromUtf8("selectLayer_dlg"))
        selectLayer_dlg.resize(400, 101)
        self.verticalLayout = QtGui.QVBoxLayout(selectLayer_dlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(selectLayer_dlg)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.selectLayer_CBox = QgsMapLayerComboBox(selectLayer_dlg)
        self.selectLayer_CBox.setObjectName(_fromUtf8("selectLayer_CBox"))
        self.verticalLayout.addWidget(self.selectLayer_CBox)
        self.buttonBox = QtGui.QDialogButtonBox(selectLayer_dlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(selectLayer_dlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), selectLayer_dlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), selectLayer_dlg.reject)
        QtCore.QMetaObject.connectSlotsByName(selectLayer_dlg)

    def retranslateUi(self, selectLayer_dlg):
        selectLayer_dlg.setWindowTitle(_translate("selectLayer_dlg", "Dialog", None))
        self.label.setText(_translate("selectLayer_dlg", "Select Roads vectotr layer", None))

from qgis.gui import QgsMapLayerComboBox
