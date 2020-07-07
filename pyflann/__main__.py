# -*- coding: utf-8 -*-
def main():  # nocover
    import pyflann

    print('Looks like the imports worked')
    print('pyflann = {!r}'.format(pyflann))
    print('pyflann.__file__ = {!r}'.format(pyflann.__file__))
    print('pyflann.__version__ = {!r}'.format(pyflann.__version__))
    print('pyflann.FLANN = {!r}'.format(pyflann.FLANN))
    print('pyflann.flannlib = {!r}'.format(pyflann.flannlib))


if __name__ == '__main__':
    """
    CommandLine:
       python -m pyflann
    """
    main()
