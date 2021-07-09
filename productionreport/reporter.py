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
        print('Reports Generated !!!')


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
        self.state_manager = StateManager(states_file, loss_states_df, loss_df)
        self.oci_sheet_name = 'DS_TS_OCI'
        self.zero_production_oci_sheet_name = '0 Production OCIs'
        self.zero_production_without_invoice_sheet_name = 'Without invoice OCIs'

    def name(self):
        return 'DS TS Reporter'

    def generate_report(self):
        df = self.filter_production_rows()
        self.generate_zero_production_oci(df)
        self.generate_zero_production_without_invoice_oci(df)

    def filter_production_rows(self):
        rows = []
        for oci, group in self.production_df:
            rows.extend(self.state_manager.get_production(oci, group))
        df = pd.DataFrame(rows)
        print('writing production rows to file...')
        df.to_excel(self.writer, sheet_name=self.oci_sheet_name, index=False)
        return df

    def generate_zero_production_without_invoice_oci(self, df):
        without_invoice_oci = df.groupby(['OCINumber']).filter(
            lambda x: not x['Department'].str.contains('INVOICED').any())[
            'OCINumber'].unique()
        without_invoice_oci_df = pd.DataFrame(without_invoice_oci, columns=['OCINumber'])
        print('writing non-invoiced production OCIs to file...')
        without_invoice_oci_df.to_excel(self.writer, sheet_name=self.zero_production_without_invoice_sheet_name,
                                        index=False)

    def generate_zero_production_oci(self, df):
        oci = df.groupby(['OCINumber']).filter(
            lambda x: (x['ProductionQuantity'].sum() == 0) & (x['Department'].str.contains('TS|DS').any()))[
            'OCINumber'].unique()
        zero_prod_df = pd.DataFrame(oci, columns=['OCINumber'])
        print('writing zero production OCIs to file...')
        zero_prod_df.to_excel(self.writer, sheet_name=self.zero_production_oci_sheet_name, index=False)
