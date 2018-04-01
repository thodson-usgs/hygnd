"""
Predefined site
"""

code_lookup = {
    'discharge':'00060',
    'temperature':'00010',
    'nitrate':'99133',
    'turbidity':'63680'
}

site_dict = {'florence':'05586300',
             'spoon':'03336890'}

param_lookup = {
    '99133'
} 

super_gauges = [
    '03336890', #Spoon River, St. Joseph
    '03339000', #Vermillion River, Danville   
    '03346500', #Embarras River, Lawrenceville
    '03381495', #Little Wabash River, Carmi
    '05446500', #Rock River, Joslin
    '05447500', #Green River, Geneseo
    '05554300', #Indian Creek, Fairbury
    '05576100', #Lick Creek, Woodside
    '05576195', #Sugar Creek, Chatham
    '05586300', #Illinois River, Florence
    '05595000', #Kaskaskia River, New Athens
    '05599490', #Murphysboro
]

super_gauge_pms = [
    '00010', # temperature
    '00060', #discharge
    '00065', #gage height
    '00095', #specific conductance
    '00300', #dissolved oxygen mg/L
    '00301', #DO %
    '00400', #pH
    '32295', #fDOM
    '32318', #chl
    '32319', #BG's
    '51289', #orthoP
    '63680', #turbidity
    '91049', #nitrate load
    '99133'  #nitrate concentration
]

#nicknames from Andrew's said script
said_sites = {
    #'03336890':'Spoon', 
    '03339000':['Vermillion', '2015-02-24'],
    '03346500':['Embarras', '2015-11-01' ],
    '03381495':['LittleWabash', '2015-11-01'], 
    '05446500':['Rock', '2015-08-20'],
    '05447500':['Green', '2015-08-19'],
    #'05554300', #Indian Creek, Fairbury
    #'05576100': 'Lick',
    #'05576195', #Sugar Creek, Chatham
    '05586300':['Illinois', '2012-06-02'],
    '05595000':['Kaskaskia', '2015-09-17'],
    '05599490':['BigMuddy', '2015-10-01'],#Murphysboro
}

super_network = {
    'sites': [
        {'id':'03339000', 'name':'Vermillion', 'start':'2015-02-24'},
        {'id':'03346500', 'name':'Embarras',   'start':'2015-11-01'},
        {'id':'03381495', 'name':'LittleWabash','start':'2015-11-01',
        'proxies':{'00060':'03381500'}}, 
        {'id': '03381500', 'name':'LittleWabashQ', 'start':'2015-11-01'},
        {'id':'05446500', 'name':'Rock', 'start':'2015-08-20'}, 
        {'id':'05447500', 'name':'Green', 'start':'2015-08-19'}, 
        {'id':'05586300', 'name':'Illinois', 'start':'2012-06-02',
        'proxies':{'00060':'05586100'}},
        {'id':'05586100', 'name':'IllinoisQ', 'start':'2012-06-02'},
        {'id':'05595000', 'name':'Kaskaskia', 'start':'2015-09-17'},
        {'id':'05599490', 'name':'BigMuddy', 'start':'2015-10-01'},#Murphysboro
    ],
    'proxies' : [
        {'id':'XXXX'}
    ]
    
}

# need to merge with previous, this one has proxy sites removed
super_network2 = {
    'sites': [
        {'id':'03339000', 'name':'Vermillion', 'start':'2015-02-24'},
        {'id':'03346500', 'name':'Embarras',   'start':'2015-11-01'},
        {'id':'03381495', 'name':'LittleWabash','start':'2015-11-01',
        'proxies':{'00060':'03381500'}}, 
        {'id':'05446500', 'name':'Rock', 'start':'2015-08-20'}, 
        {'id':'05447500', 'name':'Green', 'start':'2015-08-19'}, 
        {'id':'05586300', 'name':'Illinois', 'start':'2012-06-02',
        'proxies':{'00060':'05586100'}},
        {'id':'05595000', 'name':'Kaskaskia', 'start':'2015-09-17'},
        {'id':'05599490', 'name':'BigMuddy', 'start':'2015-10-01'},#Murphysboro
    ],
    'proxies' : [
        {'id':'XXXX'}
    ]
    
}

said_files = {
    'Surrogate': { 
        #'00065' : 'Gage Height',
        '00060' : 'Discharge',
        '00095' : 'Spec Cond',
        '63680' : 'Turb',
        '99133' : 'NitrateSurr',
        '51289' : 'OrthoP'
    },

    'DailyQ' : {
        '00060' : 'Discharge',
    }
}

nwis_to_said = {
    'site_no' : 'Site',
    'datetime':'DateTime',
    '00065':'Gage Height',
    '00095':'Spec Cond',
    '63680_ysi' : 'Turb_YSI',
    '63680_hach': 'Turb_HACH',
    '99133': 'NitrateSurr',
    '51289': 'OrthoP',
    '00060': 'Discharge',
    'p80154': 'SSC',
    'p00665': 'TP',
    'p00631': 'Nitrate',
    'p70331': '<62'
}

# dictionary of parameter names same as nwis_to_said
pn = {
    'site_no' : 'Site',
    'datetime':'DateTime',
    '00065':'Gage Height',
    '00095':'Spec Cond',
    '63680_ysi' : 'Turb_YSI',
    '63680_hach': 'Turb_HACH',
    '99133': 'NitrateSurr',
    '51289': 'OrthoP',
    '00060': 'Discharge',
    'p80154': 'SSC',
    'p00665': 'TP',
    'p00631': 'Nitrate',
    'p70331': '<62'
}

pc = {
    'SSC':'p80154',
    'Turb_YSI':'63680_ysi',
    
}