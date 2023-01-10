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

# Related third party imports
from PyQt5.QtWidgets import QComboBox

# Local application/library specific imports
from harvesters_gui._private.frontend.pyqt5.helper import get_system_font


class ComboBoxDisplayRateList(QComboBox):
    #
    _dict_disp_rates = {'1 fps': 0, '2 fps': 1, '5 fps': 2, '30 fps': 3, '60 fps': 4}

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(get_system_font())
        for d in self._dict_disp_rates:
            self.addItem(d)
        self.setCurrentIndex(self._dict_disp_rates['30 fps'])
        self.currentTextChanged.connect(self._set_display_rate)

    def _set_display_rate(self, value):
        if value == '1 fps': 
            display_rate = 1.
        elif value == '2 fps': 
            display_rate = 2.
        elif value == '5 fps': 
            display_rate = 5.
        elif value == '30 fps':
            display_rate = 30.
        else:
            display_rate = 60.
        self.parent().parent().canvas.display_rate = display_rate

