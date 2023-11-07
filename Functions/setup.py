from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        "world_map_editor_pyx.pyx", compiler_directives={"language_level": "3"}
    )
)