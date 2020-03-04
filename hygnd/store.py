import pandas as pd
from hygnd.project import Project

from dataretrieval import nwis
import numpy as np

class Collection():
    """Class that contains a collection of documents or dataframes
    """
    def __init__(self, site_id, store_path, root):
        self._id = site_id
        self._store_path = store_path
        self._root = root


    def _root_dir(self):
        return '/{}/{}/'.format(self._root, self._id)


    def _group(self, service):
        return '{}{}'.format(self._root_dir(), service)


    def id(self):
        return self._id


    def get(self, service):
        """Get service belonging to station from local data store.
        """

        group = self._group(service)

        with HGStore(self._store_path) as store:

            try:
                df = store.get(group)

            except KeyError:
                return None

        return df


    def put(self, service, df):
        """Put service belonging to station into local data store.

        """
        if df is None:
            return

        group = self._group(service)

        with HGStore(self._store_path) as store:
            store.put(group, df, format='fixed')

    def remove(self, service):
        """Remove table from store
        """
        group = self._group(service)

        with HGStore(self._store_path) as store:
            store.remove(group)


class Station(Collection):
    """Class representing a station, which could be a stream gage
    or any other point-source data.
    """
    def __init__(self, site_id, store_path):
        self._root = 'site'
        super().__init__(site_id, store_path, self._root)
        self._approved_services = ['dv','iv','qwdata','site']

    def services(self):
        """List services in local data store

        Returns
        -------
            List of services (iv, dv, etc) that are contained in the local
            data store.
        """

        with NWISStore(self._store_path) as store:
            keys = store.keys()
            root = self._root_dir()

            services = [s.replace(root,'') for s in keys if root in s]

            return services


    def update(self, service=None, approved=False):
        """Update a service

        Parameters
        ----------
        service : string
            Name of service to upgrade. If none, upgrade all existing services.

        approved : boolean


        TODO: set default approval to True once implemented
        """

        if not service:
            for service in self.services():
                self.update(service=service, approved=approved)

        elif service not in self._approved_services:
            raise TypeError("Unrecognized service")

        elif service == 'site':
            #site has only one record, so simply update the entire table
            updated = nwis.get_record(self.id(), service=service)
            self.put(service, updated)

        else:

            site = self.id()
            old_df = self.get(service)

            if approved:
                last_time = old_df.iloc[0].name.strftime('%Y-%m-%d')

            if not approved:
                last_time = old_df.iloc[-1].name.strftime('%Y-%m-%d')


            new_df = nwis.get_record(site, start=last_time, end=None, service=service)

            if new_df is not None:
                overlap = new_df.index.intersection(old_df.index)
                old_df.drop(overlap, axis=0)

                updated = old_df.append(new_df)
                self.put(service, updated)


    def download(self, service, start=None, end=None):
        """Download

        Parameters
        ----------
        service : string
        start : string
        end : string
        """
        group = self._group(service)
        df = nwis.get_record(self.id(), start=start, end=end, service=service)

        self.put(service, df)


    def iv(self):
        return self.get('iv')


    def qwdata(self):
        return self.get('qwdata')


    def dv(self):
        return self.get('dv')


    def sur(self):
        return self.get('sur')

class HGStore(pd.HDFStore):
    """
    """
    def stations(self):
        """Returns a list of stations within store
        """
        stations = []
        keys = self.keys()

        paths = [s for s in keys if "site" in s]

        stations = [ s.split('/')[2] for s in paths]

        return list(set(stations))

    def get_object(self, object_id, root):
        return Collection(object_id, self._path, root)



class NWISStore(HGStore):
    """class works on pytables hdf

    """
    #open
    #init pass filename
    #set for HDFStore(file, complevel=9, complib='blosc:blosclz)'
    #alternatively better compression may be achieved with ptrepack
    #wrapper 

    #add more services
    #should go in a hygndstore XXX testing

    def get_station(self, station_id):
        return Station(station_id, self._path)


    def spinup(self, project_template, verbose=False):
        """Download data for all stations specified in project

        Parameters
        ----------
        project_template : dict
            dictionary specifying the organization of stations within the project

        TODO: add check to make sure hdf does not already exist
        """
        p = Project(project_template)

        services = p.station_services()

        for site in p.stations(proxies=True):

            if verbose:
                print(site)

            station = self.get_station(site['id'])
            start = site.get('start')
            end = site.get('end')

            for service in p.services:
                station.download(service, start=start, end=end)


    def update(self, station_id=None, service=None):
        """Update station object in datastore.

        TODO: add approval parameter
        """

        if all([station_id, service]):
            station = self.get_station(station_id)
            station.update(service)

        elif station_id:
            station = self.get_station(station_id)
            station.update()

        else:
            station_ids = self.stations()
            for station_id in station_ids:
                station = self.get_station(station_id)
                station.update()
