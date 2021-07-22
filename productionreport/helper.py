def get_lab(value):
    lab = 'A15'
    if 'A2' in value:
        lab = 'A2'
    elif 'A14' in value:
        lab = 'A14'
    return lab
