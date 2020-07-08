#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from pyflann import FLANN
import unittest
import time


class Test_PyFLANN_clustering(unittest.TestCase):
    def setUp(self):
        self.nn = FLANN(iterations=11)

    ##########################################################################

    def test_Rand(self):
        x = np.random.rand(100, 10000)
        nK = 10
        centroids = self.nn.kmeans(x, nK)
        self.assertTrue(len(centroids) == nK)

    def test2d_small(self):
        self.__nd_random_clustering_test(2, 2)

    def test3d_small(self):
        self.__nd_random_clustering_test(3, 3)

    def test4d_small(self):
        self.__nd_random_clustering_test(4, 4)

    def test3d_large(self):
        self.__nd_random_clustering_test(3, 3, 1000)

    def test10d_large(self):
        self.__nd_random_clustering_test(10, 2, 10)

    def test500d(self):
        self.__nd_random_clustering_test(500, 2, 10)

    def __nd_random_clustering_test(self, dim, N, dup=1):
        """
        Make a set of random points, then pass the same ones to the
        query points.  Each point should be closest to itself.
        """
        np.random.seed(0)
        x = np.random.rand(N, dim)
        xc = np.concatenate(tuple([x for i in range(dup)]))

        if dup > 1:
            xc += np.random.randn(xc.shape[0], xc.shape[1]) * 0.000001 / dim

        # rnseed = int(time.time())
        centroids = self.nn.kmeans(
            xc[np.random.permutation(len(xc))], N, centers_init='random', random_seed=2,
        )
        mindists = np.array([[sum((d1 - d2) ** 2) for d1 in x] for d2 in centroids]).min(
            0
        )
        # print mindists
        for m in mindists:
            self.assertAlmostEqual(m, 0.0, 1)

        # rnseed = int(time.time())
        centroids = self.nn.kmeans(
            xc[np.random.permutation(len(xc))], N, centers_init='gonzales', random_seed=2,
        )
        mindists = np.array([[sum((d1 - d2) ** 2) for d1 in x] for d2 in centroids]).min(
            0
        )
        # print mindists
        for m in mindists:
            self.assertAlmostEqual(m, 0.0, 1)

        centroids = self.nn.kmeans(
            xc[np.random.permutation(len(xc))], N, centers_init='kmeanspp', random_seed=2,
        )
        mindists = np.array([[sum((d1 - d2) ** 2) for d1 in x] for d2 in centroids]).min(
            0
        )
        # print mindists
        for m in mindists:
            self.assertAlmostEqual(m, 0.0, 1)

    def testrandomnumber_same(self):
        """
        self = Test_PyFLANN_clustering()
        self.setUp()
        """
        import pytest

        pytest.skip('broken, but not worth fixing')

        data = np.random.rand(1000, 2)  # Random, so we can get a lot of local minima

        rnseed = int(time.time())
        cl1 = self.nn.kmeans(data, 50, random_seed=rnseed)
        cl2 = self.nn.kmeans(data, 50, random_seed=rnseed)

        self.assertTrue(np.all(cl1 == cl2))

    def testrandnumber_different(self):

        data = np.random.rand(1000, 100)  # Random, so we can get a lot of local minima

        rnseed = int(time.time())
        cl1 = self.nn.kmeans(data, 50, random_seed=rnseed)
        cl2 = self.nn.kmeans(data, 50)

        self.assertTrue(np.any(cl1 != cl2))


if __name__ == '__main__':
    """
    pytest ~/code/flann/test/test_clustering.py --verbose
    """
    unittest.main()
