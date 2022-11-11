# -*- coding: utf-8 -*-
'''
Created on Oct 12 2021

@author: hilee
'''


from setuptools import setup, find_packages


setup(
    name='IGRINS2',
    version='1.0.0',
    author='hilee',
    author_email='hyeinlee@kasi.re.kr',
    description='IGRINS2 HKP CLI',
    packages=find_packages(),
    entry_points={
        "console_scripts": [
	    "hkp = HKP.HK_cli:CliCommand"
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)


