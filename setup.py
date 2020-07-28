from setuptools import setup, find_packages

setup(
    name='synthpop',
    version='0.2.1',
    description='Population Synthesis',
    author='UrbanSim Inc.',
    author_email='udst@urbansim.com',
    license='BSD',
    url='https://github.com/udst/synthpop',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    packages=find_packages(exclude=['*.tests']),
    install_requires=[
        'census>=0.5',
        'numexpr==2.7.1',
        'numpy==1.18.3',
        'pandas==1.0.3',
        'scipy==1.4.1',
        'us>=0.8'
    ]
)
