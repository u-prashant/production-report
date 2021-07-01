import pandas as pd


class Reader:
    @staticmethod
    def read_csv(file):
        return pd.read_csv(file)

    @staticmethod
    def read_excel(file):
        return pd.read_excel(file)


class ProductionFileReader:
    def __init__(self, columns_file):
        self.columns = self.get_column_names(columns_file)

    @staticmethod
    def get_column_names(columns_file):
        return pd.read_csv(columns_file).columns

    def read(self, production_files):
        dfs = []
        for file in production_files:
            print('Reading {} file...'.format(file))
            dfs.append(Reader.read_csv(file)[self.columns])
        return pd.concat(dfs)


class LossFileReader:
    @staticmethod
    def read(loss_files):
        dfs = []
        for file in loss_files:
            print('Reading {} file...'.format(file))
            dfs.append(Reader.read_excel(file))
        return pd.concat(dfs)


class LossStateReader:
    @staticmethod
    def read(loss_state_file):
        return Reader.read_csv(loss_state_file)
