import json

class Project:
    """Projects define the organization of a hygnd data store
    """

    def __init__(self, template):
        """
        Parameters
        ----------
        template : string or dict
        """

        if isinstance(template, dict):
            self.__dict__ = template

        elif isinstance(template, str):
            self.load(template)

        else:
            raise TypeError('Project must be initiated with either a dict or filename')

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.__dict__, f)

    def load(self, filename):
        import pdb; pdb.set_trace()
        with open(filename, 'r') as f:
            self.__dict__ = json.load(f)

    def stations(self, proxies=False):
        """List stations in project

        Parameters
        ----------
        proxies : boolean
            If true, includes proxy stations
        """

        if proxies and hasattr(self, 'proxy_sites'):
            return self.sites + self.proxy_sites

        else:
            return self.sites

    def station_services(self):
        if hasattr(self, 'services'):
            return self.services
