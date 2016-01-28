
# This files is responsible for compilling all python extensions in shared_modules

# monkey-patch for parallel compilation
def parallelCCompile(self, sources, output_dir=None, macros=None, include_dirs=None, debug=0, extra_preargs=None, extra_postargs=None, depends=None):
    # those lines are copied from distutils.ccompiler.CCompiler directly
    macros, objects, extra_postargs, pp_opts, build = self._setup_compile(output_dir, macros, include_dirs, sources, depends, extra_postargs)
    cc_args = self._get_cc_args(pp_opts, debug, extra_preargs)
    # parallel code
    N=4 # number of parallel compilations
    import multiprocessing.pool
    def _single_compile(obj):
        try: src, ext = build[obj]
        except KeyError: return
        self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)
    # convert to list, imap is evaluated on-demand
    list(multiprocessing.pool.ThreadPool(N).imap(_single_compile,objects))
    return objects
import distutils.ccompiler
distutils.ccompiler.CCompiler.compile=parallelCCompile

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy as np
import os, platform



dependencies = []
# include all header files, to recognize changes
for dirpath, dirnames, filenames in os.walk("cpp"):
    for filename in [f for f in filenames if f.endswith(".h")]:
        dependencies.append( os.path.join(dirpath, filename) )

extensions = [
    Extension(
        name="square_marker_detect",
        sources=['square_marker_detect.pyx' ],
        include_dirs = [ np.get_include() ],
        libraries = ['opencv_core'],
        #library_dirs = ['/usr/local/lib'],
        extra_link_args=[], #'-WL,-R/usr/local/lib'
        extra_compile_args=["-std=c++11",'-w','-O2'], #-w hides warnings
        depends= dependencies,
        language="c++"),

]

setup(
    name="shared_modules",
    version="0.1",
    url="https://github.com/pupil-labs/pupil",
    author='Pupil Labs',
    author_email='info@pupil-labs.com',
    license='GNU',
    ext_modules=cythonize(extensions)
)

