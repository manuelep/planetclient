# Welcome to Planetclient

Planetclient is a sub-module developed as a component of a generic
[scaffolding](https://github.com/web2py/py4web/tree/master/apps/_scaffold)
[py4web](http://py4web.com/) application and it's part of the
[Planet Suite](https://manuelep.github.io/planet-suite/).

> **Note**
> Please refer to the
> [py4web official documentation](http://py4web.com/_documentation/static/index.html#chapter-01)
> for framework installation, setup and basics concepts about implementing applications
> and about what the *apps* folder is.

# Description

This module implements the database model for the views (*named queries*) defined
in the Planestore module using the PyDAL database abstraction layer for easy IO
web REST API services implementation.

This module implements tools for easy serve and manage vector data using useful
standard geometric structures such as the
[classic squares tiles](https://wiki.openstreetmap.org/wiki/Tiles) and
the [Uber hexagonal tiles](https://eng.uber.com/h3/) in the python environment
of the application.

# How to's

## Include Planetclient in your custom application

Py4web applications are nothing more than native [python modules](https://docs.python.org/3/tutorial/modules.html)
and the Planetclient code is structured in the same way so can be used actually as
a *submodule* that can be nested in custom applications.

You can link the module to your code repository using [Git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)
but the minimal requirement is to copy/clone the [Planetclient repository](https://github.com/manuelep/planetclient)
nested in your `root` project folder.

### Requirements

* [Planetstore](https://github.com/manuelep/planetstore)

Please refer to the `requirements.txt` file for an updated list of required python
modules and install them using:

```sh
pip install -r [path/to/apps/<your app>/planetclient/]requirements.txt
```

# Doc

Please refer to the [repository wiki](https://github.com/manuelep/planetclient/wiki)
for the module detailed documentation.
