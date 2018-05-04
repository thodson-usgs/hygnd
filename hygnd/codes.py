"""
define NWIS codes
https://waterdata.usgs.gov/nwis?codes_help
"""
NWIS_codes = [
    'A',   # Approved
    'Ssn', # Parameter monitored seasonally
    'Bkw', # Flow affected by backwater
    'Ice', # Ice affected
    'Pr',  # Partial-record site
    'Rat', # Rating being developed or revised
    'Eqp', # Equipment malfunction
    'Fld', # Flood damage
    'Dry', # Dry
    'Dis', # Data-collection discontinued
    '--',  # Parameter not determined
    'Mnt', # Maintenance in progress
    'Zfl', # Zero flow
    '***'  # Temporarily unavailable
]

flag = {code:i**2 for i,code in enumerate(NWIS_codes)}


