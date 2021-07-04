from enum import Enum

from helper import get_department
from readers import Reader


class State(Enum):
    INITIAL = 'INITIAL'
    SOURCE_1 = 'SOURCE_1'
    SOURCE_2 = 'SOURCE_2'
    TARGET_1 = 'TARGET_1'
    TARGET_2 = 'TARGET_2'
    LOSS = 'LOSS'
    OTHER_1 = 'OTHER_1'
    OTHER_2 = 'OTHER_2'
    OTHER_3 = 'OTHER_3'


class StateMachine:
    def __init__(self, source_states, target_states, loss_states, ignore_states, loss_finder, oci_number,
                 order_quantity):
        self.sources_states = source_states
        self.target_states = target_states
        self.loss_states = loss_states
        self.ignore_states = ignore_states
        self.loss_finder = loss_finder

        self.oci_number = oci_number
        self.order_quantity = order_quantity
        self.quantity = [order_quantity]

        self.current_state = State.INITIAL
        self.last_states = []

        self.current_status = ''
        self.last_status = []

        self.last_status_before_loss = ['']

    def update_states(self, state, order_status):
        self.last_states.append(self.current_state)
        self.current_state = state
        self.last_status.append(self.current_status)
        self.current_status = order_status

    def move_to_initial_state(self, order_status):
        self.update_states(State.INITIAL, order_status)
        return 0

    def move_to_source_state_1(self, order_status):
        self.update_states(State.SOURCE_1, order_status)
        return 0

    def move_to_source_state_2(self, order_status):
        self.update_states(State.SOURCE_2, order_status)
        return 0

    def move_to_target_state_1(self, order_status):
        self.update_states(State.TARGET_1, order_status)
        quantity = 0
        if self.last_states[-1] in (State.SOURCE_1, State.OTHER_1):
            quantity = self.quantity[-1]
        return quantity

    def move_to_target_state_2(self, order_status):
        self.update_states(State.TARGET_2, order_status)
        return 0

    def move_to_other_state_1(self, order_status):
        self.update_states(State.OTHER_1, order_status)
        return 0

    def move_to_other_state_2(self, order_status):
        self.update_states(State.OTHER_2, order_status)
        return 0

    def move_to_other_state_3(self, order_status):
        self.update_states(State.OTHER_3, order_status)
        return 0

    def move_to_loss_state(self, order_status):
        if self.current_state == State.LOSS:
            return 0
        self.last_status_before_loss.append(self.current_status)
        self.update_states(State.LOSS, order_status)
        department = get_department(self.last_status[-1])
        quantity = self.loss_finder.get_quantity(self.oci_number, department)
        if quantity == 0:
            quantity = self.order_quantity
        self.quantity.append(quantity)
        return 0

    def move_to_ignore_state(self, order_status):
        return 0

    def handle_initial_state(self, order_status):
        if order_status in self.sources_states:
            return self.move_to_source_state_1(order_status)
        elif self.ignore_states in order_status:
            return self.move_to_ignore_state(order_status)
        else:
            return self.move_to_initial_state(order_status)

    def handle_source_state_1(self, order_status):
        if order_status in self.sources_states:
            return self.move_to_source_state_1(order_status)
        elif order_status in self.target_states:
            return self.move_to_target_state_1(order_status)
        elif order_status in self.loss_states:
            return self.move_to_loss_state(order_status)
        elif self.ignore_states in order_status:
            return self.move_to_ignore_state(order_status)
        else:
            return self.move_to_other_state_1(order_status)

    def handle_source_state_2(self, order_status):
        if order_status in self.sources_states:
            return self.move_to_source_state_2(order_status)
        elif order_status in self.target_states:
            return self.move_to_target_state_1(order_status)
        elif order_status in self.loss_states:
            return self.move_to_loss_state(order_status)
        elif self.ignore_states in order_status:
            return self.move_to_ignore_state(order_status)
        else:
            return self.move_to_other_state_2(order_status)

    def handle_target_state_1(self, order_status):
        if order_status in self.sources_states:
            return self.move_to_source_state_2(order_status)
        elif order_status in self.target_states:
            return self.move_to_target_state_1(order_status)
        elif order_status in self.loss_states:
            return self.move_to_loss_state(order_status)
        elif self.ignore_states in order_status:
            return self.move_to_ignore_state(order_status)
        else:
            return self.move_to_other_state_2(order_status)

    def handle_target_state_2(self, order_status):
        if order_status in self.sources_states:
            return self.move_to_source_state_1(order_status)
        elif order_status in self.target_states:
            return self.move_to_target_state_2(order_status)
        elif order_status in self.loss_states:
            return self.move_to_loss_state(order_status)
        elif self.ignore_states in order_status:
            return self.move_to_ignore_state(order_status)
        else:
            return self.move_to_other_state_3(order_status)

    def handle_other_state_1(self, order_status):
        if order_status in self.sources_states:
            return self.move_to_source_state_1(order_status)
        elif order_status in self.target_states:
            return self.move_to_target_state_1(order_status)
        elif order_status in self.loss_states:
            return self.move_to_loss_state(order_status)
        elif self.ignore_states in order_status:
            return self.move_to_ignore_state(order_status)
        else:
            return self.move_to_other_state_1(order_status)

    def handle_other_state_2(self, order_status):
        if order_status in self.sources_states:
            return self.move_to_source_state_2(order_status)
        elif order_status in self.target_states:
            return self.move_to_target_state_1(order_status)
        elif order_status in self.loss_states:
            return self.move_to_loss_state(order_status)
        elif self.ignore_states in order_status:
            return self.move_to_ignore_state(order_status)
        else:
            return self.move_to_other_state_2(order_status)

    def handle_other_state_3(self, order_status):
        if order_status in self.sources_states:
            return self.move_to_source_state_1(order_status)
        elif order_status in self.target_states:
            return self.move_to_target_state_2(order_status)
        elif order_status in self.loss_states:
            return self.move_to_loss_state(order_status)
        elif self.ignore_states in order_status:
            return self.move_to_ignore_state(order_status)
        else:
            return self.move_to_other_state_3(order_status)

    def handle_loss_state(self, order_status):
        if order_status in self.sources_states:
            return self.move_to_source_state_1(order_status)
        elif order_status in self.target_states:
            return self.move_to_target_state_2(order_status)
        elif order_status in self.loss_states:
            return self.move_to_loss_state(order_status)
        elif self.ignore_states in order_status:
            return self.move_to_ignore_state(order_status)
        else:
            return self.move_to_other_state_3(order_status)

    def check_if_loss_department_reached_again(self, order_status):
        if self.last_status_before_loss[-1] == order_status:
            self.quantity.pop()
            self.last_status_before_loss.pop()

    def next(self, order_status):
        self.check_if_loss_department_reached_again(order_status)
        if self.current_state == State.INITIAL:
            quantity = self.handle_initial_state(order_status)
        elif self.current_state == State.SOURCE_1:
            quantity = self.handle_source_state_1(order_status)
        elif self.current_state == State.SOURCE_2:
            quantity = self.handle_source_state_2(order_status)
        elif self.current_state == State.TARGET_1:
            quantity = self.handle_target_state_1(order_status)
        elif self.current_state == State.TARGET_2:
            quantity = self.handle_target_state_2(order_status)
        elif self.current_state == State.OTHER_1:
            quantity = self.handle_other_state_1(order_status)
        elif self.current_state == State.OTHER_2:
            quantity = self.handle_other_state_2(order_status)
        elif self.current_state == State.OTHER_3:
            quantity = self.handle_other_state_3(order_status)
        elif self.current_state == State.LOSS:
            quantity = self.handle_loss_state(order_status)
        return quantity


class LossFinder:
    def __init__(self, loss_info_df):
        self.loss_df = self.preprocess_loss_info(loss_info_df)

    @staticmethod
    def preprocess_loss_info(df):
        df['ID'] = df.index
        return df

    def get_quantity(self, oci_number, department):
        if department == '':
            print('Loss Quantity Not found for oci {}'.format(oci_number))
            return 0

        # final qc loss should be taken from tc or tmc
        departments = [department]
        if department == 'FINAL QC':
            departments.extend(['TC', 'TMC', 'CS'])

        df = self.loss_df[(self.loss_df['OCI'] == oci_number) & (self.loss_df['Department'].isin(departments))]
        if len(df) == 0:
            print('Loss Quantity Not found for oci {} and department {}'.format(oci_number, department))
            return 0
        quantity = df.iloc[0]['Quantity']
        self.loss_df = self.loss_df.drop(df.iloc[0]['ID'])
        return quantity


class StateManager:
    def __init__(self, states_file, loss_states_df, loss_info_df):
        self.loss_states = self.get_loss_states(loss_states_df)
        self.source_states, self.target_states = self.get_source_target_states(states_file)
        self.ignore_states = self.get_ignore_states()
        self.loss_finder = LossFinder(loss_info_df)

    @staticmethod
    def get_ignore_states():
        # TODO: read from file
        return 'CONFIRMATION'

    @staticmethod
    def get_loss_states(df):
        return set(df['Loss States'].values)

    @staticmethod
    def get_source_target_states(file):
        df = Reader.read_csv(file)
        return set(df['Source'].values), set(df['Target'].values)

    @staticmethod
    def get_order_quantity(df):
        return int(df.iloc[0]['OCIQty'])

    def update_quantity(self, rows, quantity):
        if quantity == 0:
            return
        for index in range(len(rows) - 1, 0, -1):
            if rows[index]['OrderStatus'] in self.source_states:
                rows[index]['ProductionQuantity'] = quantity
                return

    def get_production(self, oci, df):
        rows = []
        order_quantity = self.get_order_quantity(df)
        state_machine = StateMachine(self.source_states, self.target_states, self.loss_states, self.ignore_states,
                                     self.loss_finder, oci, order_quantity)
        for _, row in df.iterrows():
            quantity = state_machine.next(row['OrderStatus'])
            row['ProductionQuantity'] = 0
            self.update_quantity(rows, quantity)
            rows.append(row)
        return rows
