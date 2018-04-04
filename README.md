# hygnd: hydrologic gauge network data analysis toolkit
-------

hygnd (pronounced 'high ground') is a Python package providing tools for analyzing and manipulating data from the USGS hydrographic gage network.
It serves as a bridge between online data repo

At its core, hygnd is a data management system for surface-water data. It serves as a bridge between web data portals, which house hydrographic data, and common models and python libraries used for analysis and visualization of hydrographic data.
As pulling data directly from the web can be time consuming, especially with large national datasets, hygnd provides tools for downloading data to a local HDF data store. There data can be rapidly accessed to provide input for numerical models and visualizations, along with any intermediate data products that are needed for later analysis. Concievably, hygnd could eventually support high-traffic web-based tools, but it would require a heavier-weight multi-user database for the back end.

hygnd is still in early development and not ready for public consumption. However, feel free to raise an issue if you have a particular use case that
In addition, I've found the components for retrieving data from the web to be extremely useful in my own workflow. In an effort to make those available as quickly as possible, I've moved those elements to their own project, called data-retrieval, which is a python alternative to the popular R dataRetrieval library that I hope will grow as the next generation of python-trained programmers join the ranks of the USGS.

