"""
TODO: move these to better locations
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

said_files = {
    'Surrogate': { 
        '00065' : 'Gage Height',
        '00060' : 'Discharge',
        '00095' : 'Spec Cond',
        '63680' : 'Turb',
        '99133' : 'NitrateSurr'
    },

    'OrthoP' : {
        '51289' : 'OrthoP',
    },
    
    'DailyQ' : {
        '00060' : 'Discharge',
    }
}

nwis_to_said = {
    'datetime':'DateTime',
    '00065':'Gage Height',
    '00095':'Spec Cond',
    '63680(YSI)' : 'Turb_YSI',
    '63680(HACH)': 'Turb_HACH',
    '99133': 'NitrateSurr',
    '51289': 'OrthoP',
    '00060': 'Discharge',
    'p80154': 'SSC',
    'p00665': 'TP',
    'p00631': 'Nitrate',
    'p70331': '<62'
}