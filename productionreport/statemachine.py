from enum import Enum

from helper import get_department
from readers import Reader


class State(Enum):
    BEFORE = 1
    SOURCE = 2
    DESTINATION = 3
    LOSS = 4


class StateMachine:
    def __init__(self, sources, destination, loss_states, loss_df, original_quantity):
        self.sources = sources.values
        self.destination = destination.values
        self.loss_states = loss_states.values
        self.loss_df = loss_df
        self.loss_df['ID'] = loss_df.index
        self.current_state = State.BEFORE
        # TODO: make it configurable
        self.ignore_states = ['ISSUED TO CS CONFIRMATION (A15)-GRG']
        self.current_status = ''
        self.last_status = ''
        self.original_quantity = original_quantity
        self.quantity = original_quantity
        self.last_status_before_loss = ''

    def next(self, row):
        oci_number = row['OCINumber']
        order_status = row['OrderStatus']
        production_quantity = 0

        if order_status in self.ignore_states:
            row['ProductionQuantity'] = 0
            return row

        self.check_if_loss_department_reached_again(order_status)
        self.update_last_and_current_status(order_status)

        if self.current_state == State.BEFORE:
            if order_status in self.sources:
                self.transition_to_source_state()

        elif self.current_state == State.SOURCE:
            if order_status in self.destination:
                production_quantity = self.transition_to_production_state()
            elif order_status in self.loss_states:
                self.transition_to_loss_state(oci_number)
            elif order_status not in self.sources:
                self.transition_to_production_state()

        elif self.current_state == State.DESTINATION:
            if order_status in self.loss_states:
                self.transition_to_loss_state(oci_number)

        elif self.current_state == State.LOSS:
            if order_status in self.sources:
                self.transition_to_source_state()
            elif order_status in self.destination:
                production_quantity = self.transition_to_production_state()

        row['ProductionQuantity'] = production_quantity
        return row

    def transition_to_source_state(self):
        self.current_state = State.SOURCE

    def transition_to_production_state(self):
        self.current_state = State.DESTINATION
        return self.quantity

    def transition_to_loss_state(self, oci_number):
        self.quantity = self.get_loss_quantity(oci_number)
        self.last_status_before_loss = self.last_status
        self.current_state = State.LOSS

    def check_if_loss_department_reached_again(self, order_status):
        if self.last_status_before_loss == order_status:
            self.quantity = self.original_quantity
            self.last_status_before_loss = ''

    def update_last_and_current_status(self, order_status):
        self.last_status = self.current_status
        self.current_status = order_status

    def get_loss_quantity(self, oci_number):
        department = get_department(self.last_status)
        df = self.loss_df[(self.loss_df['OCI'] == oci_number) & (self.loss_df['Department'] == department)]
        if len(df) == 0:
            print('Loss Quantity Not found for oci {} and department {}'.format(oci_number, department))
            return self.original_quantity
        quantity = df.iloc[0]['Quantity']
        self.loss_df = self.loss_df.drop(df.iloc[0]['ID'])
        return quantity


class StateManager:
    def __init__(self, states_file, loss_states, loss_df):
        self.loss_states = loss_states
        self.sources, self.destination = self.read_states(states_file)
        self.loss_df = loss_df

    @staticmethod
    def read_states(production_file):
        df = Reader.read_csv(production_file)
        return df['Source'], df['Destination']

    @staticmethod
    def get_order_quantity(df, oci):
        try:
            order_quantity = int(df[df['OrderStatus'] == 'CREATED']['OCIQty'])
        except TypeError:
            order_quantity = int(df.iloc[0]['OCIQty'])
        except:
            print('Order Quantity Error for OCI ', oci)
            order_quantity = 0
        return order_quantity

    def get_production(self, oci, df):
        rows = []
        order_quantity = self.get_order_quantity(df, oci)

        ds_state_machine = StateMachine(self.sources, self.destination, self.loss_states, self.loss_df, order_quantity)
        for _, row in df.iterrows():
            row = ds_state_machine.next(row)
            if row['ProductionQuantity'] != 0:
                rows[-1]['ProductionQuantity'] = row['ProductionQuantity']
                row['ProductionQuantity'] = 0
            rows.append(row)
        return rows
