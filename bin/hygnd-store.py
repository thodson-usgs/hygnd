#!/usr/bin/env python3
"""
author: Tim Hodson

Command line script for updating NWIS datastore

TODO: make this bad boy threaded.
"""
import argparse, sys, os, glob
from hygnd.store import NWISStore

def main():
    # parse input parameters    
    parser = argparse.ArgumentParser(description= "Manage NWIS data store.")

    parser.add_argument('filename', type=string,
                        dest='filename',
                        help='Path to hdf store.')

    # if init chosen, feed a dict
    parser.add_argument('--init', action='store_true',
                        default=False,
                        dest='init',
                        help='initialize a new datastore')

    parser.add_argument('--update', action='store_true',
                        default=False,
                        dest='update',
                        help='update an existing datastore')


    # if no arguments provided, print usage and exit
    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(1)

    else:
        args = parser.parse_args()
        filename = args.filename
        init = args.init
        update = args.update

    store = NWISStore(filename)

    if init:
        #load in template dict as sites
        sites = project_template['sites']
        store._spinup_sites(sites)

    if update:
        pass


    store.close()


if __name__ == "__main__":
    main()
