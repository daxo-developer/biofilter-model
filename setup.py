from setuptools import setup, find_packages

setup(
    name='bio_model',
    version='0.1.0',
    author='Your Name',
    description='Reactive transport model with calibration and uncertainty analysis',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'numpy>=1.21.0',
        'scipy>=1.7.0',
        'matplotlib>=3.4.0',
        'pandas>=1.3.0',
        'requests>=2.28.0',
        'SALib>=1.4.7',
        'emcee>=3.1.1',
    ],
    extras_require={
        'dev': ['pytest>=7.0.0', 'pytest-cov>=4.0.0', 'flake8>=5.0.0', 'sphinx>=5.0.0'],
    },
    python_requires='>=3.9',
)
