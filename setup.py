from setuptools import setup, find_packages

setup(
    name='FTR',
    version='0.0.0',
    author='Mauricio Petersen',
    python_requires='>=3.8',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    # package_data={  # include files/directories as parts of the library
    # 'my_library': [whl_path]
    # }
    # install_requires=[  # also install:
    # 'wheel',
    # 'setuptools',
    # 'requests'  # a standard dependency of PyPI
    # ],
)
