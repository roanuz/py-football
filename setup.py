from setuptools import setup

with open('Description.txt') as file:
    long_description = file.read()

setup(
    name='py-football',
    version='1.0.3',
    description = 'Easy to install and simple way to access all Roanuz Football APIs. Its a library for showing Live Football Score, Football Schedule and Statistics',
    long_description = long_description,

    author = 'Roanuz Softwares Private Ltd',
    author_email = 'contact@roanuz.com',
    url = 'https://github.com/roanuz/py-football',
    package_dir={'': 'src'},
    packages=[''],
    include_package_data=True,
    install_requires=['requests>=2.19.1'],
    entry_points={
        'console_scripts':
        ['pyfootball=src.pyfootball:RfaApp']
    }
)
