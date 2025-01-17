# -*- coding: utf-8 -*-
# Copyright 2008-2009  Marius Muja (mariusm@cs.ubc.ca). All rights reserved.
# Copyright 2008-2009  David G. Lowe (lowe@cs.ubc.ca). All rights reserved.
#
# THE BSD LICENSE
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# from ctypes import *
# from ctypes.util import find_library
from numpy import float32, float64, uint8, int32, require

# import ctypes
# import numpy as np
from ctypes import (
    Structure,
    c_char_p,
    c_int,
    c_float,
    c_uint,
    c_long,
    c_void_p,
    cdll,
    POINTER,
)
from numpy.ctypeslib import ndpointer
import sys

STRING = c_char_p


class CustomStructure(Structure):
    """
    This class extends the functionality of the ctype's structure
    class by adding custom default values to the fields and a way of translating
    field types.
    """

    _defaults_ = {}
    _translation_ = {}

    def __init__(self):
        Structure.__init__(self)
        self.__field_names = [f for (f, t) in self._fields_]
        self.update(self._defaults_)

    def update(self, dict):
        for k, v in dict.items():
            if k in self.__field_names:
                setattr(self, k, self.__translate(k, v))
            else:
                raise KeyError('No such member: ' + k)

    def __getitem__(self, k):
        if k in self.__field_names:
            return self.__translate_back(k, getattr(self, k))

    def __setitem__(self, k, v):
        if k in self.__field_names:
            setattr(self, k, self.__translate(k, v))
        else:
            raise KeyError('No such member: ' + k)

    def keys(self):
        return self.__field_names

    def __translate(self, k, v):
        if k in self._translation_:
            if v in self._translation_[k]:
                return self._translation_[k][v]
        return v

    def __translate_back(self, k, v):
        if k in self._translation_:
            for tk, tv in self._translation_[k].items():
                if tv == v:
                    return tk
        return v


class FLANNParameters(CustomStructure):
    _fields_ = [
        ('algorithm', c_int),
        ('checks', c_int),
        ('eps', c_float),
        ('sorted', c_int),
        ('max_neighbors', c_int),
        ('cores', c_int),
        ('trees', c_int),
        ('leaf_max_size', c_int),
        ('branching', c_int),
        ('iterations', c_int),
        ('centers_init', c_int),
        ('cb_index', c_float),
        ('target_precision', c_float),
        ('build_weight', c_float),
        ('memory_weight', c_float),
        ('sample_fraction', c_float),
        ('table_number_', c_uint),
        ('key_size_', c_uint),
        ('multi_probe_level_', c_uint),
        ('log_level', c_int),
        ('random_seed', c_long),
    ]
    _defaults_ = {
        'algorithm': 'kdtree',
        'checks': 32,
        'eps': 0.0,
        'sorted': 1,
        'max_neighbors': -1,
        'cores': 0,
        'trees': 1,
        'leaf_max_size': 4,
        'branching': 32,
        'iterations': 5,
        'centers_init': 'random',
        'cb_index': 0.5,
        'target_precision': 0.9,
        'build_weight': 0.01,
        'memory_weight': 0.0,
        'sample_fraction': 0.1,
        'table_number_': 12,
        'key_size_': 20,
        'multi_probe_level_': 2,
        'log_level': 'warning',
        'random_seed': -1,
    }
    _translation_ = {
        'algorithm': {
            'linear': 0,
            'kdtree': 1,
            'kmeans': 2,
            'composite': 3,
            'kdtree_single': 4,
            'hierarchical': 5,
            'lsh': 6,
            'saved': 254,
            'autotuned': 255,
            'default': 1,
        },
        'centers_init': {'random': 0, 'gonzales': 1, 'kmeanspp': 2, 'default': 0},
        'log_level': {
            'none': 0,
            'fatal': 1,
            'error': 2,
            'warning': 3,
            'info': 4,
            'default': 2,
        },
    }


default_flags = ['C_CONTIGUOUS', 'ALIGNED']
allowed_types = [float32, float64, uint8, int32]

FLANN_INDEX = c_void_p


def load_flann_library():
    """
    CommandLine:
        python -c "import pyflann" --verbose
    """
    from os.path import join, abspath, dirname, exists, normpath

    # flann_lib_path = os.environ.get('FLANN_LIBRARY_PATH', None)

    tried_paths = []

    verbose = '--verbose' in sys.argv
    verbose |= '--veryverbose' in sys.argv
    verbose |= '--very-verbose' in sys.argv
    verbose |= '--verbflann' in sys.argv
    verbose |= '--verb-flann' in sys.argv

    if sys.platform == 'win32':
        possible_libnames = ['flann.dll', 'libflann.dll']
    elif sys.platform == 'darwin':
        possible_libnames = ['libflann.dylib']
    else:
        possible_libnames = ['libflann.so']

    # FIXME; this should really be @LIBRARY_OUTPUT_DIRECTORY@

    if verbose:
        print('[flann] Loading FLANN shared library')

    def get_plat_specifier():
        """
        Standard platform specifier used by distutils
        """
        import distutils

        plat_name = distutils.util.get_platform()
        plat_specifier = '.%s-%s' % (plat_name, sys.version[0:3])
        if hasattr(sys, 'gettotalrefcount'):
            plat_specifier += '-pydebug'
        return plat_specifier

    possible_subdirs = []

    try:
        # FIXME: this should be put in src dir by cmake scripts
        distutils_libdir = join('build', 'lib' + get_plat_specifier(), 'pyflann', 'lib')
        possible_subdirs.append(distutils_libdir)

        distutils_libdir = join('cmake_builds', 'build' + get_plat_specifier(), 'lib')
        possible_subdirs.append(distutils_libdir)
    except Exception:
        distutils_libdir = join('build', 'lib', 'pyflann', 'lib')

    possible_subdirs.append(join('build', 'lib', 'pyflann', 'lib'))
    possible_subdirs.append('lib')
    possible_subdirs.append('build/lib')

    if True:
        # Exhaustive checks to find library
        def gen_possible_libpaths():
            root_dir = abspath(dirname(__file__))
            while root_dir is not None:
                for subdir in possible_subdirs:
                    for libname in possible_libnames:
                        libpath = normpath(join(root_dir, subdir, libname))
                        yield libpath
                tmp = dirname(root_dir)
                if tmp == root_dir:
                    root_dir = None
                else:
                    root_dir = tmp

        possible_libpaths = gen_possible_libpaths()
    else:
        # Specific checks to find library
        root_dir = abspath(dirname(__file__))
        possible_libpaths = [
            normpath(join(libdir, libname))
            for libname in possible_libnames
            for libdir in [
                join(dirname(root_dir), distutils_libdir),
                join(root_dir, 'lib'),
                join(root_dir, '.'),
                # join(root_dir, '../../../build/lib'),
                # join(root_dir, 'build/lib'),
                # join(root_dir, '.'),
            ]
        ]

    flannlib = None
    for libpath in possible_libpaths:
        if verbose:
            print('[flann] Trying %s' % (libpath,))
        tried_paths.append(libpath)
        try:
            flannlib = cdll[libpath]
        except Exception:
            flannlib = None
            if exists(libpath):
                if verbose:
                    print('[flann]... exists! CDLL error!')
                raise
            else:
                if verbose:
                    print('[flann] ... does not exist')
        else:
            if verbose:
                print('[flann] ... exists')
            break

    if flannlib is None:
        # if we didn't find the library so far, try loading
        # using a relative path as a last resort
        for libpath in possible_libnames:
            try:
                if verbose:
                    print('[flann] Trying to fallback on %s' % (libpath,))
                tried_paths.append(libpath)
                flannlib = cdll[libpath]
                break
            except Exception:
                flannlib = None

    if flannlib is None:
        import warnings

        warnings.warn('Unable to load C library for FLANN')
    elif verbose:
        print('[flann] Using %r' % (flannlib,))
    return flannlib


flannlib = load_flann_library()


class FlannLib(object):
    pass


flann = FlannLib()


type_mappings = (
    ('float', 'float32'),
    ('double', 'float64'),
    ('byte', 'uint8'),
    ('int', 'int32'),
)


def define_functions(fmtstr):
    try:
        for type_ in type_mappings:
            source = fmtstr % {'C': type_[0], 'numpy': type_[1]}
            code = compile(source, '<string>', 'exec')
            eval(code)
    except AttributeError:
        print('+=========')
        print('Error compling code')
        print('+ format string ---------')
        print(fmtstr)
        print('+ failing instance ---------')
        print(source)
        print('L_________')
        raise


if flannlib is not None:
    flannlib.flann_log_verbosity.restype = None
    flannlib.flann_log_verbosity.argtypes = [c_int]  # level

    flannlib.flann_set_distance_type.restype = None
    flannlib.flann_set_distance_type.argtypes = [
        c_int,
        c_int,
    ]

    flann.build_index = {}
    define_functions(
        r"""
flannlib.flann_build_index_%(C)s.restype = FLANN_INDEX
flannlib.flann_build_index_%(C)s.argtypes = [
    ndpointer(%(numpy)s, ndim=2, flags='aligned, c_contiguous'),  # dataset
    c_int,  # rows
    c_int,  # cols
    POINTER(c_float),  # speedup
    POINTER(FLANNParameters)  # flann_params
]
flann.build_index[%(numpy)s] = flannlib.flann_build_index_%(C)s
    """
    )

    flann.used_memory = {}
    define_functions(
        r"""
flannlib.flann_used_memory_%(C)s.restype = c_int
flannlib.flann_used_memory_%(C)s.argtypes = [
        FLANN_INDEX,  # index_ptr
]
flann.used_memory[%(numpy)s] = flannlib.flann_used_memory_%(C)s
    """
    )

    flann.add_points = {}
    define_functions(
        r"""
flannlib.flann_add_points_%(C)s.restype = None
flannlib.flann_add_points_%(C)s.argtypes = [
        FLANN_INDEX, # index_id
        ndpointer(%(numpy)s, ndim = 2, flags='aligned, c_contiguous'), # dataset
        c_int, # rows
        c_int, # rebuild_threshhold
]
flann.add_points[%(numpy)s] = flannlib.flann_add_points_%(C)s
    """
    )

    flann.remove_point = {}
    define_functions(
        r"""
flannlib.flann_remove_point_%(C)s.restype = None
flannlib.flann_remove_point_%(C)s.argtypes = [
        FLANN_INDEX,  # index_ptr
        c_int,  # id_
]
flann.remove_point[%(numpy)s] = flannlib.flann_remove_point_%(C)s
    """
    )

    flann.save_index = {}
    define_functions(
        r"""
flannlib.flann_save_index_%(C)s.restype = None
flannlib.flann_save_index_%(C)s.argtypes = [
        FLANN_INDEX,  # index_id
        c_char_p #filename
]
flann.save_index[%(numpy)s] = flannlib.flann_save_index_%(C)s
    """
    )

    flann.load_index = {}
    define_functions(
        r"""
flannlib.flann_load_index_%(C)s.restype = FLANN_INDEX
flannlib.flann_load_index_%(C)s.argtypes = [
        c_char_p,  #filename
        ndpointer(%(numpy)s, ndim=2, flags='aligned, c_contiguous'),  # dataset
        c_int,  # rows
        c_int,  # cols
]
flann.load_index[%(numpy)s] = flannlib.flann_load_index_%(C)s
    """
    )

    flann.find_nearest_neighbors = {}
    define_functions(
        r"""
flannlib.flann_find_nearest_neighbors_%(C)s.restype = c_int
flannlib.flann_find_nearest_neighbors_%(C)s.argtypes = [
        ndpointer(%(numpy)s, ndim=2, flags='aligned, c_contiguous'),  # dataset
        c_int,  # rows
        c_int,  # cols
        ndpointer(%(numpy)s, ndim=2, flags='aligned, c_contiguous'),  # testset
        c_int,  # tcount
        ndpointer(int32, ndim=2, flags='aligned, c_contiguous, writeable'),  # result
        ndpointer(float32, ndim=2, flags='aligned, c_contiguous, writeable'),  # dists
        c_int,  # nn
        POINTER(FLANNParameters)  # flann_params
]
flann.find_nearest_neighbors[%(numpy)s] = flannlib.flann_find_nearest_neighbors_%(C)s
    """
    )

    # fix definition for the 'double' case

    flannlib.flann_find_nearest_neighbors_double.restype = c_int
    flannlib.flann_find_nearest_neighbors_double.argtypes = [
        ndpointer(float64, ndim=2, flags='aligned, c_contiguous'),  # dataset
        c_int,  # rows
        c_int,  # cols
        ndpointer(float64, ndim=2, flags='aligned, c_contiguous'),  # testset
        c_int,  # tcount
        ndpointer(int32, ndim=2, flags='aligned, c_contiguous, writeable'),  # result
        ndpointer(float64, ndim=2, flags='aligned, c_contiguous, writeable'),  # dists
        c_int,  # nn
        POINTER(FLANNParameters),  # flann_params
    ]
    flann.find_nearest_neighbors[float64] = flannlib.flann_find_nearest_neighbors_double

    flann.find_nearest_neighbors_index = {}
    define_functions(
        r"""
flannlib.flann_find_nearest_neighbors_index_%(C)s.restype = c_int
flannlib.flann_find_nearest_neighbors_index_%(C)s.argtypes = [
        FLANN_INDEX,  # index_id
        ndpointer(%(numpy)s, ndim=2, flags='aligned, c_contiguous'),  # testset
        c_int,  # tcount
        ndpointer(int32, ndim=2, flags='aligned, c_contiguous, writeable'),  # result
        ndpointer(float32, ndim=2, flags='aligned, c_contiguous, writeable'),  # dists
        c_int,  # nn
        POINTER(FLANNParameters) # flann_params
]
flann.find_nearest_neighbors_index[%(numpy)s] = flannlib.flann_find_nearest_neighbors_index_%(C)s
    """
    )

    flannlib.flann_find_nearest_neighbors_index_double.restype = c_int
    flannlib.flann_find_nearest_neighbors_index_double.argtypes = [
        FLANN_INDEX,  # index_id
        ndpointer(float64, ndim=2, flags='aligned, c_contiguous'),  # testset
        c_int,  # tcount
        ndpointer(int32, ndim=2, flags='aligned, c_contiguous, writeable'),  # result
        ndpointer(float64, ndim=2, flags='aligned, c_contiguous, writeable'),  # dists
        c_int,  # nn
        POINTER(FLANNParameters),  # flann_params
    ]
    flann.find_nearest_neighbors_index[
        float64
    ] = flannlib.flann_find_nearest_neighbors_index_double

    flann.radius_search = {}
    define_functions(
        r"""
flannlib.flann_radius_search_%(C)s.restype = c_int
flannlib.flann_radius_search_%(C)s.argtypes = [
        FLANN_INDEX,  # index_id
        ndpointer(%(numpy)s, ndim=1, flags='aligned, c_contiguous'),  # query
        ndpointer(int32, ndim=1, flags='aligned, c_contiguous, writeable'),  # indices
        ndpointer(float32, ndim=1, flags='aligned, c_contiguous, writeable'),  # dists
        c_int,  # max_nn
        c_float,  # radius
        POINTER(FLANNParameters) # flann_params
]
flann.radius_search[%(numpy)s] = flannlib.flann_radius_search_%(C)s
    """
    )

    flannlib.flann_radius_search_double.restype = c_int
    flannlib.flann_radius_search_double.argtypes = [
        FLANN_INDEX,  # index_id
        ndpointer(float64, ndim=1, flags='aligned, c_contiguous'),  # query
        ndpointer(int32, ndim=1, flags='aligned, c_contiguous, writeable'),  # indices
        ndpointer(float64, ndim=1, flags='aligned, c_contiguous, writeable'),  # dists
        c_int,  # max_nn
        c_float,  # radius
        POINTER(FLANNParameters),  # flann_params
    ]
    flann.radius_search[float64] = flannlib.flann_radius_search_double

    flann.compute_cluster_centers = {}
    define_functions(
        r"""
flannlib.flann_compute_cluster_centers_%(C)s.restype = c_int
flannlib.flann_compute_cluster_centers_%(C)s.argtypes = [
        ndpointer(%(numpy)s, ndim=2, flags='aligned, c_contiguous'),  # dataset
        c_int,  # rows
        c_int,  # cols
        c_int,  # clusters
        ndpointer(float32, flags='aligned, c_contiguous, writeable'),  # result
        POINTER(FLANNParameters)  # flann_params
]
flann.compute_cluster_centers[%(numpy)s] = flannlib.flann_compute_cluster_centers_%(C)s
    """
    )
    # double is an exception
    flannlib.flann_compute_cluster_centers_double.restype = c_int
    flannlib.flann_compute_cluster_centers_double.argtypes = [
        ndpointer(float64, ndim=2, flags='aligned, c_contiguous'),  # dataset
        c_int,  # rows
        c_int,  # cols
        c_int,  # clusters
        ndpointer(float64, flags='aligned, c_contiguous, writeable'),  # result
        POINTER(FLANNParameters),  # flann_params
    ]
    flann.compute_cluster_centers[float64] = flannlib.flann_compute_cluster_centers_double

    flann.free_index = {}
    define_functions(
        r"""
flannlib.flann_free_index_%(C)s.restype = None
flannlib.flann_free_index_%(C)s.argtypes = [
        FLANN_INDEX,  # index_id
        POINTER(FLANNParameters) # flann_params
]
flann.free_index[%(numpy)s] = flannlib.flann_free_index_%(C)s
    """
    )


def ensure_2d_array(arr, flags, **kwargs):
    arr = require(arr, requirements=flags, **kwargs)
    if len(arr.shape) == 1:
        arr = arr.reshape(-1, arr.size)
    return arr
