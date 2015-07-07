# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/newfuel_formula_editor_dialog.ui'
#
# Created: Tue Jul  7 17:59:10 2015
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

class Ui_newFuelFormula_dialog(object):
    def setupUi(self, newFuelFormula_dialog):
        newFuelFormula_dialog.setObjectName(_fromUtf8("newFuelFormula_dialog"))
        newFuelFormula_dialog.resize(780, 464)
        self.verticalLayout = QtGui.QVBoxLayout(newFuelFormula_dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_30 = QtGui.QHBoxLayout()
        self.horizontalLayout_30.setObjectName(_fromUtf8("horizontalLayout_30"))
        self.label_28 = QtGui.QLabel(newFuelFormula_dialog)
        self.label_28.setObjectName(_fromUtf8("label_28"))
        self.horizontalLayout_30.addWidget(self.label_28)
        self.formulaFile_LEdit = QtGui.QLineEdit(newFuelFormula_dialog)
        self.formulaFile_LEdit.setObjectName(_fromUtf8("formulaFile_LEdit"))
        self.horizontalLayout_30.addWidget(self.formulaFile_LEdit)
        self.selectFunctionFile_TButton = QtGui.QToolButton(newFuelFormula_dialog)
        self.selectFunctionFile_TButton.setObjectName(_fromUtf8("selectFunctionFile_TButton"))
        self.horizontalLayout_30.addWidget(self.selectFunctionFile_TButton)
        self.verticalLayout.addLayout(self.horizontalLayout_30)
        self.horizontalLayout_31 = QtGui.QHBoxLayout()
        self.horizontalLayout_31.setObjectName(_fromUtf8("horizontalLayout_31"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_31.addItem(spacerItem)
        self.newFormulaFile_PButton = QtGui.QPushButton(newFuelFormula_dialog)
        self.newFormulaFile_PButton.setObjectName(_fromUtf8("newFormulaFile_PButton"))
        self.horizontalLayout_31.addWidget(self.newFormulaFile_PButton)
        self.saveAsFormulaFile_PButton = QtGui.QPushButton(newFuelFormula_dialog)
        self.saveAsFormulaFile_PButton.setObjectName(_fromUtf8("saveAsFormulaFile_PButton"))
        self.horizontalLayout_31.addWidget(self.saveAsFormulaFile_PButton)
        self.saveFormulaFile_PButton = QtGui.QPushButton(newFuelFormula_dialog)
        self.saveFormulaFile_PButton.setObjectName(_fromUtf8("saveFormulaFile_PButton"))
        self.horizontalLayout_31.addWidget(self.saveFormulaFile_PButton)
        self.verticalLayout.addLayout(self.horizontalLayout_31)
        self.layoutContainer = QtGui.QVBoxLayout()
        self.layoutContainer.setObjectName(_fromUtf8("layoutContainer"))
        self.verticalLayout.addLayout(self.layoutContainer)
        self.buttonBox = QtGui.QDialogButtonBox(newFuelFormula_dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(newFuelFormula_dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), newFuelFormula_dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), newFuelFormula_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(newFuelFormula_dialog)

    def retranslateUi(self, newFuelFormula_dialog):
        newFuelFormula_dialog.setWindowTitle(_translate("newFuelFormula_dialog", "Dialog", None))
        self.label_28.setText(_translate("newFuelFormula_dialog", "FIle", None))
        self.selectFunctionFile_TButton.setText(_translate("newFuelFormula_dialog", "...", None))
        self.newFormulaFile_PButton.setText(_translate("newFuelFormula_dialog", "New", None))
        self.saveAsFormulaFile_PButton.setText(_translate("newFuelFormula_dialog", "Save As", None))
        self.saveFormulaFile_PButton.setText(_translate("newFuelFormula_dialog", "Save", None))

