import datetime

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
        df = self.add_production_date(df)
        df = self.add_department(df)
        df = self.add_building(df)
        df = self.sort(df)
        df = self.group_by_oci(df)
        return df

    def add_production_date(self, df):
        df['ProductionDate'] = \
            df.apply(lambda x: self.get_date_based_on_6am_format(x['DateOfChange'], x['ChangeOfTime']), axis=1)
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
    def get_date_based_on_6am_format(date, time):
        try:
            original_date = datetime.datetime.strptime(date, '%d/%m/%Y')
        except ValueError:
            original_date = datetime.datetime.strptime(date, '%d-%m-%Y')
        original_time = datetime.datetime.strptime(time, '%H:%M:%S')
        new_date = original_date
        if original_time.hour < 6:
            new_date = original_date - datetime.timedelta(days=1)
        return new_date.strftime('%d/%m/%Y')
