import datetime

import pandas as pd

from helper import get_lab, get_department


class LossPreprocessor:
    def preprocess(self, df):
        return self.combine_consecutive_losses_for_same_oci(df)

    @staticmethod
    def combine_consecutive_losses_for_same_oci(df):
        columns_to_shift = ['OCI', 'Department', 'Date']
        shifted_columns = ['OCI X', 'Department X', 'Date X']
        df[shifted_columns] = df[columns_to_shift].shift()
        df = df.groupby(((df['OCI'] != df['OCI X']) | (df['Date'] != df['Date X'])).cumsum()). \
            agg({'OCI': 'first', 'Quantity': 'sum', 'Department': 'first', 'Date': 'first'})
        return df


class Preprocess:
    def preprocess(self, df):
        df = self.set_datatype(df)
        df = self.sort(df)
        df = self.add_production_date(df)
        df = self.add_department(df)
        df = self.add_building(df)
        df = self.group_by_oci(df)
        return df

    def add_production_date(self, df):
        columns_to_shift = ['DateOfChange', 'ChangeOfTime']
        shifted_columns = ['DateOfChange X', 'ChangeOfTime X']
        df[shifted_columns] = df[columns_to_shift].shift(-1)
        df['ProductionDate'] = df.apply(
            lambda x: self.get_date_based_on_7am_format(x['DateOfChange X'], x['ChangeOfTime X']), axis=1)
        df = df.drop(columns=shifted_columns)
        return df

    @staticmethod
    def set_datatype(df):
        df['DateOfChange'] = pd.to_datetime(df['DateOfChange'], dayfirst=True).dt.date
        df['ChangeOfTime'] = pd.to_datetime(df['ChangeOfTime'], format='%H:%M:%S').dt.time
        return df

    @staticmethod
    def add_department(df):
        df['Department'] = df['OrderStatus'].apply(get_department)
        return df

    @staticmethod
    def add_building(df):
        df['LAB'] = df['OrderStatus'].apply(get_lab)
        return df

    @staticmethod
    def sort(df):
        return df.sort_values(['OCINumber', 'DateOfChange', 'ChangeOfTime'])

    @staticmethod
    def group_by_oci(df):
        return df.groupby(['OCINumber'])

    @staticmethod
    def get_date_based_on_7am_format(date, time):
        if pd.isnull(date) or pd.isnull(time):
            return pd.NaT

        new_date = date
        if time.hour < 7:
            new_date = new_date - datetime.timedelta(days=1)
        return new_date
