#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
from setuptools import setup, find_packages
#from distutils.core import setup

# Read in requirements.txt
requirements = open('requirements.txt').readlines()
requirements = [r.strip() for r in requirements]


setup(name='nbody_tucker',
        version=0.1,
        description='Run nbody_tucker',
        url='https://github.com/nmayhall-vt/nbody_tucker.git',
        author='Nick Mayhall',
        author_email='nmayhall@vt.edu',
        license='Apache 2',
        #packages=find_packages(where='src'),
        package_dir={'': 'src'},
        packages=[''],

        #packages=setuptools.find_packages(),
        install_requires=requirements,
        include_package_data=True,
        )

