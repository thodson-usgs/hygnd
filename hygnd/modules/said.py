from hygnd.store import HGStore
from hygnd.store import Station

class SAIDStore(HGStore):

class SAIDStation():
    pass


class SAIDStore(HGStore):
    def _prep_site(self, site, verbose=True):
        """Prepare and store dataframes for input to SAID
        """
        if verbose:
            print(site)

        dv =
        dv = self.get(key='site/{}/dv'.format(site))
        iv = self.get(key='site/{}/iv'.format(site))

        qw_key = '/site/{}/qwdata'.format(site)

        if qw_key in self.keys():
            qwdata = self.get(key=qw_key)
            qwdata = format_constituent_df(qwdata)
            self.put('site/{}/said/qwdata'.format(site), qwdata)
        #TODO remove samples too close in time

        #clean iv
        #XXX review this
        iv = iv.replace('P,e','A').replace('P:e','A')

        iv = filter_param_cd(iv, 'A')#.replace(-999999, np.NaN)
        dv = filter_param_cd(dv, 'A')#.replace(-999999, np.NaN)
        iv = interp_to_freq(iv, freq=15, interp_limit=120)

        if '00060' in iv.columns:
            iv = fill_iv_w_dv(iv, dv, freq='15min', col='00060')

        if '51289' in iv.columns:
            iv['51289'] = interp_to_freq(iv['51289'], freq=15,
                                        interp_limit=480)

        iv = format_surrogate_df(iv)

        #drop rows with only discharge
        #check_cols = iv.columns.drop('Discharge')
        #iv.dropna(how='all', subset=check_cols)
        #for i in [iv, qwdata]:
            # I *believe* SAID only works on single layer index, 
            # so strip site_no from index
         #   i.reset_index(level=0, inplace=True)

        self.put('site/{}/said/iv'.format(site), iv)

    def _apply_proxy(self, dst_id, src_id, field):
        field = pn[field] #translate to SAID XXX
        dst_df = self.get(key='site/{}/said/iv'.format(dst_id))
        src_df = self.get(key='site/{}/said/iv'.format(src_id))

        dst_df[field] = np.NaN
        dst_df.update(src_df[[field]])

        self.put('site/{}/said/iv'.format(dst_id), dst_df)

    def _prep_sites(self,sites):
        """
        Args:
            sites (list): list of dicts, each containing an id field
        """
        for site in sites:
            self._prep_site(site['id'])

        for site in sites:
            proxies = site.get('proxies')
            if proxies:
                for proxy in proxies:
                    dst_id = site['id']
                    src_id = proxies[proxy] #confusing, returns site name
                    self._apply_proxy(dst_id, src_id, proxy)



