from hygnd.store import NWISStore
from hygnd.munge import filter_param_cd
from data_retrieval import nwis


#should store this in data_retrievel
APPROVED_SERVICE = ['dv','iv']

class Station():
    """Class representing a station, which could be a stream gage
    or any other point-source data.

    """
    def __init__(self, site_id, store_path):
        self.site_id = site_id
        self.store_path = store_path

    def _root_dir(self):
        return '/site/{}/'.format(self.site_id)

    def _group(self, service):
        return '/site/{}/{}'.format(self.site_id, service)

    def id(self):
        return self.site_id

    def services(self):
        """List services in local data store

        Returns
        -------
            List of services (iv, dv, etc) that are contained in the local
            data store.
        """

        with NWISStore(self.store_path) as store:
            keys = store.keys()
            root = self._root_dir()

            services = [s.replace(root,'') for s in keys if root in s]

            return services


    def get(self, service):
        """Get service belonging to station from local data store.
        """

        group = self._group(service)

        with NWISStore(self.store_path) as store:

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

        with NWISStore(self.store_path) as store:
            store.put(group, df, format='fixed')


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

        elif service not in APPROVED_SERVICE:
            raise TypeError("Unrecognized service")

        site = self.id()
        old_df = self.get(service)

        if approved:
            last_time = old_df.iloc[0].name.strftime('%Y-%m-%d')

        if not approved:
            last_time = old_df.iloc[-1].name.strftime('%Y-%m-%d')


        new_df = nwis.get_record(site, start=last_time, end=None)
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
        df = nwis.get_record(self.site_id, start=start, end=end, service=service)


        self.put(service, df)


    def iv(self):
        return self.get('iv')


    def qwdata(self):
        return self.get('qwdata')


    def dv(self):
        return self.get('dv')


    def sur(self):
        return self.get('sur')
