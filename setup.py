#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from distutils.core import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.


setup(name = "PyDefCal",
    version = "0.0.1",
    description = "Vasp defect formation calculation",
    author = "ChangChunHe",
    author_email = "changchun_he@foxmail.com",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found
    #recursively.)
    packages = ['PyDefCal'],
    install_requires=['numpy>=1.15.4','sagar','seekpath']
)
