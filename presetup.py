from os import path as osp, system as runcmd
import argparse

def read(filename):
    return open(osp.join(osp.dirname(__file__), filename)).read()


parser = argparse.ArgumentParser()

parser.add_argument('--test', action='store_true',
                    help='testpypi vs. pypi upload')

args = parser.parse_args()


param = eval(read('core/param.i'))

test = args.test

with open('core/param.i', 'w') as f:
    f.write(str({'test': test}))

runcmd(read('setup.bat'))
