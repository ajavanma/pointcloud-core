import unittest

import numpy as np

from pointcloud_core import LabelMap, PointCloud, PointCloudError, lift_voxel_values, voxelize


class VoxelTests(unittest.TestCase):
    def test_floor_boundaries_negative_coordinates_and_order(self):
        cloud = PointCloud(
            [[1, 0, 0], [-.01, 0, 0], [0, 0, 0], [.49, 0, 0], [-.5, 0, 0], [-.51, 0, 0]],
            [[10], [2], [4], [6], [8], [12]], [2, 0, 1, 0, 1, 2], [42, 4, 8, 12, 91, 3],
        )
        result = voxelize(cloud, .5)
        np.testing.assert_array_equal(result.voxel_coords, [[-2, 0, 0], [-1, 0, 0], [0, 0, 0], [2, 0, 0]])
        np.testing.assert_array_equal(result.features, [[12], [5], [5], [10]])
        np.testing.assert_array_equal(result.labels, [2, 0, 0, 2])
        np.testing.assert_array_equal(result.point_to_voxel, [3, 1, 2, 2, 1, 0])
        np.testing.assert_array_equal(result.point_indices, cloud.point_indices)

    def test_one_mask_and_lifting_preserve_original_rows(self):
        cloud = PointCloud([[0]*3, [np.nan, 0, 0], [1, 0, 0], [2, 0, 0], [1.1, 0, 0]],
                           [[1], [2], [3], [np.inf], [7]], point_indices=[99, 4, 87, 81, 62])
        result = voxelize(cloud, 1)
        np.testing.assert_array_equal(result.features, [[1], [5]])
        np.testing.assert_array_equal(result.point_to_voxel, [0, -1, 1, -1, 1])
        np.testing.assert_array_equal(lift_voxel_values([7, 42], result.point_to_voxel), [7, -1, 42, -1, 42])
        np.testing.assert_array_equal(result.point_indices, cloud.point_indices)

    def test_ignore_majority_tie_and_explicit_class_order(self):
        mapping = LabelMap((42, 0, 7), 255)
        cloud = PointCloud([[0]*3]*5 + [[1, 0, 0]]*2 + [[2, 0, 0]]*2,
                           labels=mapping.encode([255, 255, 0, 7, 7, 255, 255, 0, 42]))
        np.testing.assert_array_equal(voxelize(cloud, 1).labels, [2, -1, 0])

    def test_arbitrary_signed_labels_and_custom_ignore(self):
        cloud = PointCloud([[0]*3]*3 + [[1, 0, 0]], labels=[9, -4, 99, 99])
        np.testing.assert_array_equal(voxelize(cloud, 1, ignore_label=99).labels, [-4, 99])

    def test_geometry_only(self):
        result = voxelize(PointCloud([[0]*3, [.1, 0, 0]]), 1)
        self.assertEqual(result.features.shape, (1, 0))
        self.assertIsNone(result.labels)

    def test_large_feature_mean_avoids_naive_sum_overflow(self):
        maximum = np.finfo(float).max
        result = voxelize(PointCloud([[0]*3]*2, [[maximum, -maximum]]*2), 1)
        np.testing.assert_array_equal(result.features, [[maximum, -maximum]])

    def test_constant_extreme_means_preserve_subnormals_and_finite_maxima(self):
        maximum = np.finfo(float).max
        smallest = np.nextafter(0.0, 1.0)
        for count in (2, 3, 9, 11):
            with self.subTest(count=count):
                row = [smallest, -smallest, maximum, -maximum, 0]
                result = voxelize(PointCloud([[0]*3]*count, [row]*count), 1)
                np.testing.assert_array_equal(result.features, [row])

    def test_scaled_mean_handles_finite_cancellation_and_separate_voxel_scales(self):
        maximum = np.finfo(float).max
        smallest = np.nextafter(0.0, 1.0)
        result = voxelize(PointCloud(
            [[0]*3]*4 + [[1, 0, 0]]*3 + [[2, 0, 0]]*2,
            [[maximum], [maximum], [-maximum], [-maximum],
             [maximum], [maximum], [-maximum], [smallest], [smallest]],
        ), 1)
        np.testing.assert_array_equal(result.features[[0, 2]], [[0], [smallest]])
        np.testing.assert_allclose(result.features[1], [maximum / 3], rtol=2e-16, atol=0)

    def test_invalid_voxel_sizes_and_ignore_labels(self):
        cloud = PointCloud([[0]*3])
        for size in (True, np.bool_(True), 0, -1, np.nan, np.inf, '1', 1j, None, 10**400):
            with self.subTest(size=size), self.assertRaisesRegex(PointCloudError, 'voxel_size'):
                voxelize(cloud, size)
        for ignored in (True, 1.0, 2**63):
            with self.subTest(ignored=ignored), self.assertRaisesRegex(PointCloudError, 'ignore_label'):
                voxelize(cloud, 1, ignore_label=ignored)

    def test_coordinate_range_and_division_overflow(self):
        for coord in (float(2**63), np.nextafter(float(-(2**63)), -np.inf)):
            with self.subTest(coord=coord), self.assertRaisesRegex(PointCloudError, 'int64 range'):
                voxelize(PointCloud([[coord, 0, 0]]), 1)
        with self.assertRaisesRegex(PointCloudError, 'int64 range'):
            voxelize(PointCloud([[1, 0, 0]]), float.fromhex('0x0.0000000000001p-1022'))
        result = voxelize(PointCloud([[float(-(2**63)), 0, 0], [np.nextafter(float(2**63), 0), 0, 0]]), 1)
        np.testing.assert_array_equal(result.voxel_coords[:, 0], [-(2**63), 2**63-1024])

    def test_nonmutation_and_output_ownership(self):
        cloud = PointCloud(np.array([[0.0]*3, [np.nan, 0, 0]]), np.ones((2, 1)), np.array([0, -1]), np.array([99, 3]))
        before = {name: getattr(cloud, name).copy() for name in ('coords', 'features', 'labels', 'point_indices')}
        result = voxelize(cloud, 1)
        for name, original in before.items():
            np.testing.assert_array_equal(getattr(cloud, name), original)
        for name in ('features', 'labels', 'point_indices'):
            self.assertFalse(np.shares_memory(getattr(cloud, name), getattr(result, name)))

    def test_repetition_and_permutation_keep_aggregation_and_mapping(self):
        rng = np.random.default_rng(8)
        coords = rng.integers(-5, 6, size=(100, 3)).astype(float) / 4
        features = rng.integers(-20, 21, size=(100, 2)).astype(float)
        labels = rng.integers(-1, 4, size=100)
        first = voxelize(PointCloud(coords, features, labels), .5)
        repeated = voxelize(PointCloud(coords, features, labels), np.float64(.5))
        permutation = rng.permutation(100)
        shuffled = voxelize(PointCloud(coords[permutation], features[permutation], labels[permutation]), .5)
        for name in ('voxel_coords', 'features', 'labels', 'point_to_voxel', 'point_indices'):
            np.testing.assert_array_equal(getattr(first, name), getattr(repeated, name))
        np.testing.assert_array_equal(first.voxel_coords, shuffled.voxel_coords)
        np.testing.assert_allclose(first.features, shuffled.features)
        np.testing.assert_array_equal(first.labels, shuffled.labels)
        np.testing.assert_array_equal(first.point_to_voxel[permutation], shuffled.point_to_voxel)


if __name__ == '__main__':
    unittest.main()
