from setuptools import setup

setup(
    name='server',
    packages=['./'],
    include_package_data=True,
    install_requires=[
        'flask','pybase64','boto3','bs4'
    ],
)
