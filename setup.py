from setuptools import setup, find_packages

setup(
	name='assignment1',
	version='1.0',
	author='Anvesh Gupta',
	authour_email='anvesh.gupta@ufl.edu',
	packages=find_packages(exclude=('tests', 'docs')),
	setup_requires=['pytest-runner'],
	tests_require=['pytest']	
)