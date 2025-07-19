# buses_data.py

BUS_LIST = [
    # (bus_number,      name,             description,          location, nominal_voltage, nominal_current, extra_parameters)
    (1,  'Main Bus',       'Main feeder',      'Lab 1', 220.0, 100.0, {"manufacturer": "Siemens"}),
    (2,  'Secondary Bus',  'Backup line',      'Lab 1', 220.0, 80.0,  {"manufacturer": "Siemens"}),
    (3,  'Load Bus',       'Load section',     'Lab 1', 220.0, 50.0,  {"manufacturer": "ABB"}),
    (4,  'Generation Bus', 'Solar plant',      'Lab 2', 380.0, 60.0,  {"manufacturer": "ABB"}),
    (5,  'Battery Bus',    'Battery section',  'Lab 2', 220.0, 40.0,  {"manufacturer": "LG"}),
    (6,  'Aux Bus',        'Auxiliary circuit','Lab 2', 220.0, 10.0,  {"manufacturer": "LG"}),
    (7,  'Spare Bus 1',    'Spare',            'Lab 3', 220.0, 15.0,  {}),
    (8,  'Spare Bus 2',    'Spare',            'Lab 3', 220.0, 15.0,  {}),
    (9,  'Spare Bus 3',    'Spare',            'Lab 3', 220.0, 15.0,  {}),
    (10, 'Test Bus 1',     'For testing',      'Lab 1', 220.0, 30.0,  {}),
    (11, 'Test Bus 2',     'For testing',      'Lab 1', 220.0, 30.0,  {}),
    (12, 'Test Bus 3',     'For testing',      'Lab 1', 220.0, 30.0,  {}),
    (13, 'External Bus',   'External source',  'Yard',  380.0, 100.0, {})
]
