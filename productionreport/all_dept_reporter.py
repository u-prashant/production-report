class OneTimeProductionReporter:
    def __init__(self, writer):
        self.writer = writer
        self.sheet_name = 'single_production_count'
        self.columns = ['OCINumber', 'CustomerName', 'OCIQty', 'OrderDate', 'TS A2', 'TS A14', 'TS A15', 'DS A2',
                        'DS A14', 'DS A15', 'FITT A2', 'FITT A14', 'FITT A15', 'TC A2', 'TC A14', 'TC A15', 'TMC A2',
                        'TMC A14', 'TMC A15', 'TINT A2', 'TINT A14', 'TINT A15', 'INVOICED', 'DISPATCH', 'CANCELLED']

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

        for dept in self.columns[22:]:
            if dept in df['Department'].values:
                ndf[dept].iloc[0] = order_quantity

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
        one_time_reporter_df = production_df.apply(lambda x: self.get_one_time_production(x))
        one_time_reporter_df = one_time_reporter_df.reset_index()
        one_time_reporter_df = one_time_reporter_df[self.columns]

        c = CustomDepartmentReporter()
        production_df = one_time_reporter_df.apply(lambda x: c.get_custom_report(x), axis=1)
        # # custom_reporter_df = custom_reporter_df[c.columns[1:]]
        # custom_reporter_df = custom_reporter_df.reset_index()

        print('writing single time production count to file...')
        production_df.to_excel(self.writer, sheet_name=self.sheet_name, index=False)


class CustomDepartmentReporter:
    def __init__(self):
        self.columns = ['OCINumber',
                        'UC A2', 'UC A14', 'UC A15',
                        'UC_TINT A2', 'UC_TINT A14', 'UC_TINT A15',
                        'UC_FITT A2', 'UC_FITT A14', 'UC_FITT A15',
                        'Stock_FITT A2', 'Stock_FITT A14', 'Stock_FITT A15',
                        'Stock_TC A2', 'Stock_TC A14', 'Stock_TC A15',
                        'Stock_TMC A2', 'Stock_TMC A14', 'Stock_TMC A15',
                        'Stock_TINT A2', 'Stock_TINT A14', 'Stock_TINT A15',
                        'TINT_TC A2', 'TINT_TC A14', 'TINT_TC A15',
                        'TINT_TMC A2', 'TINT_TMC A14', 'TINT_TMC A15',
                        'TINT_FITT A2', 'TINT_FITT A14', 'TINT_FITT A15',
                        'SUR_A14_A15 To TC_A2', 'SUR_A2_A15 To TC_A14', 'SUR_A2_A14 To TC_A15']

    @staticmethod
    def get_custom_report(row):
        departments = ['TS', 'DS', 'TC', 'TMC', 'TINT', 'FITT']
        labs = ['A2', 'A14', 'A15']
        for dept in departments:
            total = 0
            for lab in labs:
                total += row[dept + ' ' + lab]
            row[dept] = total

        # uncoat order
        for lab in labs:
            row['UC' + ' ' + lab] = 0
            if (row['TS' + ' ' + lab] > 0 or row['DS' + ' ' + lab] > 0) and (row['TC'] == 0) and (row['TMC'] == 0) and (
                    row['TINT'] == 0):
                row['UC' + ' ' + lab] = row['TS' + ' ' + lab] + row['DS' + ' ' + lab]
        row['UC'] = row['UC A2'] + row['UC A14'] + row['UC A15']

        # uncoat tint order
        for lab in labs:
            row['UC_TINT' + ' ' + lab] = 0
            if (row['TS'] > 0 or row['DS'] > 0) and (row['TC'] == 0) and (row['TMC'] == 0) and (
                    row['TINT' + ' ' + lab] > 0):
                row['UC_TINT' + ' ' + lab] = row['TINT' + ' ' + lab]
        row['UC_TINT'] = row['UC_TINT A2'] + row['UC_TINT A14'] + row['UC_TINT A15']

        # uncoat fitting order
        for lab in labs:
            row['UC_FITT' + ' ' + lab] = 0
            if (row['TS'] > 0 or row['DS'] > 0) and (row['TC'] == 0) and (row['TMC'] == 0) and (
                    row['FITT' + ' ' + lab] > 0):
                row['UC_FITT' + ' ' + lab] = row['FITT' + ' ' + lab]
        row['UC_FITT'] = row['UC_FITT A2'] + row['UC_FITT A14'] + row['UC_FITT A15']

        # stock fitting order
        for lab in labs:
            row['Stock_FITT' + ' ' + lab] = 0
            if (row['TS'] == 0) and (row['DS'] == 0) and (row['FITT' + ' ' + lab] > 0):
                row['Stock_FITT' + ' ' + lab] = row['FITT' + ' ' + lab]
        row['Stock_FITT'] = row['Stock_FITT A2'] + row['Stock_FITT A14'] + row['Stock_FITT A15']

        # stock tc order
        for lab in labs:
            row['Stock_TC' + ' ' + lab] = 0
            if (row['TS'] == 0) and (row['DS'] == 0) and (row['TC' + ' ' + lab] > 0):
                row['Stock_TC' + ' ' + lab] = row['TC' + ' ' + lab]
        row['Stock_TC'] = row['Stock_TC A2'] + row['Stock_TC A14'] + row['Stock_TC A15']

        # stock tmc order
        for lab in labs:
            row['Stock_TMC' + ' ' + lab] = 0
            if (row['TS'] == 0) and (row['DS'] == 0) and (row['TMC' + ' ' + lab] > 0):
                row['Stock_TMC' + ' ' + lab] = row['TMC' + ' ' + lab]
        row['Stock_TMC'] = row['Stock_TMC A2'] + row['Stock_TMC A14'] + row['Stock_TMC A15']

        # stock tint order
        for lab in labs:
            row['Stock_TINT' + ' ' + lab] = 0
            if (row['TS'] == 0) and (row['DS'] == 0) and (row['TC'] == 0) and (row['TMC'] == 0) and (
                    row['TINT' + ' ' + lab] > 0):
                row['Stock_TINT' + ' ' + lab] = row['TINT' + ' ' + lab]
        row['Stock_TINT'] = row['Stock_TINT A2'] + row['Stock_TINT A14'] + row['Stock_TINT A15']

        # tint tc order
        for lab in labs:
            row['TINT_TC' + ' ' + lab] = 0
            if (row['TINT'] > 0) and (row['TC' + ' ' + lab] > 0):
                row['TINT_TC' + ' ' + lab] = row['TC' + ' ' + lab]
        row['TINT_TC'] = row['TINT_TC A2'] + row['TINT_TC A14'] + row['TINT_TC A15']

        # tint tmc order
        for lab in labs:
            row['TINT_TMC' + ' ' + lab] = 0
            if (row['TINT'] > 0) and (row['TMC' + ' ' + lab] > 0):
                row['TINT_TMC' + ' ' + lab] = row['TMC' + ' ' + lab]
        row['TINT_TMC'] = row['TINT_TMC A2'] + row['TINT_TMC A14'] + row['TINT_TMC A15']

        # tint fitting order
        for lab in labs:
            row['TINT_FITT' + ' ' + lab] = 0
            if (row['TINT'] > 0) and (row['FITT' + ' ' + lab] > 0):
                row['TINT_FITT' + ' ' + lab] = row['FITT' + ' ' + lab]
        row['TINT_FITT'] = row['TINT_FITT A2'] + row['TINT_FITT A14'] + row['TINT_FITT A15']

        # 'SUR_A14_A15 To TC_A2'
        row['SUR_A14_A15 To TC_A2'] = 0
        if (row['TC A2'] > 0) and (row['TS A2'] + row['DS A2'] == 0) and (
                (row['TS A14'] + row['DS A14'] + row['TS A15'] + row['DS A15'] > 0)):
            row['SUR_A14_A15 To TC_A2'] = row['TC A2']

        # 'SUR_A2_A15 To TC_A14'
        row['SUR_A2_A15 To TC_A14'] = 0
        if (row['TC A14'] > 0) and (row['TS A14'] + row['DS A14'] == 0) and (
                (row['TS A2'] + row['DS A2'] + row['TS A15'] + row['DS A15'] > 0)):
            row['SUR_A14_A15 To TC_A14'] = row['TC A14']

        # 'SUR_A2_A14 To TC_A15'
        row['SUR_A2_A14 To TC_A15'] = 0
        if (row['TC A15'] > 0) and (row['TS A15'] + row['DS A15'] == 0) and (
                (row['TS A14'] + row['DS A14'] + row['TS A2'] + row['DS A2'] > 0)):
            row['SUR_A2_A14 To TC_A15'] = row['TC A15']

        return row
