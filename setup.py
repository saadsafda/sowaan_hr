from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in sowaan_hr/__init__.py
from sowaan_hr import __version__ as version

setup(
	name="sowaan_hr",
	version=version,
	description="Modern HR features",
	author="Sowaan",
	author_email="info@sowaan.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
