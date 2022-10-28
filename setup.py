from setuptools import setup

setup(
    name='fdorganizer',
    packages=['server'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
