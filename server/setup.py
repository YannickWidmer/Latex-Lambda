from setuptools import setup

setup(
    name='pdf_server',
    packages=['pdf_server'],
    include_package_data=True,
    install_requires=[
        'flask','pybase64','boto3','bs4'
    ],
)
