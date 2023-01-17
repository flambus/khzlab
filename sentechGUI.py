#!/usr/bin/env python3
# ----------------------------------------------------------------------------
#
# Copyright 2018 EMVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ----------------------------------------------------------------------------


# Standard library imports
import datetime
import os
import sys
import time
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Related third party imports
from PyQt5.QtCore import QMutexLocker, QMutex, pyqtSignal, QThread
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QMainWindow, QAction, QComboBox, \
    QDesktopWidget, QFileDialog, QDialog, QShortcut, QApplication, QLineEdit, QSpinBox

from genicam.gentl import NotInitializedException, InvalidHandleException, \
    InvalidIdException, ResourceInUseException, \
    InvalidParameterException, NotImplementedException, \
    AccessDeniedException

# Local application/library specific imports
from harvesters.core import Harvester as HarvesterCore
from harvesters_gui._private.frontend.canvas import Canvas2D
from harvesters_gui._private.frontend.helper import compose_tooltip
from harvesters_gui._private.frontend.pyqt5.about import About
from harvesters_gui._private.frontend.pyqt5.action import Action
from harvesters_gui._private.frontend.pyqt5.attribute_controller import AttributeController
from harvesters_gui._private.frontend.pyqt5.device_list import ComboBoxDeviceList
#from harvesters_gui._private.frontend.pyqt5.gain_list import GainList
from harvesters_gui._private.frontend.pyqt5.display_rate_list import ComboBoxDisplayRateList
from harvesters_gui._private.frontend.pyqt5.helper import get_system_font
from harvesters_gui._private.frontend.pyqt5.icon import Icon
from harvesters_gui._private.frontend.pyqt5.thread import _PyQtThread
from harvesters.util.logging import get_logger

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.widgets import RectangleSelector


class Harvester(QMainWindow):
    #
    _signal_update_statistics = pyqtSignal(str)
    _signal_stop_image_acquisition = pyqtSignal()

    def __init__(self, *, vsync=True, logger=None):
        #
        self._logger = logger or get_logger(name='harvesters')

        #
        super().__init__()

        #
        self._mutex = QMutex()

        profile = True if 'HARVESTER_PROFILE' in os.environ else False
        self._harvester_core = HarvesterCore(
            profile=profile, logger=self._logger
        )
        self._ia = None  # Image Acquirer

        #
        self._widget_canvas = Canvas2D(vsync=vsync)
        self._widget_canvas.create_native()
        self._widget_canvas.native.setParent(self)

        #
        self._action_stop_image_acquisition = None

        #
        self._observer_widgets = []

        #
        self._widget_device_list = None
        self._widget_device_list2 = None
        self._widget_device_list3 = None
        self._widget_status_bar = None
        self._widget_main = None
        self._widget_about = None
        self._widget_attribute_controller = None

        self._textfield = None

        self._origin = [0, 0]

        self._cropped = 0

        #
        self._signal_update_statistics.connect(self.update_statistics)
        self._signal_stop_image_acquisition.connect(self._stop_image_acquisition)
        self._thread_statistics_measurement = _PyQtThread(
            parent=self, mutex=self._mutex,
            worker=self._worker_update_statistics,
            update_cycle_us=250000
        )

        #
        self._initialize_widgets(1200, 600)

        #
        for o in self._observer_widgets:
            o.update()

    def _stop_image_acquisition(self):
        self.action_stop_image_acquisition.execute()

    def update_statistics(self, message):
        self.statusBar().showMessage(message)

    def closeEvent(self, QCloseEvent):
        #
        if self._widget_attribute_controller:
            self._widget_attribute_controller.close()

        #
        if self._harvester_core:
            self._harvester_core.reset()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._harvester_core.reset()

    @property
    def canvas(self):
        return self._widget_canvas

    @property
    def attribute_controller(self):
        return self._widget_attribute_controller

    @property
    def about(self):
        return self._widget_about

    @property
    def version(self):
        return self.harvester_core.version

    @property
    def device_list(self):
        return self._widget_device_list

    @property
    def cti_files(self):
        return self.harvester_core.files

    @property
    def harvester_core(self):
        return self._harvester_core

    @property
    def gain_list(self):
        return self._textfield

    def _resize_window(self, width, heigth):
        self.resize(width, heigth)

    def _initialize_widgets(self, width, heigth):
        #
        self.setWindowIcon(Icon('genicam_logo_i.png'))

        #
        self.setWindowTitle('GenICam.Harvester')
        self.setFont(get_system_font())

        #
        self.statusBar().showMessage('')
        self.statusBar().setFont(get_system_font())

        #
        self._initialize_gui_toolbar(self._observer_widgets)

        #
        self.setCentralWidget(self.canvas.native)

        #
        self.resize(width, heigth)

        # Place it in the center.
        rectangle = self.frameGeometry()
        coordinate = QDesktopWidget().availableGeometry().center()
        rectangle.moveCenter(coordinate)
        self.move(rectangle.topLeft())

    def _initialize_gui_toolbar(self, observers):
        #
        group_gentl_info = self.addToolBar('GenTL Information')
        group_connection = self.addToolBar('Connection')
        group_device = self.addToolBar('Image Acquisition')
        group_display = self.addToolBar('Display')
        group_help = self.addToolBar('Help')

        # Create buttons:

        # SELECT FILE
        button_select_file = ActionSelectFile(
            icon='open_file.png', title='Select file', parent=self,
            action=self.action_on_select_file,
            is_enabled=self.is_enabled_on_select_file
        )
        shortcut_key = 'Ctrl+o'
        button_select_file.setToolTip(
            compose_tooltip('Open a CTI file to load', shortcut_key)
        )
        button_select_file.setShortcut(shortcut_key)
        button_select_file.toggle()
        observers.append(button_select_file)

        # # TESTTESTTEST
        # button_test = ActionTest(
        #     icon='open_file.png', title='Select file', parent=self,
        #     action=self.action_on_test,
        #     is_enabled=self.is_enabled_on_test
        # )
        # shortcut_key = 'Ctrl+o'
        # button_test.setToolTip(
        #     compose_tooltip('Open a CTI file to load', shortcut_key)
        # )
        # button_test.setShortcut(shortcut_key)
        # button_test.toggle()
        # observers.append(button_test)

        # UPDATE LIST
        button_update = ActionUpdateList(
            icon='update.png', title='Update device list', parent=self,
            action=self.action_on_update_list,
            is_enabled=self.is_enabled_on_update_list
        )
        shortcut_key = 'Ctrl+u'
        button_update.setToolTip(
            compose_tooltip('Update the device list', shortcut_key)
        )
        button_update.setShortcut(shortcut_key)
        button_update.toggle()
        observers.append(button_update)

        # CONNECT
        button_connect = ActionConnect(
            icon='connect.png', title='Connect', parent=self,
            action=self.action_on_connect,
            is_enabled=self.is_enabled_on_connect
        )
        shortcut_key = 'Ctrl+c'
        button_connect.setToolTip(
            compose_tooltip(
                'Connect the selected device to Harvester',
                shortcut_key
            )
        )
        button_connect.setShortcut(shortcut_key)
        button_connect.toggle()
        observers.append(button_connect)

        # DISCONNECT
        button_disconnect = ActionDisconnect(
            icon='disconnect.png', title='Disconnect', parent=self,
            action=self.action_on_disconnect,
            is_enabled=self.is_enabled_on_disconnect
        )
        shortcut_key = 'Ctrl+d'
        button_disconnect.setToolTip(
            compose_tooltip(
                'Disconnect the device from Harvester',
                shortcut_key
            )
        )
        button_disconnect.setShortcut(shortcut_key)
        button_disconnect.toggle()
        observers.append(button_disconnect)

        # START ACQUISITION
        button_start_image_acquisition = ActionStartImageAcquisition(
            icon='start_acquisition.png', title='Start Acquisition', parent=self,
            action=self.action_on_start_image_acquisition,
            is_enabled=self.is_enabled_on_start_image_acquisition
        )
        shortcut_key = 'Ctrl+j'
        button_start_image_acquisition.setToolTip(
            compose_tooltip('Start image acquisition', shortcut_key)
        )
        button_start_image_acquisition.setShortcut(shortcut_key)
        button_start_image_acquisition.toggle()
        observers.append(button_start_image_acquisition)

        # PAUSE/RESUME DRAWING
        button_toggle_drawing = ActionToggleDrawing(
            icon='pause.png', title='Pause/Resume Drawing', parent=self,
            action=self.action_on_toggle_drawing,
            is_enabled=self.is_enabled_on_toggle_drawing
        )
        shortcut_key = 'Ctrl+k'
        button_toggle_drawing.setToolTip(
            compose_tooltip('Pause/Resume drawing', shortcut_key)
        )
        button_toggle_drawing.setShortcut(shortcut_key)
        button_toggle_drawing.toggle()
        observers.append(button_toggle_drawing)

        # STOP ACQUISITION
        button_stop_image_acquisition = ActionStopImageAcquisition(
            icon='stop_acquisition.png', title='Stop Acquisition', parent=self,
            action=self.action_on_stop_image_acquisition,
            is_enabled=self.is_enabled_on_stop_image_acquisition
        )
        shortcut_key = 'Ctrl+l'
        button_stop_image_acquisition.setToolTip(
            compose_tooltip('Stop image acquisition', shortcut_key)
        )
        button_stop_image_acquisition.setShortcut(shortcut_key)
        button_stop_image_acquisition.toggle()
        observers.append(button_stop_image_acquisition)
        self._action_stop_image_acquisition = button_stop_image_acquisition

        # DEVICE ATTRIBUTES
        button_dev_attribute = ActionShowAttributeController(
            icon='device_attribute.png', title='Device Attribute', parent=self,
            action=self.action_on_show_attribute_controller,
            is_enabled=self.is_enabled_on_show_attribute_controller
        )
        shortcut_key = 'Ctrl+a'
        button_dev_attribute.setToolTip(
            compose_tooltip('Edit device attribute', shortcut_key)
        )
        button_dev_attribute.setShortcut(shortcut_key)
        button_dev_attribute.toggle()
        observers.append(button_dev_attribute)

        # Create widgets to add:

        # EXPOSITION
        ###self._widget_device_list2 = QLineEdit(self)
        self._widget_device_list3 = QSpinBox(self)
        #self._widget_device_list3 = QComboBox(self)
        # self._widget_device_list3.setSizeAdjustPolicy(
        #     QComboBox.AdjustToContents
        # )
        shortcut_key = 'Ctrl+Shift+e'
        shortcut = QShortcut(QKeySequence(shortcut_key), self)

        def show_popup():
            self._widget_device_list3.showPopup()

        shortcut.activated.connect(show_popup)
        self._widget_device_list3.setToolTip(
            compose_tooltip('Change exposition', shortcut_key)
        )
        observers.append(self._widget_device_list3)
        # self.exposureTimeList = map(str, list(range(5000,60001,5000)))
        # for d in self.exposureTimeList:
        #     self._widget_device_list3.addItem(d)
        #self._widget_device_list3.setMinimum(0)
        self._widget_device_list3.setSingleStep(1000)
        self._widget_device_list3.setRange(0, 2147483647)
        self._widget_device_list3.editingFinished.connect(lambda: self._set_exposition(self._widget_device_list3.value()))
        #self._widget_device_list3.valueChanged.connect(self._set_exposition)
        #self._widget_device_list3.textChanged.connect(self._set_exposition)
        #self._widget_device_list3.currentTextChanged.connect(self._set_exposition)
        group_display.addWidget(self._widget_device_list3)
        observers.append(self._widget_device_list3)

        # GAIN
        self._widget_device_list2 = QComboBox(self)
        self._widget_device_list2.setSizeAdjustPolicy(
            QComboBox.AdjustToContents
        )
        shortcut_key = 'Ctrl+Shift+g'
        shortcut = QShortcut(QKeySequence(shortcut_key), self)

        def show_popup():
            self._widget_device_list2.showPopup()

        shortcut.activated.connect(show_popup)
        self._widget_device_list2.setToolTip(
            compose_tooltip('Change gain', shortcut_key)
        )
        observers.append(self._widget_device_list2)
        self.testList = ["1", "4", "16", "64", "255"]
        #for d in self.harvester_core.device_info_list:
        print(self.harvester_core.device_info_list)
        print(type(self.harvester_core.device_info_list))
        for d in self.testList:
            self._widget_device_list2.addItem(d)
        group_display.addWidget(self._widget_device_list2)
        self._widget_device_list2.currentTextChanged.connect(self._set_gain)
        observers.append(self._widget_device_list2)

        # BINNING (1x1, 2x2, 4x4)
        # ROI (Region of Interest)
        # Show framerate

        # SELECT DEVICE
        self._widget_device_list = ComboBoxDeviceList(self)
        self._widget_device_list.setSizeAdjustPolicy(
            QComboBox.AdjustToContents
        )
        shortcut_key = 'Ctrl+Shift+d'
        shortcut = QShortcut(QKeySequence(shortcut_key), self)

        def show_popup():
            self._widget_device_list.showPopup()

        shortcut.activated.connect(show_popup)
        self._widget_device_list.setToolTip(
            compose_tooltip('Select a device to connect', shortcut_key)
        )
        observers.append(self._widget_device_list)
        for d in self.harvester_core.device_info_list:
            self._widget_device_list.addItem(d)
        group_connection.addWidget(self._widget_device_list)
        observers.append(self._widget_device_list)

        # DISPLAY RATES
        self._widget_display_rates = ComboBoxDisplayRateList(self)
        self._widget_display_rates.setSizeAdjustPolicy(
            QComboBox.AdjustToContents
        )
        shortcut_key = 'Ctrl+Shift+r'
        shortcut = QShortcut(QKeySequence(shortcut_key), self)

        def show_popup():
            self._widget_display_rates.showPopup()

        shortcut.activated.connect(show_popup)
        self._widget_display_rates.setToolTip(
            compose_tooltip('Select a display rate', shortcut_key)
        )
        observers.append(self._widget_display_rates)
        self._widget_display_rates.setEnabled(True)
        group_display.addWidget(self._widget_display_rates)
        observers.append(self._widget_display_rates)

        # # TEXT FIELD
        # self._textfield = GainList(self)
        # self._textfield.setSizeAdjustPolicy(
        #     QComboBox.AdjustToContents
        # )
        # shortcut_key = 'Ctrl+Shift+d'
        # shortcut = QShortcut(QKeySequence(shortcut_key), self)

        # def show_popup():
        #     self._widget_device_list.showPopup()

        # shortcut.activated.connect(show_popup)
        # self._widget_device_list.setToolTip(
        #     compose_tooltip('Select a device to connect', shortcut_key)
        # )
        # observers.append(self._textfield)
        # group_display.addWidget(self._widget_device_list)


        # ROI (REGION OF INTEREST)
        button_roi = ActionRoi(
            icon='crop.png', title='Crop image', parent=self,
            action=self.action_on_roi,
            is_enabled=self.is_enabled_on_roi
        )
        shortcut_key = 'Ctrl+j'
        button_roi.setToolTip(
            compose_tooltip('Crop image', shortcut_key)
        )
        button_roi.setShortcut(shortcut_key)
        button_roi.toggle()
        observers.append(button_roi)

        # SUM OF LINES IN CROPPED AREA
        button_sum = ActionSum(
            icon='crop.png', title='Analysis', parent=self,
            action=self.action_on_sum,
            is_enabled=self.is_enabled_on_sum
        )
        shortcut_key = 'Ctrl+j'
        button_sum.setToolTip(
            compose_tooltip('Analysis', shortcut_key)
        )
        button_sum.setShortcut(shortcut_key)
        button_sum.toggle()
        observers.append(button_sum)

        # ABOUT HARVESTER
        self._widget_about = About(self)
        button_about = ActionShowAbout(
            icon='about.png', title='About', parent=self,
            action=self.action_on_show_about
        )
        button_about.setToolTip(
            compose_tooltip('Show information about Harvester')
        )
        button_about.toggle()
        observers.append(button_about)

        # Configure observers:

        #
        button_select_file.add_observer(button_update)
        button_select_file.add_observer(button_connect)
        button_select_file.add_observer(button_disconnect)
        button_select_file.add_observer(button_dev_attribute)
        button_select_file.add_observer(button_start_image_acquisition)
        button_select_file.add_observer(button_toggle_drawing)
        button_select_file.add_observer(button_stop_image_acquisition)
        button_select_file.add_observer(button_roi)
        button_select_file.add_observer(button_sum)
        button_select_file.add_observer(self._widget_device_list)
        button_select_file.add_observer(self._widget_device_list2)
        button_select_file.add_observer(self._widget_device_list3)

        #
        button_update.add_observer(self._widget_device_list)
        button_update.add_observer(self._widget_device_list2)
        button_update.add_observer(self._widget_device_list3)
        button_update.add_observer(button_connect)
        button_update.add_observer(button_roi)
        button_update.add_observer(button_sum)

        #
        button_connect.add_observer(button_select_file)
        button_connect.add_observer(button_update)
        button_connect.add_observer(button_disconnect)
        button_connect.add_observer(button_dev_attribute)
        button_connect.add_observer(button_start_image_acquisition)
        button_connect.add_observer(button_toggle_drawing)
        button_connect.add_observer(button_stop_image_acquisition)
        button_connect.add_observer(self._widget_device_list)
        button_connect.add_observer(self._widget_device_list2)
        button_connect.add_observer(self._widget_device_list3)
        button_connect.add_observer(button_roi)
        button_connect.add_observer(button_sum)

        #
        button_disconnect.add_observer(button_select_file)
        button_disconnect.add_observer(button_update)
        button_disconnect.add_observer(button_connect)
        button_disconnect.add_observer(button_dev_attribute)
        button_disconnect.add_observer(button_start_image_acquisition)
        button_disconnect.add_observer(button_toggle_drawing)
        button_disconnect.add_observer(button_stop_image_acquisition)
        button_disconnect.add_observer(self._widget_device_list)
        button_disconnect.add_observer(self._widget_device_list2)
        button_disconnect.add_observer(self._widget_device_list3)
        button_disconnect.add_observer(button_roi)
        button_disconnect.add_observer(button_sum)

        #
        # button_test.add_observer(button_update)
        # button_test.add_observer(button_connect)
        # button_test.add_observer(button_disconnect)
        # button_test.add_observer(button_dev_attribute)
        # button_test.add_observer(button_start_image_acquisition)
        # button_test.add_observer(button_toggle_drawing)
        # button_test.add_observer(button_stop_image_acquisition)
        # button_test.add_observer(self._widget_device_list)
        # button_test.add_observer(self._widget_device_list2)

        #
        button_start_image_acquisition.add_observer(button_toggle_drawing)
        button_start_image_acquisition.add_observer(button_stop_image_acquisition)

        #
        button_toggle_drawing.add_observer(button_start_image_acquisition)
        button_toggle_drawing.add_observer(button_stop_image_acquisition)

        #
        button_stop_image_acquisition.add_observer(button_start_image_acquisition)
        button_stop_image_acquisition.add_observer(button_toggle_drawing)

        # Add buttons to groups:

        #
        group_gentl_info.addAction(button_select_file)
        # group_gentl_info.addAction(button_test)
        group_gentl_info.addAction(button_update)

        #
        group_connection.addAction(button_connect)
        group_connection.addAction(button_disconnect)

        #
        group_device.addAction(button_start_image_acquisition)
        group_device.addAction(button_toggle_drawing)
        group_device.addAction(button_stop_image_acquisition)
        group_device.addAction(button_roi)
        group_device.addAction(button_sum)
        group_device.addAction(button_dev_attribute)

        #
        group_help.addAction(button_about)

        # Connect handler functions:

        #
        group_gentl_info.actionTriggered[QAction].connect(
            self.on_button_clicked_action
        )
        group_connection.actionTriggered[QAction].connect(
            self.on_button_clicked_action
        )
        group_device.actionTriggered[QAction].connect(
            self.on_button_clicked_action
        )
        group_display.actionTriggered[QAction].connect(
            self.on_button_clicked_action
        )
        group_help.actionTriggered[QAction].connect(
            self.on_button_clicked_action
        )

    @staticmethod
    def on_button_clicked_action(action):
        action.execute()

    @property
    def action_stop_image_acquisition(self):
        return self._action_stop_image_acquisition

    @property
    def ia(self):
        return self._ia

    @ia.setter
    def ia(self, value):
        self._ia = value

    # def on_mouse_press(self, event):
    #     self._is_dragging = True
    #     ###
    #     self._origin = event.pos
    #     print(self._origin)
    #     delta = event.pos - self._origin
    #     print(self._width)
    #     print(self._height)
    #     #deltaX = self.width - self._origin[0]
    #     print(delta)
    #     self._origin = event.pos
    #     self._x_click = self._origin[0]
    #     self._y_click = self._origin[1]
    #     self._origin[0] = 0
    #     self._origin[1] = 0
    #     print(self._x_click)
    #     print(self._y_click)

    # def on_mouse_release(self, event):
    #     self._is_dragging = False
    #     ###
    #     self._origin2 = event.pos
    #     print(self._origin2)
    #     self._x_release = self._coordinate[0]
    #     self._y_release = self._coordinate[1]
    #     self._coordinate[0] = 0
    #     self._coordinate[1] = 0
    #     print(self._x_release)
    #     print(self._y_release)

    def action_on_connect(self):
        #
        try:
            self._ia = self.harvester_core.create(
                self.device_list.currentIndex()
            )
            # We want to hold one buffer to keep the chunk data alive:
            self._ia.num_buffers += 1
        except (
            NotInitializedException, InvalidHandleException,
            InvalidIdException, ResourceInUseException,
            InvalidParameterException, NotImplementedException,
            AccessDeniedException,
        ) as e:
            self._logger.error(e, exc_info=True)

        if not self._ia:
            # The device is not available.
            return

        #

        self.ia.thread_image_acquisition = _PyQtThread(
            parent=self, mutex=self._mutex
        )
        self.ia.signal_stop_image_acquisition = self._signal_stop_image_acquisition
        self.ia.remote_device.node_map.ExposureTimeRaw.value = 16000
        self.ia.remote_device.node_map.ExposureTimeRaw.value = 1
        self._widget_device_list3.setValue(16000)
        self._width = int(self.ia.remote_device.node_map.Width.value)
        self._heigth = int(self.ia.remote_device.node_map.Height.value)
        self.standardWidth = self._width
        self.standardHeigth = self._heigth
        print(dir(self.ia.remote_device.node_map))
        print("BinningHorizontal ", self.ia.remote_device.node_map.BinningVertical.value)
        print(self._width)
        print(self._heigth)
        self._resize_window(self._width, self._heigth)

        try:
            if self.ia.remote_device.node_map:
                self._widget_attribute_controller = \
                    AttributeController(
                        self.ia.remote_device.node_map,
                        parent=self
                    )
        except AttributeError:
            pass

        #
        self.canvas.ia = self.ia

    def is_enabled_on_connect(self):
        enable = False
        if self.cti_files:
            if self.harvester_core.device_info_list:
                if self.ia is None:
                    enable = True
        return enable

    def action_on_disconnect(self):
        if self.attribute_controller:
            if self.attribute_controller.isVisible():
                self.attribute_controller.close()
                self._widget_attribute_controller = None

            # Discard the image acquisition manager.
            if self.ia:
                self.action_on_stop_image_acquisition()
                self.is_enabled_on_stop_image_acquisition()
                self.ia.remote_device.node_map.OffsetX.value = 0
                self.ia.remote_device.node_map.OffsetY.value = 0
                self.ia.remote_device.node_map.Width.value = 1280
                self.ia.remote_device.node_map.Height.value = 966
                print("OffsetX after disconnect ", self.ia.remote_device.node_map.OffsetX.value)
                print("OffsetY after disconnect ", self.ia.remote_device.node_map.OffsetY.value)
                print("Width after disconnect ", self.ia.remote_device.node_map.Width.value)
                print("Height after disconnect ", self.ia.remote_device.node_map.Height.value)
                self.ia.destroy()
                self._ia = None

    def is_enabled_on_disconnect(self):
        enable = False
        if self.cti_files:
            if self.ia:
                enable = True
        return enable

    def action_on_select_file(self):
        # Show a dialog and update the CTI file list.
        dialog = QFileDialog(self)
        dialog.setWindowTitle('Select a CTI file to load')
        dialog.setNameFilter('CTI files (*.cti)')
        dialog.setFileMode(QFileDialog.ExistingFile)

        if dialog.exec_() == QDialog.Accepted:
            #
            file_path = dialog.selectedFiles()[0]

            #
            self.harvester_core.reset()

            # Update the path to the target GenTL Producer.
            self.harvester_core.add_file(file_path)

            # Update the device list.
            self.harvester_core.update()

    def is_enabled_on_select_file(self):
        enable = False
        if self.ia is None:
            enable = True
        return enable

    def action_on_sum(self):
        with self.ia.fetch() as buffer:
            component = buffer.payload.components[0]

            _2d = component.data.reshape(
                component.height, component.width
            )

            lineSumHorizontal = _2d.sum(axis=1)
            lineSumVertical = _2d.sum(axis=0)
            
            plt.hist(lineSumVertical, density=True, bins=int(lineSumVertical.shape[0] / 8))
            plt.show()


    def is_enabled_on_sum(self):
        enable = False
        if self.cti_files:
            if self.ia:
                enable = True
        return enable

    def _set_exposition(self, value):
        try:
            self.action_on_stop_image_acquisition()
            self.is_enabled_on_stop_image_acquisition()
            self.ia.remote_device.node_map.ExposureTimeRaw.value = int(value)
            self.action_on_start_image_acquisition()
            self.is_enabled_on_start_image_acquisition()
        except AttributeError:
            pass
    
    def action_on_update_list(self):
        self.harvester_core.update_device_info_list()

    def is_enabled_on_update_list(self):
        enable = False
        if self.cti_files:
            if self.ia is None:
                enable = True
        return enable

    def action_on_roi(self):
        if self._cropped == 0:
            self._cropped += 1
            if self._widget_canvas._x_click % 8 != 0:
                if (self._widget_canvas._x_click - ((self._widget_canvas._x_click // 8) * 8)) <= np.abs((self._widget_canvas._x_click - (((self._widget_canvas._x_click // 8) * 8) + 8))):
                    x1 = int((self._widget_canvas._x_click // 8) * 8)
                else:
                    x1 = int(((self._widget_canvas._x_click // 8) * 8) + 8)
            else:
                x1 = int(self._widget_canvas._x_click)

            if self._widget_canvas._y_click % 8 != 0:
                if (self._widget_canvas._y_click - ((self._widget_canvas._y_click // 8) * 8)) <= np.abs((self._widget_canvas._y_click - (((self._widget_canvas._y_click // 8) * 8) + 8))):
                    y1 = int((self._widget_canvas._y_click // 8) * 8)
                else:
                    y1 = int((((self._widget_canvas._y_click // 8) * 8) + 8))
            else:
                y1 = int(self._widget_canvas._x_click)

            x2 = int(self._widget_canvas._x_release - x1)
            y2 = int(self._widget_canvas._y_release - y1)

            if x2 % 8 != 0:
                if (x2 - ((x2 // 8) * 8)) <= np.abs((x2 - (((x2 // 8) * 8) + 8))):
                    x2 = int((x2 // 8) * 8)
                else:
                    x2 = int(((x2 // 8) * 8) + 8)
            else:
                x2 = int(x2)

            if y2 % 8 != 0:
                if (y2 - ((y2 // 8) * 8)) <= np.abs((y2 - (((y2 // 8) * 8) + 8))):
                    y2 = int((y2 // 8) * 8)
                else:
                    y2 = int((((y2 // 8) * 8) + 8))
            else:
                y2 = int(y2)

            print('x1: ', x1)
            print('y1: ', y1)
            print('x2: ', x2)
            print('y2: ', y2)

            self.action_on_stop_image_acquisition()
            self.is_enabled_on_stop_image_acquisition()
            self.ia.remote_device.node_map.Width.value = self.ia.remote_device.node_map.Width.value - x1
            self.ia.remote_device.node_map.Height.value = self.ia.remote_device.node_map.Height.value - y1
            self.ia.remote_device.node_map.OffsetX.value = x1
            self.ia.remote_device.node_map.OffsetY.value = y1
            self.ia.remote_device.node_map.Width.value = x2
            self.ia.remote_device.node_map.Height.value = y2
            self.action_on_start_image_acquisition()
            self.is_enabled_on_start_image_acquisition()
        else:
            self.action_on_stop_image_acquisition()
            self.is_enabled_on_stop_image_acquisition()
            self.ia.remote_device.node_map.OffsetX.value = 0
            self.ia.remote_device.node_map.OffsetY.value = 0
            self.ia.remote_device.node_map.Width.value = self._width
            self.ia.remote_device.node_map.Height.value = self._heigth
            self.action_on_start_image_acquisition()
            self.is_enabled_on_start_image_acquisition()
            self._cropped -= 1


    def is_enabled_on_roi(self):
        enable = False
        if self.cti_files:
            if self.ia:
                enable = True
        return enable

    def action_on_start_image_acquisition(self):
        if self.ia.is_acquiring():
            # If it's pausing drawing images, just resume it and
            # immediately return this method.
            if self.canvas.is_pausing():
                self.canvas.resume_drawing()
        else:
            # Start statistics measurement:
            self.ia.statistics.reset()
            self._thread_statistics_measurement.start()

            #self.ia.start_image_acquisition()
            #self.ia.start()
            self.ia.start_acquisition()

    def is_enabled_on_start_image_acquisition(self):
        enable = False
        if self.cti_files:
            if self.ia:
                if not self.ia.is_acquiring() or \
                        self.canvas.is_pausing():
                    enable = True
        return enable

    def action_on_stop_image_acquisition(self):
        # Stop statistics measurement:
        self._thread_statistics_measurement.stop()

        # Release the preserved buffers, which the we kept chunk data alive,
        # before stopping image acquisition. Otherwise the preserved buffers
        # will be dangling after stopping image acquisition:
        self.canvas.release_buffers()

        # Then we stop image acquisition:
        #self.ia.stop_image_acquisition()
        self.ia.stop()

        # Initialize the drawing state:
        self.canvas.pause_drawing(False)

    def is_enabled_on_stop_image_acquisition(self):
        enable = False
        if self.cti_files:
            if self.ia:
                if self.ia.is_acquiring():
                    enable = True
        return enable

    def action_on_show_attribute_controller(self):
        if self.ia and self.attribute_controller.isHidden():
            self.attribute_controller.show()
            self.attribute_controller.expand_all()

    def is_enabled_on_show_attribute_controller(self):
        enable = False
        if self.cti_files:
            if self.ia is not None:
                enable = True
        return enable

    def action_on_toggle_drawing(self):
        self.canvas.toggle_drawing()

    def is_enabled_on_toggle_drawing(self):
        enable = False
        if self.cti_files:
            if self.ia:
                if self.ia.is_acquiring():
                    enable = True
        return enable

    def action_on_show_about(self):
        self.about.setModal(False)
        self.about.show()
    
    def _set_gain(self, value):
        try:
            if value == '1':
                print('1')
                self.action_on_stop_image_acquisition()
                self.is_enabled_on_stop_image_acquisition()
                self.ia.remote_device.node_map.GainRaw.value = 1
                self.action_on_start_image_acquisition()
                self.is_enabled_on_start_image_acquisition()
            elif value == '4':
                self.action_on_stop_image_acquisition()
                self.is_enabled_on_stop_image_acquisition()
                self.ia.remote_device.node_map.GainRaw.value = 4
                self.action_on_start_image_acquisition()
                self.is_enabled_on_start_image_acquisition()
            elif value == '16':
                self.action_on_stop_image_acquisition()
                self.is_enabled_on_stop_image_acquisition()
                self.ia.remote_device.node_map.GainRaw.value = 16
                self.action_on_start_image_acquisition()
                self.is_enabled_on_start_image_acquisition()
            elif value == '64':
                self.action_on_stop_image_acquisition()
                self.is_enabled_on_stop_image_acquisition()
                self.ia.remote_device.node_map.GainRaw.value = 64
                self.action_on_start_image_acquisition()
                self.is_enabled_on_start_image_acquisition()
            elif value == '255':
                self.action_on_stop_image_acquisition()
                self.is_enabled_on_stop_image_acquisition()
                self.ia.remote_device.node_map.GainRaw.value = 255
                self.action_on_start_image_acquisition()
                self.is_enabled_on_start_image_acquisition()
        except AttributeError:
            pass

    def _worker_update_statistics(self):
        #
        if self.ia is None:
            return

        #
        message_config = 'W: {0} x H: {1}, {2}, '.format(
            self.ia.remote_device.node_map.Width.value,
            self.ia.remote_device.node_map.Height.value,
            self.ia.remote_device.node_map.PixelFormat.value
        )
        #
        message_statistics = '{0:.1f} fps, elapsed {1}, {2} images, {3:.1f} fps'.format(
            self.ia.statistics.fps,
            str(datetime.timedelta(
                seconds=int(self.ia.statistics.elapsed_time_s)
            )),
            self.ia.statistics.num_images,
            self.ia.remote_device.node_map.AcquisitionFrameRate.value
        )
        #
        self._signal_update_statistics.emit(
            message_config + message_statistics
        )


class ActionSelectFile(Action):
    def __init__(
            self, icon=None, title=None, parent=None, action=None, is_enabled=None
    ):
        #
        super().__init__(
            icon=icon, title=title, parent=parent, action=action, is_enabled=is_enabled
        )

class ActionSum(Action):
    def __init__(
            self, icon=None, title=None, parent=None, action=None, is_enabled=None
    ):
        #
        super().__init__(
            icon=icon, title=title, parent=parent, action=action, is_enabled=is_enabled
        )


class ActionUpdateList(Action):
    def __init__(
            self, icon=None, title=None, parent=None, action=None, is_enabled=None
    ):
        #
        super().__init__(
            icon=icon, title=title, parent=parent, action=action, is_enabled=is_enabled
        )


class ActionConnect(Action):
    def __init__(
            self, icon=None, title=None, parent=None, action=None, is_enabled=None
    ):
        #
        super().__init__(
            icon=icon, title=title, parent=parent, action=action, is_enabled=is_enabled
        )


class ActionDisconnect(Action):
    def __init__(
            self, icon=None, title=None, parent=None, action=None, is_enabled=None
    ):
        #
        super().__init__(
            icon=icon, title=title, parent=parent, action=action, is_enabled=is_enabled
        )


class ActionStartImageAcquisition(Action):
    def __init__(
            self, icon=None, title=None, parent=None, action=None, is_enabled=None
    ):
        #
        super().__init__(
            icon=icon, title=title, parent=parent, action=action, is_enabled=is_enabled
        )


class ActionToggleDrawing(Action):
    def __init__(
            self, icon=None, title=None, parent=None, action=None, is_enabled=None
    ):
        #
        super().__init__(
            icon=icon, title=title, parent=parent, action=action, is_enabled=is_enabled,
            checkable=True
        )

    def _update(self):
        #
        checked = True if self.parent().canvas.is_pausing() else False
        self.setChecked(checked)


class ActionStopImageAcquisition(Action):
    def __init__(
            self, icon=None, title=None, parent=None, action=None, is_enabled=None
    ):
        #
        super().__init__(
            icon=icon, title=title, parent=parent, action=action, is_enabled=is_enabled
        )


class ActionShowAttributeController(Action):
    def __init__(
            self, icon=None, title=None, parent=None, action=None, is_enabled=None
    ):
        #
        super().__init__(
            icon=icon, title=title, parent=parent, action=action, is_enabled=is_enabled
        )

class ActionRoi(Action):
    def __init__(
            self, icon=None, title=None, parent=None, action=None, is_enabled=None
    ):
        #
        super().__init__(
            icon=icon, title=title, parent=parent, action=action, is_enabled=is_enabled
        )

class ActionShowAbout(Action):
    def __init__(
            self, icon=None, title=None, parent=None, action=None, is_enabled=None
    ):
        #
        super().__init__(
            icon=icon, title=title, parent=parent, action=action, is_enabled=is_enabled
        )

        #
        self._is_model = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    harvester = Harvester(vsync=True)
    harvester.show()
    sys.exit(app.exec_())
