Updating documentation
######################

Build the website locally
=========================

Prerequisites
    * Python 3.9+

#. Clone the repository
    Begin by cloning the EAK-Copilot repository to your local machine to get the necessary project files.

    .. code-block:: console

        git clone https://github.com/CdC-SI/eak-copilot.git
        cd eak-copilot
        cd doc

#. Install dependencies
    The ``requirement.txt`` contains Sphinx and several Sphinx extension packages that we use within the project.

    .. code-block:: console

        pip install -r requirements.txt

#. Run the build
    .. code-block:: console

        sphinx-build -M html doc _build

An ``index.html`` document can now be found in the ``_build/html/`` directory. You can open it with your favorite browser and start exploring!


Documentation folder structure
==============================

Files related to the documentation can be found inside the ``doc/`` directory.

Currently, our repository is structured as follows.

| eak-copilot
| ├── doc
| │   ├── _static
| │   │   ├ css
| │   │   └ img
| │   ├── guidelines
| │   │   └ ...
| │   ├── intro
| │   │   └ ...
| │   ├── topics
| │   │   └ ...
| │   ├── conf.py
| │   ├── index.py
| │   └── requirements.txt
| └── ...
|
|

.. todo::

    * Introduction to reStructuredText (.rst) format
    * Documentation folder structure (in progress)