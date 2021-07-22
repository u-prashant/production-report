class DepartmentFinder:
    def __init__(self, df):
        self.departments_map = self.get_map(df)

    @staticmethod
    def get_map(df):
        return dict(zip(df['OrderStatus'], df['Department']))

    def get_department(self, value):
        if value in self.departments_map:
            return self.departments_map[value]

        value = value.upper()
        dept = ''

        if 'TS' in value:
            dept = 'TS'
        elif 'TC' in value:
            dept = 'TC'
        elif 'DS' in value:
            dept = 'DS'
        elif 'TMC' in value:
            dept = 'TMC'
        elif 'TINT' in value:
            dept = 'TINT'
        elif 'QC' in value and 'COATING' in value:
            dept = 'FINAL QC'
        elif 'FITT' in value:
            dept = 'FITT'

        if dept == '':
            print('Department Not Found for OrderStatus {}'.format(value))
        return dept
