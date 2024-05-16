Updating documentation
######################

Local build
===========

Prerequisites
    * Python 3.9+

#. Clone the repository
    Begin by cloning the EAK-Copilot repository to your local machine to get the necessary project files.

    .. code-block:: console

        git clone https://github.com/CdC-SI/eak-copilot.git
        cd eak-copilot

#. Install dependencies
    The ``requirement.txt`` contains Sphinx and several Sphinx extension packages that we use within the project.

    .. code-block:: console

        pip install -r doc/requirements.txt
        pip install -r autocomplete/requirements.txt
        pip install -r indexing/requirements.txt
        pip install -r rag/requirements.txt

#. Run the build
    .. code-block:: console

        sphinx-build -M html doc _build

An ``index.html`` document can now be found in the ``_build/html/`` directory. You can open it with your favorite browser and start exploring!


Documentation structure
=======================

Files related to the documentation can be found inside the ``doc/`` directory.

Currently, our /doc folder is structured as follows.

.. code::

    doc
    ├── _static
    │   ├ css
    │   └ img
    ├── guidelines
    │   ├ sphinx.rst <--- you are here
    │   └ ...
    ├── intro
    │   └ ...
    ├── topics
    │   └ ...
    ├── conf.py
    ├── index.rst
    └── ...

| **conf.py** is the Sphinx configuration files.
| **_static/** contains custom static files, such as stylesheets or images.

All the remaining folders contains ``.rst`` or ``.md`` files only, each file represents a webpage.

| **index.rst** is the website homepage.
| **intro/** contains pages that introduce the Copilot project.
| **guidelines/** contains tutorials and best practices guidelines.
| **topics/** contains Copilot open sourced code documentation.

Especially, **index.rst** contains several "Toc trees" which define the architecture of the website and build the sidebar on the left.
Each ``toctree`` defines a theme. Currently, the website is split into 3 of theme: Introduction (intro), Guidelines, and Documentation (topics).

.. todo::

    * Introduction to reStructuredText (.rst) format
    * Documentation folder structure (in progress)