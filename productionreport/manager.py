import os
import timeit
from datetime import datetime

import pandas as pd

from department import DepartmentFinder
from all_dept_reporter import OneTimeProductionReporter
from preprocess import Preprocess, LossPreprocessor
from readers import ProductionFileReader, LossFileReader, LossStateReader, DepartmentFileReader, CustomerInfoReader
from reporter import ReportManager, DSTSReporter, FittingReporter


class Manager:
    def __init__(self, production_files, loss_files, production_columns_file, summary_file_dir, loss_state_file,
                 ds_ts_state_file, department_file, fitting_state_file, production_report, order_receipt_report,
                 customer_info_file):
        self.production_files = production_files
        self.loss_files = loss_files
        self.production_columns_file = production_columns_file
        self.summary_file = self.get_summary_file(summary_file_dir)
        self.loss_state_file = loss_state_file
        self.ds_state_file = ds_ts_state_file
        self.department_file = department_file
        self.fitting_state_file = fitting_state_file
        self.production_report = production_report
        self.order_receipt_report = order_receipt_report
        self.customer_info_file = customer_info_file

    @staticmethod
    def get_summary_file(summary_file_dir):
        current_time = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        return os.path.join(summary_file_dir, 'production_summary_{}.xlsx'.format(current_time))

    def manage(self):
        start = timeit.default_timer()

        production_df = ProductionFileReader(self.production_columns_file).read(self.production_files)

        customer_df = CustomerInfoReader.read(self.customer_info_file)

        production_df = pd.merge(production_df, customer_df, how='left', on='CustomerCode')

        loss_file_not_selected = (len(self.loss_files) == 0 or self.loss_files[0] == 'No Files Selected')

        if self.production_report and loss_file_not_selected:
            print('LOSS file is mandatory for production report !!!!!!!!!!!!!!!')
            return

        if not loss_file_not_selected:
            loss_df = LossFileReader.read(self.loss_files)
            loss_df = LossPreprocessor().preprocess(loss_df)
            loss_states_df = LossStateReader.read(self.loss_state_file)

        departments_df = DepartmentFileReader.read(self.department_file)
        department_finder = DepartmentFinder(departments_df)

        production_df = Preprocess().preprocess(production_df, department_finder)

        writer = pd.ExcelWriter(self.summary_file, engine='xlsxwriter')

        if self.production_report:
            ds_ts_reporter = DSTSReporter(writer, production_df, loss_df, loss_states_df, self.ds_state_file)
            fitting_reporter = FittingReporter(writer, production_df, loss_df, loss_states_df, self.fitting_state_file)
            reporters = ReportManager([ds_ts_reporter, fitting_reporter])
            reporters.generate_report()

        if self.order_receipt_report:
            one_time_prod_reporter = OneTimeProductionReporter(writer)
            one_time_prod_reporter.generate_report(production_df)

        writer.save()

        stop = timeit.default_timer()
        print('Time: ', stop - start)


if __name__ == '__main__':
    production_files_path = [r'../sample_data/Ex_Dom_Files/Dom_0506.csv']
    loss_files_path = [r'../sample_data/export_domestic_loss_27th_June.xlsx']
    production_columns_file_path = r'../data/production_columns.csv'
    summary_file_dir_path = r'../sample_data'
    loss_state_file_path = r'../data/loss_states.csv'
    ds_state_file_path = r'../data/ds_ts_states.csv'
    department_file_path = r'../data/departments.xlsx'
    fitting_state_file_path = r'../data/fitting_states.csv'
    manager = Manager(production_files_path, loss_files_path, production_columns_file_path, summary_file_dir_path,
                      loss_state_file_path, ds_state_file_path, department_file_path, fitting_state_file_path)
    manager.manage()
