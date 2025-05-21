from os import mkdir as _mkdir
import os.path as _path
from os import walk as _walk
from os import scandir as _scandir
from os import chdir as _chdir
from os import getcwd as _getcwd
from shutil import copyfile as _copyfile
from shutil import rmtree as _rmtree

from . import main as _m

_slashConverter = str.maketrans('\\','/')
def _getAllFilePaths(dirPath):
    return [
        _path.join(dirpath,f).translate(_slashConverter) for (
            dirpath, dirnames, filenames
        ) in _walk(dirPath) for f in filenames
    ]

def _getFilesDirs(dirPath):
    oldDir=_getcwd()
    _chdir(dirPath)
    a = []
    b = []
    for f in _scandir():
        g = f.path.translate(_slashConverter).removeprefix('./')
        if f.is_dir():
            b.append(g)
        else:
            a.append(g)
    _chdir(oldDir)
    return a, b

def _filterByFileExt(files, *fileExts:str):
    passed = []
    failed = []
    for file in files:
        if any(file.endswith(fileExt) for fileExt in fileExts):
            passed.append(file)
            continue
        failed.append(file)
    return passed, failed

def ncompile_to(file:str, new_file:str=None, *, indent_amount:int=1, replace_previous:bool=False, cythonic:bool=None, tokenlog:bool=False):
  cythonic = _path.splitext(file)[~0] == '.npx' if cythonic is None else cythonic
  new_file = f'{_path.splitext(file)[0]}.py{"x" if cythonic else ""}' if new_file is None else new_file
  def compile(file):
    print(f'> compiling {file}')
    with (
      open(file, 'r', encoding='utf-8') as f,
      open(new_file, 'w', encoding='utf-8') as fn):
        fn.write(_m.ncompile(f.read(), indent_amount=indent_amount, cythonic=cythonic, tokenlog=tokenlog, filename=file))
  if not _path.isfile(new_file) or replace_previous:
    compile(file)
  else:
    i = input(
      f'File \'{file}\' already exists. Would you like to overwrite it? [y/(n)]: ')
    if i.lower() == 'y':
      compile(file)


def nbuild(dir:str, new_dir:str, *, indent_amount:int=1, erase_dir:bool=None,
           replace_previous:bool=False, transfer_other_files:bool=True):
 subpath = ''
 def subbuild():
    nonlocal dir
    nonlocal subpath
    nonlocal new_dir
    nonlocal indent_amount
    nonlocal erase_dir
    nonlocal replace_previous
    nonlocal transfer_other_files
    if _path.isdir(f'{new_dir}/{subpath}'):
      def remove():
        _rmtree(f'{new_dir}/{subpath}')
        _mkdir(f'{new_dir}/{subpath}')
      if erase_dir:
          remove()
      elif erase_dir is None:
          i = input(
            f'Directory \'{new_dir}/{subpath}\' already exists. Would you like to erase it? [y/(n)]: ')
          if i.lower() == 'y':
            remove()

    else:
      _mkdir(f'{new_dir}/{subpath}')
    compilable, leaveBe = _filterByFileExt(_getFilesDirs(f'{dir}/{subpath}')[0], '.npy', '.npx')
    for file in compilable:
      ncompile_to(f'{dir}/{subpath}/{file}', f'{new_dir}/{subpath}/{(fsplit := _path.splitext(file.rsplit("/", 1)[-1]))[0]}.py{"x" if fsplit[~0] == ".npx" else ""}',
               indent_amount=indent_amount, replace_previous=replace_previous)
    if transfer_other_files:
      for file in leaveBe:
        print(f'> transferring {dir}/{subpath}/{file}')
        _copyfile(f'{dir}/{subpath}/{file}', f'{new_dir}/{subpath}/{file.rsplit("/", 1)[-1].lstrip("/")}')
    for subdir in _getFilesDirs(f'{dir}/{subpath}')[~0]:
        subpath += subdir
        subbuild()

 subbuild()
 print(f'> compiled!\n')

def ncompile(file:str, *, indent_amount:int=1, cythonic:bool=None, tokenlog:bool=False):
  cythonic = _path.splitext(file)[~0] == '.npx' if cythonic is None else cythonic
  with open(file, 'r', encoding='utf-8') as f:
    return _m.ncompile(f.read(), indent_amount=indent_amount, cythonic=cythonic, tokenlog=tokenlog, filename=file)

def nexec(file:str, *, indent_amount:int=1, cythonic:bool=None, tokenlog:bool=False):
  from . import imports as importHandler
  del importHandler
  exec(ncompile(file, indent_amount=indent_amount, cythonic=cythonic, tokenlog=tokenlog))