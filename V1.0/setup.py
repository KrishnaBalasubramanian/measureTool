from setuptools import setup

setup(
    name='measureTool',
    version='1.0',    
    description='A python package to interface electronic characterization tools',
    url='https://github.com/KrishnaBalasubramanian/measureTool',
    author='Krishna Balasubramanian',
    author_email='bkrishna@mse.iitd.ac.in',
    license='BSD 2-clause',
    packages=['measureTool'],
    install_requires=['matplotlib',
                      'numpy',
                      'pyvisa',
                      'lakeshore'
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
    ],
)
