#define dictionary of NWIS parameter codes

pn = {
    'site_no' : 'Site',
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

pc = {
    
    
}


class LayeredSurrogateRatingModel:
    
    def __init__(self, constituent_data, surrogate_data, **kwargs):
        """
        same as SurrogateRatingModel except surrogate data is list of lists
        """
        
        pass
    

class SaidSurrogateModel:
    