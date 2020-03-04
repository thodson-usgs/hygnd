# hygnd: Hydrologic Gage-Network Data manager
--------------------------------------------

hygnd ('high ground') is a Python package for managing data from the USGS hydrographic gage network.

At its core, hygnd is a data management system for surface-water data that serves as the bridge between web data portals, which house hydrographic data, and common models and python libraries used to analyze and visualize that data.
As pulling large datasets directly from the web can be time consuming, hygnd provides tools for downloading and maintaining local copies of online databases, so that the data can be rapidly accessed to provide input for analysis and visualization. 
Currently, hygnd uses HDF to store data; however, the limitations of that choice were quickly apparent so future versions will also support  mySQL and POSTGRES. The latter has multi-user support and would allow hygnd work as a backend for web-based applications.

hygnd is still in early development and not ready for public consumption. However, feel free to contact me if you, like me, want faster access to environmental data and you're interested in sharing your time, ideas, or funding to help develop this tool.

In addition, I've found the components for retrieving data from the web to be extremely useful in my own workflow. In an effort to make those components available as quickly as possible, I've moved them to their own project, called dataretrieval, which is a python alternative to the popular R dataRetrieval library.
