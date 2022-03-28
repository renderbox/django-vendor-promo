# --------------------------------------------
# Copyright 2021, Grant Viklund
# @Author: Grant Viklund
# @Date:   2021-05-07 15:20:29
# --------------------------------------------

from os import path
from setuptools import setup, find_packages

from vendorpromo.__version__ import VERSION

readme_file = path.join(path.dirname(path.abspath(__file__)), "README.md")

try:
    from m2r import parse_from_file

    long_description = parse_from_file(readme_file)  # Convert the file to RST for PyPI
except ImportError:
    # m2r may not be installed in user environment
    with open(readme_file) as f:
        long_description = f.read()

package_metadata = {
    "name": "django-vendor-promo",
    "version": VERSION,
    "description": "Extension to Django Vendor to add Promo Code capabilities",
    "long_description": long_description,
    "url": "https://github.com/renderbox/django-vendor-promo/",
    "author": "Grant Viklund",
    "author_email": "renderbox@gmail.com",
    "license": "MIT license",
    "classifiers": [
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    "keywords": ["django", "app"],
}

setup(
    **package_metadata,
    packages=find_packages(),
    package_data={"vendorpromo": ["templates/vendorpromo/*.html", "templates/vendorpromo/*/*.html"]},
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[
        "Django>=3.0,<4.1",
        'django-autoslug',
        'django-extensions',
        "django-vendor>=0.2.25",
        "django-site-configs",
        'django-integrations',
        'iso4217',
    ],
    extras_require={
        "dev": [  # Packages needed by developers
            "django-allauth",
            'dj-database-url',
            'psycopg2-binary',
            "django-crispy-forms",
        ],
        "test": [],  # Packages needed to run tests
        "prod": [],  # Packages needed to run in the deployment
        "build": [  # Packages needed to build the package
            "setuptools",
            "wheel",
            "twine",
            "m2r",
        ],
        "docs": [  # Packages needed to generate docs
            "recommonmark",
            "m2r",
            "django_extensions",
            "coverage",
            "Sphinx",
            "rstcheck",
            "sphinx-rtd-theme",  # Assumes a Read The Docs theme for opensource projects
        ],
    }
)
