from setuptools import setup, find_packages
import os

setup(
    name="finaddr",
    version=os.getenv("FINADDR_BUILD_VERSION"),
    license="MIT",
    author="Pasi Talvitie",
    author_email="pasi@antispam.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/phasi/finaddr",
    keywords="finnish address data client",
)
