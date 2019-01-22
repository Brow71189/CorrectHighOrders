import gettext
import numpy as np
from scipy.linalg import lstsq
import threading
import logging

from nion.utils import Registry

_ = gettext.gettext

class CorrectPanelDelegate(object):

    def __init__(self, api):
        self.__api = api
        self.panel_id = 'Correct-High-Orders-Panel'
        self.panel_name = _('Correct High Orders')
        self.panel_positions = ['left', 'right']
        self.panel_position = 'right'
        self.settings = {'order': 'C4s'}
        self.knobs = {'C4s': ['6Sa', '6Sb', '11Sa', '11Sb', '16Sa', '16Sb']}
        self.aberrations = {'C4s': ['C41.', 'C43.', 'C45.']}
        self.__excitations = {}
        self.stem_controller = Registry.get_component('stem_controller')

    def get_aberrations_for_order(self, order, axis='ab'):
        _control_list = self.aberrations[order]
        control_list = []
        for control in _control_list:
            if control.endswith('.'):
                control_list.extend([control+axis[0], control+axis[1]])
            else:
                control_list.append(control)
        return control_list

    def get_variables_for_order(self, order, axis='ab'):
        _control_list = self.aberrations[order]
        control_list = []
        for control in _control_list:
            if control.endswith('.'):
                control_list.extend(['v'+control[:-1]+axis[0], 'v'+control[:-1]+axis[1]])
            else:
                control_list.append(control)
        return control_list

    def calculate_excitations_for_order(self, order, connect_string='->'):
        knobs = self.knobs[order]
        aberrations = self.get_aberrations_for_order(order)
        variables = self.get_variables_for_order(order)
        correction_matrix = np.zeros((len(variables), len(knobs)))
        for j in range(len(variables)):
            for i in range(len(knobs)):
                correction_matrix[j, i] = self.stem_controller.GetVal(knobs[i] + connect_string + variables[j])
        aberration_coefficients = np.zeros(len(aberrations))
        for i in range(len(aberrations)):
            aberration_coefficients[i] = self.stem_controller.GetVal(aberrations[i])
        result = lstsq(correction_matrix, aberration_coefficients)
        self.__excitations[order] = result[0]
        self.update_result_widget(order, correction_matrix, result[0], aberration_coefficients)
        residues = np.abs(np.dot(correction_matrix, result[0]) - aberration_coefficients)
        logging.info(f'\nResidues (abs([M][S]-[C])):\n{residues[:, np.newaxis]}')
        return result

    def apply_excitations_for_order(self, order):
        if self.__excitations.get(order) is not None:
            excitations = self.__excitations.pop(order)
            knobs = self.knobs[order]
            for i in range(len(knobs)):
                self.stem_controller.SetVal(knobs[i], excitations[i])

    def update_result_widget(self, order, matrix, excitations, aberrations):
        symbol_position = int(matrix.shape[0]/2)
        split_str_matrix = []
        split_str_excitations = []
        split_str_aberrations = []
        times = []
        equals = []
        for i in range(matrix.shape[0]):
            # symbols
            if i == symbol_position:
                times.append(' x ')
                equals.append(' = ')
            else:
                times.append('   ')
                equals.append('   ')
            # matrix
            row = matrix[i]
            if i == 0:
                row_str = '['
            else:
                row_str = ' '
            for k in range(len(row)):
                if k == 0:
                    row_str += '['
                row_str += '{: .2e}'.format(row[k])
                if k == len(row) - 1:
                    row_str += ']'
                else:
                    row_str += ' '
            if i == matrix.shape[0] - 1:
                row_str += ']'
            else:
                row_str += ' '
            split_str_matrix.append(row_str)
            # excitations and aberrations
            excitations_str = ''
            aberrations_str = ''
            if i == 0:
                excitations_str += '['
                aberrations_str += '['
            else:
                excitations_str += ' '
                aberrations_str += ' '
            excitations_str += '{: .2e}'.format(excitations[i])
            aberrations_str += '{: .2e}'.format(aberrations[i])
            if i == matrix.shape[0] - 1:
                excitations_str += ']'
                aberrations_str += ']'
            else:
                excitations_str += ' '
                aberrations_str += ' '
            split_str_excitations.append(excitations_str)
            split_str_aberrations.append(aberrations_str)

        result_str = f'\nResults for {order} ([M][S]=[C]):\n'
        for i in range(len(split_str_matrix)):
            result_str += f'{split_str_matrix[i]}{times[i]}{split_str_excitations[i]}{equals[i]}{split_str_aberrations[i]}\n'
        logging.info(result_str)
        def update_widget():
            self.result_widget.text = result_str
        self.__api.queue_task(update_widget)

    def create_panel_widget(self, ui, document_controller):
        def calculate_clicked():
            def run_calculate():
                settings = self.settings.copy()
                try:
                    self.calculate_excitations_for_order(settings['order'])
                finally:
                    if self.__excitations.get(settings['order']) is not None:
                        self.update_button_state(self.apply_button, True)
                    else:
                        self.update_button_state(self.apply_button, False)
                    self.update_button_state(self.calculate_button, True)
            self.update_button_state(self.calculate_button, False)
            threading.Thread(target=run_calculate).start()

        def apply_clicked():
            def run_apply():
                settings = self.settings.copy()
                self.apply_excitations_for_order(settings['order'])
            self.update_button_state(self.apply_button, False)
            threading.Thread(target=run_apply).start()

        def aberrations_combo_changed(current_item):
            self.settings['order'] = current_item
            if self.__excitations.get(current_item) is not None:
                self.update_button_state(self.apply_button, True)

        column = ui.create_column_widget()

        aberrations_label = ui.create_label_widget('Aberrations: ')
        self.aberrations_combo = ui.create_combo_box_widget(list(self.aberrations.keys()))
        self.aberrations_combo.on_current_item_changed = aberrations_combo_changed
        self.calculate_button = ui.create_push_button_widget('Calculate')
        self.calculate_button.on_clicked = calculate_clicked
        self.apply_button = ui.create_push_button_widget('Apply')
        self.apply_button.on_clicked = apply_clicked
        self.result_widget = ui.create_text_edit_widget()
        self.result_widget._widget.editable = False

        row1 = ui.create_row_widget()
        row1.add_spacing(5)
        row1.add(aberrations_label)
        row1.add(self.aberrations_combo)
        row1.add_spacing(5)
        row1.add_stretch()

        row2 = ui.create_row_widget()
        row2.add_spacing(5)
        row2.add(self.calculate_button)
        row2.add_spacing(5)
        row2.add(self.apply_button)
        row2.add_spacing(5)
        row2.add_stretch()

        row3 = ui.create_row_widget()
        row3.add_spacing(5)
        row3.add(self.result_widget)
        row3.add_spacing(5)

        column.add_spacing(5)
        column.add(row1)
        column.add_spacing(10)
        column.add(row2)
        #column.add_spacing(5)
        #column.add(row3)
        column.add_spacing(5)
        column.add_stretch()

        self.apply_button._widget.enabled = False

        return column

    def update_button_state(self, button, state):
        def update():
            button._widget.enabled = state
        self.__api.queue_task(update)


class CorrectGUIExtension(object):
    extension_id = 'nions.correct_high_orders'

    def __init__(self, api_broker):
        api = api_broker.get_api(version='1', ui_version='1')
        self.__panel_ref = api.create_panel(CorrectPanelDelegate(api))

    def close(self):
        self.__panel_ref.close()
        self.__panel_ref = None