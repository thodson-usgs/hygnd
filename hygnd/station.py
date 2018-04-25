from hygnd.store import NWISStore
from data_retrieval import nwis


#should store this in data_retrievel
APPROVED_SERVICE = ['dv','iv']

class Station():
    """

    TODO: add a function for handling 'all'
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

        with NWISStore(self.store_path) as store:
            keys = store.keys()
            root = self._root_dir()

            services = [s.replace(root,'') for s in keys if root in s]

            return services


    def get(self, service):

        group = self._group(service)

        with NWISStore(self.store_path) as store:

            try:
                df = store.get(group)

            except KeyError:
                return None

        return df


    def put(self, service, df):
        group = self._group(service)

        with NWISStore(self.store_path) as store:
            store.put(group, df, format='fixed')


    def update(self, service=None, approved=False):
        """Update a service

        Parameters
        ----------

        TODO: set default approval to True once implemented
        """

        if not service:
            for service in self.services():
                self.update(service=service, approved=approved)

            #update all recursively
            pass

        elif service in APPROVED_SERVICE and approved == True:
            self._update_approved(service)

        else:
            self._update_recent(service)


    def _update_recent(self, service):
        """Update any gets add since last update
        """
        site = self.id()
        old_df = self.get(service)

        last_time = old_df.iloc[-1].name.strftime('%Y-%m-%d')

        new_df = nwis.get_record(site, start=last_time, end=None)
        overlap = new_df.index.intersection(old_df.index)
        old_df.drop(overlap, axis=0)

        updated = old_df.append(new_df)

        self.put(service, updated)


    def _update_approved(self, service):
        """Updates any approved data

        Parameters
        ----------
        service : string
        """
        group = self._group(service)

        old_df = self.get(group)

        pass


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
