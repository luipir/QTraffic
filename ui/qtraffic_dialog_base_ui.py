# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/qtraffic_dialog_base.ui'
#
# Created: Tue May  5 14:53:12 2015
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

class Ui_qtraffic_dockWidget(object):
    def setupUi(self, qtraffic_dockWidget):
        qtraffic_dockWidget.setObjectName(_fromUtf8("qtraffic_dockWidget"))
        qtraffic_dockWidget.resize(930, 462)
        qtraffic_dockWidget.setFloating(False)
        self.qtraffic_widget = QtGui.QWidget()
        self.qtraffic_widget.setObjectName(_fromUtf8("qtraffic_widget"))
        self.verticalLayout_16 = QtGui.QVBoxLayout(self.qtraffic_widget)
        self.verticalLayout_16.setObjectName(_fromUtf8("verticalLayout_16"))
        self.tabWidget = QtGui.QTabWidget(self.qtraffic_widget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.input_tab = QtGui.QWidget()
        self.input_tab.setObjectName(_fromUtf8("input_tab"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.input_tab)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.groupBox = QtGui.QGroupBox(self.input_tab)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lineEdit = QtGui.QLineEdit(self.groupBox)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.horizontalLayout.addWidget(self.lineEdit)
        self.toolButton = QtGui.QToolButton(self.groupBox)
        self.toolButton.setObjectName(_fromUtf8("toolButton"))
        self.horizontalLayout.addWidget(self.toolButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(self.input_tab)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.verticalLayout_6 = QtGui.QVBoxLayout()
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_6.addWidget(self.label)
        self.linkId_combo = QtGui.QComboBox(self.groupBox_2)
        self.linkId_combo.setEditable(True)
        self.linkId_combo.setObjectName(_fromUtf8("linkId_combo"))
        self.verticalLayout_6.addWidget(self.linkId_combo)
        self.gridLayout_3.addLayout(self.verticalLayout_6, 0, 0, 1, 1)
        self.verticalLayout_11 = QtGui.QVBoxLayout()
        self.verticalLayout_11.setObjectName(_fromUtf8("verticalLayout_11"))
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout_11.addWidget(self.label_6)
        self.roadGradient_combo = QtGui.QComboBox(self.groupBox_2)
        self.roadGradient_combo.setEditable(True)
        self.roadGradient_combo.setObjectName(_fromUtf8("roadGradient_combo"))
        self.verticalLayout_11.addWidget(self.roadGradient_combo)
        self.gridLayout_3.addLayout(self.verticalLayout_11, 2, 1, 1, 1)
        self.verticalLayout_10 = QtGui.QVBoxLayout()
        self.verticalLayout_10.setObjectName(_fromUtf8("verticalLayout_10"))
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_10.addWidget(self.label_5)
        self.roadLenght_combo = QtGui.QComboBox(self.groupBox_2)
        self.roadLenght_combo.setEditable(True)
        self.roadLenght_combo.setObjectName(_fromUtf8("roadLenght_combo"))
        self.verticalLayout_10.addWidget(self.roadLenght_combo)
        self.gridLayout_3.addLayout(self.verticalLayout_10, 2, 0, 1, 1)
        self.verticalLayout_7 = QtGui.QVBoxLayout()
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_7.addWidget(self.label_2)
        self.linkType_combo = QtGui.QComboBox(self.groupBox_2)
        self.linkType_combo.setEditable(True)
        self.linkType_combo.setObjectName(_fromUtf8("linkType_combo"))
        self.verticalLayout_7.addWidget(self.linkType_combo)
        self.gridLayout_3.addLayout(self.verticalLayout_7, 0, 1, 1, 1)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.next_pushButton = QtGui.QPushButton(self.input_tab)
        self.next_pushButton.setObjectName(_fromUtf8("next_pushButton"))
        self.horizontalLayout_2.addWidget(self.next_pushButton)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.tabWidget.addTab(self.input_tab, _fromUtf8(""))
        self.vehicle_tab = QtGui.QWidget()
        self.vehicle_tab.setObjectName(_fromUtf8("vehicle_tab"))
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.vehicle_tab)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_19 = QtGui.QVBoxLayout()
        self.verticalLayout_19.setObjectName(_fromUtf8("verticalLayout_19"))
        self.label_13 = QtGui.QLabel(self.vehicle_tab)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.verticalLayout_19.addWidget(self.label_13)
        self.comboBox_8 = QtGui.QComboBox(self.vehicle_tab)
        self.comboBox_8.setObjectName(_fromUtf8("comboBox_8"))
        self.verticalLayout_19.addWidget(self.comboBox_8)
        self.gridLayout.addLayout(self.verticalLayout_19, 4, 0, 1, 1)
        self.verticalLayout_13 = QtGui.QVBoxLayout()
        self.verticalLayout_13.setObjectName(_fromUtf8("verticalLayout_13"))
        self.label_7 = QtGui.QLabel(self.vehicle_tab)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout_13.addWidget(self.label_7)
        self.comboBox_2 = QtGui.QComboBox(self.vehicle_tab)
        self.comboBox_2.setObjectName(_fromUtf8("comboBox_2"))
        self.verticalLayout_13.addWidget(self.comboBox_2)
        self.gridLayout.addLayout(self.verticalLayout_13, 0, 0, 1, 1)
        self.verticalLayout_18 = QtGui.QVBoxLayout()
        self.verticalLayout_18.setObjectName(_fromUtf8("verticalLayout_18"))
        self.label_11 = QtGui.QLabel(self.vehicle_tab)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.verticalLayout_18.addWidget(self.label_11)
        self.comboBox_6 = QtGui.QComboBox(self.vehicle_tab)
        self.comboBox_6.setObjectName(_fromUtf8("comboBox_6"))
        self.verticalLayout_18.addWidget(self.comboBox_6)
        self.gridLayout.addLayout(self.verticalLayout_18, 3, 0, 1, 1)
        self.verticalLayout_15 = QtGui.QVBoxLayout()
        self.verticalLayout_15.setObjectName(_fromUtf8("verticalLayout_15"))
        self.label_9 = QtGui.QLabel(self.vehicle_tab)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.verticalLayout_15.addWidget(self.label_9)
        self.comboBox_4 = QtGui.QComboBox(self.vehicle_tab)
        self.comboBox_4.setObjectName(_fromUtf8("comboBox_4"))
        self.verticalLayout_15.addWidget(self.comboBox_4)
        self.gridLayout.addLayout(self.verticalLayout_15, 3, 1, 1, 1)
        self.verticalLayout_20 = QtGui.QVBoxLayout()
        self.verticalLayout_20.setObjectName(_fromUtf8("verticalLayout_20"))
        self.label_15 = QtGui.QLabel(self.vehicle_tab)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.verticalLayout_20.addWidget(self.label_15)
        self.comboBox_10 = QtGui.QComboBox(self.vehicle_tab)
        self.comboBox_10.setObjectName(_fromUtf8("comboBox_10"))
        self.verticalLayout_20.addWidget(self.comboBox_10)
        self.gridLayout.addLayout(self.verticalLayout_20, 4, 1, 1, 1)
        self.verticalLayout_23 = QtGui.QVBoxLayout()
        self.verticalLayout_23.setObjectName(_fromUtf8("verticalLayout_23"))
        self.label_17 = QtGui.QLabel(self.vehicle_tab)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.verticalLayout_23.addWidget(self.label_17)
        self.comboBox_12 = QtGui.QComboBox(self.vehicle_tab)
        self.comboBox_12.setObjectName(_fromUtf8("comboBox_12"))
        self.verticalLayout_23.addWidget(self.comboBox_12)
        self.gridLayout.addLayout(self.verticalLayout_23, 0, 1, 1, 1)
        self.verticalLayout_8.addLayout(self.gridLayout)
        self.verticalLayout_14 = QtGui.QVBoxLayout()
        self.verticalLayout_14.setObjectName(_fromUtf8("verticalLayout_14"))
        self.label_8 = QtGui.QLabel(self.vehicle_tab)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.verticalLayout_14.addWidget(self.label_8)
        self.comboBox_3 = QtGui.QComboBox(self.vehicle_tab)
        self.comboBox_3.setObjectName(_fromUtf8("comboBox_3"))
        self.verticalLayout_14.addWidget(self.comboBox_3)
        self.verticalLayout_8.addLayout(self.verticalLayout_14)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_8.addItem(spacerItem2)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem3)
        self.next_pushButton_2 = QtGui.QPushButton(self.vehicle_tab)
        self.next_pushButton_2.setObjectName(_fromUtf8("next_pushButton_2"))
        self.horizontalLayout_5.addWidget(self.next_pushButton_2)
        self.verticalLayout_8.addLayout(self.horizontalLayout_5)
        self.tabWidget.addTab(self.vehicle_tab, _fromUtf8(""))
        self.fleetComposition_tab = QtGui.QWidget()
        self.fleetComposition_tab.setObjectName(_fromUtf8("fleetComposition_tab"))
        self.verticalLayout = QtGui.QVBoxLayout(self.fleetComposition_tab)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_14 = QtGui.QHBoxLayout()
        self.horizontalLayout_14.setObjectName(_fromUtf8("horizontalLayout_14"))
        self.verticalLayout_12 = QtGui.QVBoxLayout()
        self.verticalLayout_12.setObjectName(_fromUtf8("verticalLayout_12"))
        self.newRoadType_button = QtGui.QPushButton(self.fleetComposition_tab)
        self.newRoadType_button.setObjectName(_fromUtf8("newRoadType_button"))
        self.verticalLayout_12.addWidget(self.newRoadType_button)
        self.removeRoadType_button = QtGui.QPushButton(self.fleetComposition_tab)
        self.removeRoadType_button.setObjectName(_fromUtf8("removeRoadType_button"))
        self.verticalLayout_12.addWidget(self.removeRoadType_button)
        spacerItem4 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_12.addItem(spacerItem4)
        self.loadConfiguration_button = QtGui.QPushButton(self.fleetComposition_tab)
        self.loadConfiguration_button.setObjectName(_fromUtf8("loadConfiguration_button"))
        self.verticalLayout_12.addWidget(self.loadConfiguration_button)
        self.saveConfiguration_button = QtGui.QPushButton(self.fleetComposition_tab)
        self.saveConfiguration_button.setObjectName(_fromUtf8("saveConfiguration_button"))
        self.verticalLayout_12.addWidget(self.saveConfiguration_button)
        self.horizontalLayout_14.addLayout(self.verticalLayout_12)
        self.roadTypes_listWidget = QtGui.QListWidget(self.fleetComposition_tab)
        self.roadTypes_listWidget.setResizeMode(QtGui.QListView.Adjust)
        self.roadTypes_listWidget.setObjectName(_fromUtf8("roadTypes_listWidget"))
        self.horizontalLayout_14.addWidget(self.roadTypes_listWidget)
        self.fleetComposition_tabs = QtGui.QTabWidget(self.fleetComposition_tab)
        self.fleetComposition_tabs.setObjectName(_fromUtf8("fleetComposition_tabs"))
        self.passengerCars_tab = QtGui.QWidget()
        self.passengerCars_tab.setObjectName(_fromUtf8("passengerCars_tab"))
        self.horizontalLayout_7 = QtGui.QHBoxLayout(self.passengerCars_tab)
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.passengerCars_webView = QtWebKit.QWebView(self.passengerCars_tab)
        self.passengerCars_webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.passengerCars_webView.setObjectName(_fromUtf8("passengerCars_webView"))
        self.horizontalLayout_7.addWidget(self.passengerCars_webView)
        self.fleetComposition_tabs.addTab(self.passengerCars_tab, _fromUtf8(""))
        self.lightDutyVehicles_tab = QtGui.QWidget()
        self.lightDutyVehicles_tab.setObjectName(_fromUtf8("lightDutyVehicles_tab"))
        self.horizontalLayout_8 = QtGui.QHBoxLayout(self.lightDutyVehicles_tab)
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.lightDutyVehicles_webView = QtWebKit.QWebView(self.lightDutyVehicles_tab)
        self.lightDutyVehicles_webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.lightDutyVehicles_webView.setObjectName(_fromUtf8("lightDutyVehicles_webView"))
        self.horizontalLayout_8.addWidget(self.lightDutyVehicles_webView)
        self.fleetComposition_tabs.addTab(self.lightDutyVehicles_tab, _fromUtf8(""))
        self.heavyDutyVehicles_tab = QtGui.QWidget()
        self.heavyDutyVehicles_tab.setObjectName(_fromUtf8("heavyDutyVehicles_tab"))
        self.horizontalLayout_9 = QtGui.QHBoxLayout(self.heavyDutyVehicles_tab)
        self.horizontalLayout_9.setObjectName(_fromUtf8("horizontalLayout_9"))
        self.heavyDutyVehicles_webView = QtWebKit.QWebView(self.heavyDutyVehicles_tab)
        self.heavyDutyVehicles_webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.heavyDutyVehicles_webView.setObjectName(_fromUtf8("heavyDutyVehicles_webView"))
        self.horizontalLayout_9.addWidget(self.heavyDutyVehicles_webView)
        self.fleetComposition_tabs.addTab(self.heavyDutyVehicles_tab, _fromUtf8(""))
        self.urbanBuses_tab = QtGui.QWidget()
        self.urbanBuses_tab.setObjectName(_fromUtf8("urbanBuses_tab"))
        self.horizontalLayout_10 = QtGui.QHBoxLayout(self.urbanBuses_tab)
        self.horizontalLayout_10.setObjectName(_fromUtf8("horizontalLayout_10"))
        self.buses_webView = QtWebKit.QWebView(self.urbanBuses_tab)
        self.buses_webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.buses_webView.setObjectName(_fromUtf8("buses_webView"))
        self.horizontalLayout_10.addWidget(self.buses_webView)
        self.fleetComposition_tabs.addTab(self.urbanBuses_tab, _fromUtf8(""))
        self.coaches_tab = QtGui.QWidget()
        self.coaches_tab.setObjectName(_fromUtf8("coaches_tab"))
        self.horizontalLayout_12 = QtGui.QHBoxLayout(self.coaches_tab)
        self.horizontalLayout_12.setObjectName(_fromUtf8("horizontalLayout_12"))
        self.coaches_webView = QtWebKit.QWebView(self.coaches_tab)
        self.coaches_webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.coaches_webView.setObjectName(_fromUtf8("coaches_webView"))
        self.horizontalLayout_12.addWidget(self.coaches_webView)
        self.fleetComposition_tabs.addTab(self.coaches_tab, _fromUtf8(""))
        self.motorcycles_tab = QtGui.QWidget()
        self.motorcycles_tab.setObjectName(_fromUtf8("motorcycles_tab"))
        self.horizontalLayout_11 = QtGui.QHBoxLayout(self.motorcycles_tab)
        self.horizontalLayout_11.setObjectName(_fromUtf8("horizontalLayout_11"))
        self.motors_webView = QtWebKit.QWebView(self.motorcycles_tab)
        self.motors_webView.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.motors_webView.setObjectName(_fromUtf8("motors_webView"))
        self.horizontalLayout_11.addWidget(self.motors_webView)
        self.fleetComposition_tabs.addTab(self.motorcycles_tab, _fromUtf8(""))
        self.horizontalLayout_14.addWidget(self.fleetComposition_tabs)
        self.horizontalLayout_14.setStretch(0, 1)
        self.horizontalLayout_14.setStretch(1, 2)
        self.verticalLayout.addLayout(self.horizontalLayout_14)
        spacerItem5 = QtGui.QSpacerItem(20, 105, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem5)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem6)
        self.next_pushButton_4 = QtGui.QPushButton(self.fleetComposition_tab)
        self.next_pushButton_4.setObjectName(_fromUtf8("next_pushButton_4"))
        self.horizontalLayout_6.addWidget(self.next_pushButton_4)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.tabWidget.addTab(self.fleetComposition_tab, _fromUtf8(""))
        self.parameters_tab = QtGui.QWidget()
        self.parameters_tab.setObjectName(_fromUtf8("parameters_tab"))
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.parameters_tab)
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.horizontalLayout_15 = QtGui.QHBoxLayout()
        self.horizontalLayout_15.setObjectName(_fromUtf8("horizontalLayout_15"))
        self.groupBox_6 = QtGui.QGroupBox(self.parameters_tab)
        self.groupBox_6.setStyleSheet(_fromUtf8("QGroupBox{\n"
"    border:1px solid gray;\n"
"    border-radius:5px;\n"
"    margin-top: 1ex;\n"
"}\n"
"QGroupBox::title{\n"
"    subcontrol-origin: margin;\n"
"    subcontrol-position:top center;\n"
"    padding:0 3px;\n"
"}"))
        self.groupBox_6.setObjectName(_fromUtf8("groupBox_6"))
        self.formLayout = QtGui.QFormLayout(self.groupBox_6)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_3 = QtGui.QLabel(self.groupBox_6)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_3)
        self.spinBox = QtGui.QSpinBox(self.groupBox_6)
        self.spinBox.setObjectName(_fromUtf8("spinBox"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.spinBox)
        self.label_4 = QtGui.QLabel(self.groupBox_6)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_4)
        self.label_10 = QtGui.QLabel(self.groupBox_6)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_10)
        self.doubleSpinBox = QtGui.QDoubleSpinBox(self.groupBox_6)
        self.doubleSpinBox.setObjectName(_fromUtf8("doubleSpinBox"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.doubleSpinBox)
        self.doubleSpinBox_2 = QtGui.QDoubleSpinBox(self.groupBox_6)
        self.doubleSpinBox_2.setObjectName(_fromUtf8("doubleSpinBox_2"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.doubleSpinBox_2)
        self.horizontalLayout_15.addWidget(self.groupBox_6)
        self.groupBox_7 = QtGui.QGroupBox(self.parameters_tab)
        self.groupBox_7.setStyleSheet(_fromUtf8("QGroupBox{\n"
"    border:1px solid gray;\n"
"    border-radius:5px;\n"
"    margin-top: 1ex;\n"
"}\n"
"QGroupBox::title{\n"
"    subcontrol-origin: margin;\n"
"    subcontrol-position:top center;\n"
"    padding:0 3px;\n"
"}"))
        self.groupBox_7.setObjectName(_fromUtf8("groupBox_7"))
        self.formLayout_2 = QtGui.QFormLayout(self.groupBox_7)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.label_12 = QtGui.QLabel(self.groupBox_7)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_12)
        self.spinBox_2 = QtGui.QSpinBox(self.groupBox_7)
        self.spinBox_2.setObjectName(_fromUtf8("spinBox_2"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.spinBox_2)
        self.label_16 = QtGui.QLabel(self.groupBox_7)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_16)
        self.doubleSpinBox_4 = QtGui.QDoubleSpinBox(self.groupBox_7)
        self.doubleSpinBox_4.setObjectName(_fromUtf8("doubleSpinBox_4"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.doubleSpinBox_4)
        self.label_14 = QtGui.QLabel(self.groupBox_7)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_14)
        self.doubleSpinBox_3 = QtGui.QDoubleSpinBox(self.groupBox_7)
        self.doubleSpinBox_3.setObjectName(_fromUtf8("doubleSpinBox_3"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.doubleSpinBox_3)
        self.horizontalLayout_15.addWidget(self.groupBox_7)
        self.groupBox_8 = QtGui.QGroupBox(self.parameters_tab)
        self.groupBox_8.setStyleSheet(_fromUtf8("QGroupBox{\n"
"    border:1px solid gray;\n"
"    border-radius:5px;\n"
"    margin-top: 1ex;\n"
"}\n"
"QGroupBox::title{\n"
"    subcontrol-origin: margin;\n"
"    subcontrol-position:top center;\n"
"    padding:0 3px;\n"
"}"))
        self.groupBox_8.setObjectName(_fromUtf8("groupBox_8"))
        self.formLayout_3 = QtGui.QFormLayout(self.groupBox_8)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.label_18 = QtGui.QLabel(self.groupBox_8)
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_18)
        self.spinBox_3 = QtGui.QSpinBox(self.groupBox_8)
        self.spinBox_3.setObjectName(_fromUtf8("spinBox_3"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.FieldRole, self.spinBox_3)
        self.label_20 = QtGui.QLabel(self.groupBox_8)
        self.label_20.setObjectName(_fromUtf8("label_20"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_20)
        self.doubleSpinBox_6 = QtGui.QDoubleSpinBox(self.groupBox_8)
        self.doubleSpinBox_6.setObjectName(_fromUtf8("doubleSpinBox_6"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.FieldRole, self.doubleSpinBox_6)
        self.label_19 = QtGui.QLabel(self.groupBox_8)
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_19)
        self.doubleSpinBox_5 = QtGui.QDoubleSpinBox(self.groupBox_8)
        self.doubleSpinBox_5.setObjectName(_fromUtf8("doubleSpinBox_5"))
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.FieldRole, self.doubleSpinBox_5)
        self.horizontalLayout_15.addWidget(self.groupBox_8)
        self.verticalLayout_9.addLayout(self.horizontalLayout_15)
        self.groupBox_5 = QtGui.QGroupBox(self.parameters_tab)
        self.groupBox_5.setStyleSheet(_fromUtf8("QGroupBox{\n"
"    border:1px solid gray;\n"
"    border-radius:5px;\n"
"    margin-top: 1ex;\n"
"}\n"
"QGroupBox::title{\n"
"    subcontrol-origin: margin;\n"
"    subcontrol-position:top center;\n"
"    padding:0 3px;\n"
"}"))
        self.groupBox_5.setCheckable(False)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.horizontalLayout_19 = QtGui.QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_19.setContentsMargins(-1, 20, -1, 20)
        self.horizontalLayout_19.setObjectName(_fromUtf8("horizontalLayout_19"))
        self.horizontalLayout_16 = QtGui.QHBoxLayout()
        self.horizontalLayout_16.setObjectName(_fromUtf8("horizontalLayout_16"))
        self.label_21 = QtGui.QLabel(self.groupBox_5)
        self.label_21.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.horizontalLayout_16.addWidget(self.label_21)
        self.doubleSpinBox_7 = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_7.setObjectName(_fromUtf8("doubleSpinBox_7"))
        self.horizontalLayout_16.addWidget(self.doubleSpinBox_7)
        self.horizontalLayout_19.addLayout(self.horizontalLayout_16)
        self.horizontalLayout_17 = QtGui.QHBoxLayout()
        self.horizontalLayout_17.setObjectName(_fromUtf8("horizontalLayout_17"))
        self.label_22 = QtGui.QLabel(self.groupBox_5)
        self.label_22.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.horizontalLayout_17.addWidget(self.label_22)
        self.doubleSpinBox_8 = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_8.setObjectName(_fromUtf8("doubleSpinBox_8"))
        self.horizontalLayout_17.addWidget(self.doubleSpinBox_8)
        self.horizontalLayout_19.addLayout(self.horizontalLayout_17)
        self.horizontalLayout_18 = QtGui.QHBoxLayout()
        self.horizontalLayout_18.setObjectName(_fromUtf8("horizontalLayout_18"))
        self.label_23 = QtGui.QLabel(self.groupBox_5)
        self.label_23.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_23.setObjectName(_fromUtf8("label_23"))
        self.horizontalLayout_18.addWidget(self.label_23)
        self.doubleSpinBox_9 = QtGui.QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_9.setObjectName(_fromUtf8("doubleSpinBox_9"))
        self.horizontalLayout_18.addWidget(self.doubleSpinBox_9)
        self.horizontalLayout_19.addLayout(self.horizontalLayout_18)
        self.verticalLayout_9.addWidget(self.groupBox_5)
        spacerItem7 = QtGui.QSpacerItem(20, 124, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_9.addItem(spacerItem7)
        self.horizontalLayout_13 = QtGui.QHBoxLayout()
        self.horizontalLayout_13.setObjectName(_fromUtf8("horizontalLayout_13"))
        spacerItem8 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem8)
        self.next_pushButton_3 = QtGui.QPushButton(self.parameters_tab)
        self.next_pushButton_3.setObjectName(_fromUtf8("next_pushButton_3"))
        self.horizontalLayout_13.addWidget(self.next_pushButton_3)
        self.verticalLayout_9.addLayout(self.horizontalLayout_13)
        self.tabWidget.addTab(self.parameters_tab, _fromUtf8(""))
        self.output_tab = QtGui.QWidget()
        self.output_tab.setObjectName(_fromUtf8("output_tab"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.output_tab)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.groupBox_3 = QtGui.QGroupBox(self.output_tab)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.lineEdit_2 = QtGui.QLineEdit(self.groupBox_3)
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.horizontalLayout_4.addWidget(self.lineEdit_2)
        self.toolButton_2 = QtGui.QToolButton(self.groupBox_3)
        self.toolButton_2.setObjectName(_fromUtf8("toolButton_2"))
        self.horizontalLayout_4.addWidget(self.toolButton_2)
        self.verticalLayout_5.addLayout(self.horizontalLayout_4)
        self.verticalLayout_4.addWidget(self.groupBox_3)
        self.groupBox_4 = QtGui.QGroupBox(self.output_tab)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.checkBox = QtGui.QCheckBox(self.groupBox_4)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.gridLayout_2.addWidget(self.checkBox, 0, 0, 1, 1)
        self.checkBox_2 = QtGui.QCheckBox(self.groupBox_4)
        self.checkBox_2.setObjectName(_fromUtf8("checkBox_2"))
        self.gridLayout_2.addWidget(self.checkBox_2, 0, 1, 1, 1)
        self.checkBox_3 = QtGui.QCheckBox(self.groupBox_4)
        self.checkBox_3.setObjectName(_fromUtf8("checkBox_3"))
        self.gridLayout_2.addWidget(self.checkBox_3, 0, 2, 1, 1)
        self.checkBox_4 = QtGui.QCheckBox(self.groupBox_4)
        self.checkBox_4.setObjectName(_fromUtf8("checkBox_4"))
        self.gridLayout_2.addWidget(self.checkBox_4, 0, 3, 1, 1)
        self.checkBox_5 = QtGui.QCheckBox(self.groupBox_4)
        self.checkBox_5.setObjectName(_fromUtf8("checkBox_5"))
        self.gridLayout_2.addWidget(self.checkBox_5, 1, 0, 1, 1)
        self.checkBox_6 = QtGui.QCheckBox(self.groupBox_4)
        self.checkBox_6.setObjectName(_fromUtf8("checkBox_6"))
        self.gridLayout_2.addWidget(self.checkBox_6, 1, 1, 1, 1)
        self.checkBox_7 = QtGui.QCheckBox(self.groupBox_4)
        self.checkBox_7.setObjectName(_fromUtf8("checkBox_7"))
        self.gridLayout_2.addWidget(self.checkBox_7, 1, 2, 1, 1)
        self.verticalLayout_4.addWidget(self.groupBox_4)
        spacerItem9 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem9)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem10 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem10)
        self.calculate_pushButton = QtGui.QPushButton(self.output_tab)
        self.calculate_pushButton.setObjectName(_fromUtf8("calculate_pushButton"))
        self.horizontalLayout_3.addWidget(self.calculate_pushButton)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.tabWidget.addTab(self.output_tab, _fromUtf8(""))
        self.verticalLayout_16.addWidget(self.tabWidget)
        qtraffic_dockWidget.setWidget(self.qtraffic_widget)

        self.retranslateUi(qtraffic_dockWidget)
        self.tabWidget.setCurrentIndex(2)
        self.fleetComposition_tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(qtraffic_dockWidget)

    def retranslateUi(self, qtraffic_dockWidget):
        qtraffic_dockWidget.setWindowTitle(_translate("qtraffic_dockWidget", "QTraffic", None))
        self.groupBox.setTitle(_translate("qtraffic_dockWidget", "Input Layer", None))
        self.toolButton.setText(_translate("qtraffic_dockWidget", "...", None))
        self.groupBox_2.setTitle(_translate("qtraffic_dockWidget", "Table Column Select", None))
        self.label.setText(_translate("qtraffic_dockWidget", "Link ID", None))
        self.label_6.setText(_translate("qtraffic_dockWidget", "Road Gradient", None))
        self.label_5.setText(_translate("qtraffic_dockWidget", "Road Lenght", None))
        self.label_2.setText(_translate("qtraffic_dockWidget", "Link Type", None))
        self.next_pushButton.setText(_translate("qtraffic_dockWidget", "Next ->", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.input_tab), _translate("qtraffic_dockWidget", "Input Network", None))
        self.label_13.setText(_translate("qtraffic_dockWidget", "Urban buses count", None))
        self.label_7.setText(_translate("qtraffic_dockWidget", "Passenger cars count", None))
        self.label_11.setText(_translate("qtraffic_dockWidget", "Heavy duty vehicles count", None))
        self.label_9.setText(_translate("qtraffic_dockWidget", "Light duty vehicles count", None))
        self.label_15.setText(_translate("qtraffic_dockWidget", "Coaches count", None))
        self.label_17.setText(_translate("qtraffic_dockWidget", "Motorcycles count", None))
        self.label_8.setText(_translate("qtraffic_dockWidget", "Average vehicle speed (km/h)", None))
        self.next_pushButton_2.setText(_translate("qtraffic_dockWidget", "Next ->", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.vehicle_tab), _translate("qtraffic_dockWidget", "Vechicle Count/Speed", None))
        self.newRoadType_button.setText(_translate("qtraffic_dockWidget", "Add", None))
        self.removeRoadType_button.setText(_translate("qtraffic_dockWidget", "Remove", None))
        self.loadConfiguration_button.setText(_translate("qtraffic_dockWidget", "Load", None))
        self.saveConfiguration_button.setText(_translate("qtraffic_dockWidget", "Save", None))
        self.roadTypes_listWidget.setSortingEnabled(True)
        self.fleetComposition_tabs.setTabText(self.fleetComposition_tabs.indexOf(self.passengerCars_tab), _translate("qtraffic_dockWidget", "Passenger cars", None))
        self.fleetComposition_tabs.setTabText(self.fleetComposition_tabs.indexOf(self.lightDutyVehicles_tab), _translate("qtraffic_dockWidget", "Light duty vehicles", None))
        self.fleetComposition_tabs.setTabText(self.fleetComposition_tabs.indexOf(self.heavyDutyVehicles_tab), _translate("qtraffic_dockWidget", "Heavy duty vehicles", None))
        self.fleetComposition_tabs.setTabText(self.fleetComposition_tabs.indexOf(self.urbanBuses_tab), _translate("qtraffic_dockWidget", "Urban buses", None))
        self.fleetComposition_tabs.setTabText(self.fleetComposition_tabs.indexOf(self.coaches_tab), _translate("qtraffic_dockWidget", "Coaches", None))
        self.fleetComposition_tabs.setTabText(self.fleetComposition_tabs.indexOf(self.motorcycles_tab), _translate("qtraffic_dockWidget", "Motorcycles", None))
        self.next_pushButton_4.setText(_translate("qtraffic_dockWidget", "Next ->", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.fleetComposition_tab), _translate("qtraffic_dockWidget", "Fleet Composition", None))
        self.groupBox_6.setTitle(_translate("qtraffic_dockWidget", "Gasoline properties", None))
        self.label_3.setText(_translate("qtraffic_dockWidget", "Sulphure contents (ppm)", None))
        self.label_4.setText(_translate("qtraffic_dockWidget", "Pb contents (g/l)", None))
        self.label_10.setText(_translate("qtraffic_dockWidget", "Volatility", None))
        self.groupBox_7.setTitle(_translate("qtraffic_dockWidget", "Diesel properties", None))
        self.label_12.setText(_translate("qtraffic_dockWidget", "Sulphure contents (ppm)", None))
        self.label_16.setText(_translate("qtraffic_dockWidget", "Pb contents (g/l)", None))
        self.label_14.setText(_translate("qtraffic_dockWidget", "Volatility", None))
        self.groupBox_8.setTitle(_translate("qtraffic_dockWidget", "Alternative fuels properties", None))
        self.label_18.setText(_translate("qtraffic_dockWidget", "Sulphure contents (ppm)", None))
        self.label_20.setText(_translate("qtraffic_dockWidget", "Pb contents (g/l)", None))
        self.label_19.setText(_translate("qtraffic_dockWidget", "Volatility", None))
        self.groupBox_5.setTitle(_translate("qtraffic_dockWidget", "Temperature", None))
        self.label_21.setText(_translate("qtraffic_dockWidget", "Minimum", None))
        self.label_22.setText(_translate("qtraffic_dockWidget", "Average", None))
        self.label_23.setText(_translate("qtraffic_dockWidget", "Maximum", None))
        self.next_pushButton_3.setText(_translate("qtraffic_dockWidget", "Next ->", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.parameters_tab), _translate("qtraffic_dockWidget", "Parameters", None))
        self.groupBox_3.setTitle(_translate("qtraffic_dockWidget", "Output File", None))
        self.toolButton_2.setText(_translate("qtraffic_dockWidget", "...", None))
        self.groupBox_4.setTitle(_translate("qtraffic_dockWidget", "Parameters to calc", None))
        self.checkBox.setText(_translate("qtraffic_dockWidget", "CO", None))
        self.checkBox_2.setText(_translate("qtraffic_dockWidget", "CO2", None))
        self.checkBox_3.setText(_translate("qtraffic_dockWidget", "NOx", None))
        self.checkBox_4.setText(_translate("qtraffic_dockWidget", "Fuel Consumption", None))
        self.checkBox_5.setText(_translate("qtraffic_dockWidget", "PM", None))
        self.checkBox_6.setText(_translate("qtraffic_dockWidget", "SO2", None))
        self.checkBox_7.setText(_translate("qtraffic_dockWidget", "VOC", None))
        self.calculate_pushButton.setText(_translate("qtraffic_dockWidget", "Calculate", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.output_tab), _translate("qtraffic_dockWidget", "Output", None))

from PyQt4 import QtWebKit
