"""
Library for pulling data from the Water Quality Portal

https://www.waterqualitydata.us/webservices_documentation/

The WQP web services may be queried using a RESTlike (REpresentational State Transfer) technique. This method will retrieve the same data as the WQP form when the same retrieval parameters are specified. The basic building blocks for querying the services are outlined in the following series of tables. Most non-alphanumeric characters (such as punctuation) must be "url-encoded", (for example: space is "%20").

Parameters must be appended to the base Uniform Resource Locator (URL) for the RESTlike WQP web services. The base URL is constructed differently depending on the type of information being requested. There are two options - one base URL for downloading sites and one base URL for downloading results:

Base URL for downloading sites -- https://www.waterqualitydata.us/Station/search?
Base URL for downloading results -- https://www.waterqualitydata.us/Result/search?
Base URL for downloading activity data – https://www.waterqualitydata.us/Activity/search?
Base URL for downloading activitymetric data – https://www.waterqualitydata.us/ActivityMetric/search?
Construct a RESTlike web service query by concatenating the base URL with the desired parameters and arguments (Table 1).  At least one parameter-argument pair must be specified. Separate multiple parameter-argument pairs with an ampersand ("&"). Unneeded web service parameters may be omitted. If no mime type is specified, the retrieval will default to WQX-XML format. Station and Result retrieval data elements are output in a consistent format and nomenclature. See the User Guide for a list of elements included in the station and result retrievals.
"""

import pandas as pd
import requests

class WQPClient():
    
    def get_data(siteid,start,end, params=[]):
        """
        Args:
          site (string): X digit USGS site ID. USGS-05586300
          start: 2018-01-25
          end:
          params: One or more five-digit USGS parameter codes
        """
        url = 'https://www.waterqualitydata.us/Station/search?'
        
        payload = {'sites':siteid, 'startDateLo':start, 'startDateHi':end, 
               'mimeType':'csv', 'pCode':'params'} 
        pass
    
    def make_HDF():
        pass
    
    def append_HDF():
        pass
    
    def update_HDF():
        pass
        