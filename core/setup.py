from setuptools import find_packages, setup
from os import path as osp, system as runcmd

def parse(filename):
    return osp.join(osp.dirname(__file__), filename)

def read(filename):
    return open(parse(filename), 'r').read()


param = eval(read('param.i'))

import nestpython as c

version = c.__version__
test = param['test']

with open(parse('../README.md'), 'r') as f, open(parse('README.md'), 'w') as fn:
    readme = f.read()
    fn.write(readme)

    setup(
        name='nestpython',
        packages=find_packages(include=['nestpython']),
        version=version,
        description=c.__description__,
        author=c.__author__,
        license=c.__license__,
        long_description=readme,
        long_description_content_type='text/markdown',
        python_requires=">=3.10",
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Compilers',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Education',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: Implementation :: CPython',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
        ],
        url=c.__url__
    )

token = open(f'D:/slycefolder/ins/nsp/{ {True: "tt", False: "tr"}[test]}', 'r').read()

runcmd(
    f'pause & python -m twine upload --repository { {True: "testpypi", False: "pypi"}[test]} dist/*{version}* -u __token__ -p {token} --verbose')
