#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pyflann import FLANN, index_type
from numpy import arange
from numpy.random import rand, randn
import unittest


class Test_PyFLANN_nn(unittest.TestCase):
    def setUp(self):
        self.nn = FLANN()


class Test_PyFLANN_nn_index(unittest.TestCase):
    def testnn_index_save_kdtree_1(self):
        self.run_nn_index_save_perturbed(64, 1000, algorithm='kdtree', trees=1)

    def testnn_index_save_kdtree_4(self):
        self.run_nn_index_save_perturbed(64, 1000, algorithm='kdtree', trees=4)

    def testnn_index_save_kdtree_10(self):
        self.run_nn_index_save_perturbed(64, 1000, algorithm='kdtree', trees=10)

    def testnn_index_save_kmeans_2(self):
        self.run_nn_index_save_perturbed(
            64, 1000, algorithm='kmeans', branching=2, iterations=11
        )

    def testnn_index_save_kmeans_16(self):
        self.run_nn_index_save_perturbed(
            64, 1000, algorithm='kmeans', branching=16, iterations=11
        )

    def testnn_index_save_kmeans_32(self):
        self.run_nn_index_save_perturbed(
            64, 1000, algorithm='kmeans', branching=32, iterations=11
        )

    def testnn_index_save_kmeans_64(self):
        self.run_nn_index_save_perturbed(
            64, 1000, algorithm='kmeans', branching=64, iterations=11
        )

    def testnn__save_kdtree_1(self):
        self.run_nn_index_save_rand(
            64, 10000, 1000, algorithm='kdtree', trees=1, checks=128
        )

    def testnn__save_kdtree_4(self):
        self.run_nn_index_save_rand(
            64, 10000, 1000, algorithm='kdtree', trees=4, checks=128
        )

    def testnn__save_kdtree_10(self):
        self.run_nn_index_save_rand(
            64, 10000, 1000, algorithm='kdtree', trees=10, checks=128
        )

    def testnn__save_kmeans_2(self):
        self.run_nn_index_save_rand(
            64,
            1000,
            1000,
            algorithm='kmeans',
            branching=2,
            iterations=11,
            checks=64,
        )

    def testnn__save_kmeans_8(self):
        self.run_nn_index_save_rand(
            64,
            10000,
            1000,
            algorithm='kmeans',
            branching=8,
            iterations=11,
            checks=32,
        )

    def testnn__save_kmeans_16(self):
        self.run_nn_index_save_rand(
            64,
            10000,
            1000,
            algorithm='kmeans',
            branching=16,
            iterations=11,
            checks=40,
        )

    def testnn__save_kmeans_32(self):
        self.run_nn_index_save_rand(
            64,
            10000,
            1000,
            algorithm='kmeans',
            branching=32,
            iterations=11,
            checks=56,
        )

    def run_nn_index_save_perturbed(self, dim, N, **kwargs):

        x = rand(N, dim)

        nn = FLANN()
        nn.build_index(x, **kwargs)
        nn.save_index('index.dat')
        nn.delete_index()

        nn = FLANN()
        nn.load_index('index.dat', x)
        x_query = x + randn(x.shape[0], x.shape[1]) * 0.0001 / dim
        nnidx, nndist = nn.nn_index(x_query)
        correct = all(nnidx == arange(N, dtype=index_type))

        nn.delete_index()
        self.assertTrue(correct)

    def run_nn_index_save_rand(self, dim, N, Nq, **kwargs):

        x = rand(N, dim)
        x_query = rand(Nq, dim)

        # build index, search and delete it
        nn = FLANN()
        nn.build_index(x, **kwargs)
        nnidx, nndist = nn.nn_index(x_query, checks=kwargs['checks'])
        nn.save_index('index.dat')
        del nn

        # now reload index and search again
        nn = FLANN()
        nn.load_index('index.dat', x)
        nnidx2, nndist2 = nn.nn_index(x_query, checks=kwargs['checks'])
        del nn

        correct = all(nnidx == nnidx2)
        self.assertTrue(correct)


if __name__ == '__main__':
    unittest.main()
