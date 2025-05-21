import importlib.abc as _iabc
import importlib.machinery as _im
import os.path as _path
from . import main as _m
from sys import path as _syspath, meta_path as _metapath
class NpyLoader(_iabc.SourceLoader):
    def __init__(self, path):
        self.path = path

    def get_filename(self, fullname):
        return self.path

    def get_data(self, path):
        with open(path, 'rb') as f:
            return f.read()

    def source_to_code(self, data, path=''):
        source = data.decode('utf-8')
        transpiled_source = _m.ncompile(source)
        return compile(transpiled_source, path, 'exec')

class NpxLoader(_iabc.SourceLoader):
    def __init__(self, path):
        self.path = path

    def get_filename(self, fullname):
        return self.path

    def get_data(self, path):
        with open(path, 'rb') as f:
            return f.read()

    def source_to_code(self, data, path=''):
        source = data.decode('utf-8')
        transpiled_source = _m.ncompile(source, cythonic=True)
        return compile(transpiled_source, path, 'exec')

class MyFinder(_iabc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        module_name = fullname.rpartition('.')[-1]

        # Search for .npy file
        if path is None:
            search_paths = _syspath
        else:
            search_paths = path

        for dir_path in search_paths:
            npy_path = _path.join(dir_path, module_name + '.npy')
            if _path.isfile(npy_path):
                loader = NpyLoader(npy_path)
                return _im.ModuleSpec(fullname, loader)

            npx_path = _path.join(dir_path, module_name + '.npx')
            if _path.isfile(npx_path):
                loader = NpxLoader(npx_path)
                return _im.ModuleSpec(fullname, loader)

        return None  # Not found

# Insert your finder at the front of sys.meta_path
_metapath.insert(0, MyFinder())

