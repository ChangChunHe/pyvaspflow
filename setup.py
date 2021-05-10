#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from distutils.core import setup
from os import pardir,path,mkdir

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.


setup(name = "pyvaspflow",
    version = "0.0.3",
    description = "Vasp Calculation",
    long_description="A Python package for VASP task preparation and submission maganement.",
    author = "hecc",
    author_email = "changchun_he@foxmail.com",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found
    #recursively.)
    packages = ['pyvaspflow','pyvaspflow.io','pyvaspflow.vasp','pyvaspflow.defect_cal'],
    install_requires=['numpy','sagar','seekpath','psutil','','progressbar2','matplotlib'],
    url="https://github.com/ChangChunHe/pyvaspflow",
    entry_points={
        'console_scripts': [
        'pyvasp = pyvaspflow.pyvasp:cli',
        ]}
)



home = path.expanduser("~")

if not path.isdir(path.join(home,'.config')):
    mkdir(path.join(home,'.config'))

if not path.isdir(path.join(home,'.config','pyvaspflow')):
    mkdir(path.join(home,'.config','pyvaspflow'))

if not path.isfile(path.join(home,'.config','pyvaspflow','config.ini')):
    with open("./config.ini","r") as f:
        lines = f.read()
    with open(path.join(home,'.config','pyvaspflow','config.ini'),'w') as outfile:
        outfile.write(lines)
