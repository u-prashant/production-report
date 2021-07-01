def get_lab(value):
    lab = 'A15'
    if 'A2' in value:
        lab = 'A2'
    elif 'A14' in value:
        lab = 'A14'
    return lab


def get_department(value):
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
    elif 'FINAL' in value:
        dept = 'FINAL QC'
    elif 'FITT' in value:
        dept = 'FITT'
    return dept
