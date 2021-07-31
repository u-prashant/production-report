class OneTimeProductionReporter:
    def __init__(self, writer):
        self.writer = writer
        self.sheet_name = 'single_production_count'
        self.columns = ['OCINumber', 'CustomerName', 'OCIQty', 'OrderDate', 'TS A2', 'TS A14', 'TS A15', 'DS A2',
                        'DS A14', 'DS A15', 'FITT A2', 'FITT A14', 'FITT A15', 'TC A2', 'TC A14', 'TC A15', 'TMC A2',
                        'TMC A14', 'TMC A15', 'TINT A2', 'TINT A14', 'TINT A15']

    def get_one_time_production(self, df):
        departments = self.columns[4:]
        for dept in departments:
            df[dept] = 0
        ndf = df[self.columns[1:]].iloc[:1]
        order_quantity = df['OCIQty'].iloc[0]
        depts = ['TS', 'DS', 'FITT', 'TC', 'TMC', 'TINT']
        for dept in depts:
            has_production, lab = OneTimeProductionReporter.get_dept_prod(df, dept)
            if has_production:
                ndf[dept + ' ' + lab].iloc[0] = order_quantity
        return ndf

    @staticmethod
    def get_dept_prod(df, dept):
        last_dept = ''
        lab = 'A15'
        for index, row in df.iterrows():
            if row['Department'] == 'CS':
                continue
            if last_dept == dept and row['Department'] != dept:
                return True, lab
            last_dept = row['Department']
            lab = row['LAB']
        return False, lab

    def generate_report(self, production_df):
        production_df = production_df.apply(
            lambda x: self.get_one_time_production(x))
        production_df = production_df.reset_index()
        production_df = production_df[self.columns]
        print('writing single time production count to file...')
        production_df.to_excel(self.writer, sheet_name=self.sheet_name, index=False)
