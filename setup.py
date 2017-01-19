from setuptools import setup
import yaml
import os.path

with open(os.path.normpath(os.path.join(__file__, '..', 'conda-recipe', 'meta.yaml')), 'rb') as fp:
    data = yaml.load(fp)

setup(
    name=data['package']['name'],
    version=data['package']['version'],
    packages=[ data['package']['name'], ],
    entry_points={
        'console_scripts' : data['build']['entry_points'],
    }
)


