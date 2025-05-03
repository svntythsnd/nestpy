from setuptools import find_packages, setup
from os import path as osp, system as runcmd

def parse(filename):
    return osp.join(osp.dirname(__file__), filename)

def read(filename):
    return open(parse(filename), 'r').read()


param = eval(read('param.i'))

version = param['version']
test = param['test']

with open(parse('../README.md'), 'r') as f, open(parse('README.md'), 'w') as fn:
    readme = f.read()
    fn.write(readme)

    setup(
        name='nestpython',
        packages=find_packages(include=['nestpython']),
        version=version,
        description='python with braces.',
        author='slycedf',
        license='MIT',
        long_description=readme,
        long_description_content_type='text/markdown',
        classifiers=[
            "Development Status :: 4 - Beta"
        ]
    )

token = open(f'D:/slycefolder/ins/nsp/{ {True: "tt", False: "tr"}[test]}', 'r').read()

runcmd(
    f'pause & python -m twine upload --repository { {True: "testpypi", False: "pypi"}[test]} dist/*{version}* -u __token__ -p {token} --verbose')
