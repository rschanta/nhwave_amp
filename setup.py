from setuptools import setup, find_packages

setup(
    name="nhwave_amp",             
    version="0.0.0",                      
    description="automated, modular, pipline for NHWAVE",
    author="Ryan Schanta",
    author_email="rschanta@uw.com",
    license="MIT",                        

    packages=find_packages(),             
    python_requires=">=3.8",              
    classifiers=[                         
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)