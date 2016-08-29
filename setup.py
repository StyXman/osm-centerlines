from distutils.core import setup

setup (
    name='centerlines',
    version= '0.1',
    description= 'A module for calculating polygon centerlines.',
    author= 'Marcos Dione',
    author_email= 'mdione@grulic.org.ar',
    url= 'https://github.com/StyXman/osm-centerlines',
    packages= [ 'centerlines' ],
    scripts= [ 'centerlines-plugin-script.py' ],
    license= 'GPLv3',
    classifiers= [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        ],
    )
