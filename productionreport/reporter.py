from abc import ABC, abstractmethod

import pandas as pd

from statemachine import StateManager


class ReportManager:
    def __init__(self, reporters):
        self.reporters = reporters

    def generate_report(self):
        for reporter in self.reporters:
            print('Running {} ...'.format(reporter.name()))
            reporter.generate_report()


class Reporter(ABC):
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def generate_report(self):
        pass


class DSTSReporter(Reporter):
    def __init__(self, writer, production_df, loss_df, loss_states_df, states_file):
        self.writer = writer
        self.production_df = production_df
        self.state_manager = StateManager(states_file, loss_states_df['Loss States'], loss_df)
        self.oci_sheet_name = 'DS_TS_OCI'

    def name(self):
        return 'DS TS Reporter'

    def generate_report(self):
        rows = []
        for oci, group in self.production_df:
            rows.extend(self.state_manager.get_production(oci, group))
        df = pd.DataFrame(rows)
        df.to_excel(self.writer, sheet_name=self.oci_sheet_name, index=False)
