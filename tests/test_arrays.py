import unittest

import numpy as np

from pointcloud_core import PointCloud, PointCloudError, validate_cloud


class ArrayTests(unittest.TestCase):
    def test_geometry_only_defaults(self):
        result = validate_cloud(PointCloud([[0, 1, 2], [3, 4, 5]]))
        self.assertEqual(result.coords.dtype, np.dtype('float64'))
        self.assertEqual(result.features.shape, (2, 0))
        self.assertIsNone(result.labels)
        np.testing.assert_array_equal(result.point_indices, [0, 1])

    def test_normalization_owns_arrays(self):
        source = PointCloud(np.ones((2, 3)), np.ones((2, 1)), np.array([4, 7]), np.array([99, 3]))
        result = validate_cloud(source)
        for field in ('coords', 'features', 'labels', 'point_indices'):
            self.assertFalse(np.shares_memory(getattr(source, field), getattr(result, field)))
        result.coords[0] = 2
        np.testing.assert_array_equal(source.coords, np.ones((2, 3)))

    def test_finite_mask_is_deferred_without_reordering(self):
        result = validate_cloud(PointCloud([[0, 0, 0], [np.nan, 0, 0]], [[3], [np.inf]], [1, 2], [9, 2]))
        np.testing.assert_array_equal(result.point_indices, [9, 2])
        self.assertTrue(np.isnan(result.coords[1, 0]))
        self.assertTrue(np.isinf(result.features[1, 0]))

    def test_rejects_invalid_coordinate_shapes_and_types(self):
        for value in ([], 1, [[1, 2]], np.empty((0, 3)), [[1, 2, 3], [1]], [[True]*3], [[1j]*3], [['1']*3], [[10**400]*3]):
            with self.subTest(value=value), self.assertRaises(PointCloudError):
                validate_cloud(PointCloud(value))

    def test_rejects_misaligned_arrays(self):
        for kwargs in ({'features': [1, 2]}, {'features': [[1]]}, {'labels': [1]}, {'point_indices': [1]}, {'labels': [[1], [2]]}):
            with self.subTest(kwargs=kwargs), self.assertRaises(PointCloudError):
                validate_cloud(PointCloud([[0]*3, [1]*3], **kwargs))

    def test_rejects_noninteger_labels_and_indices(self):
        for field in ('labels', 'point_indices'):
            for value in ([1.0, 2.0], [True, False], np.array([1, 2**63], dtype=np.uint64), ['1', '2']):
                with self.subTest(field=field, value=value), self.assertRaises(PointCloudError):
                    validate_cloud(PointCloud([[0]*3, [1]*3], **{field: value}))

    def test_rejects_invalid_point_ids(self):
        for value in ([2, 2], [-1, 2]):
            with self.subTest(value=value), self.assertRaisesRegex(PointCloudError, 'unique nonnegative'):
                validate_cloud(PointCloud([[0]*3, [1]*3], point_indices=value))

    def test_rejects_all_invalid_rows_and_wrong_cloud_type(self):
        for cloud in (PointCloud([[np.nan]*3]), PointCloud([[0]*3], [[np.inf]]), {'coords': [[0]*3]}):
            with self.subTest(cloud=cloud), self.assertRaises(PointCloudError):
                validate_cloud(cloud)

    def test_extreme_signed_labels_and_point_ids_survive(self):
        result = validate_cloud(PointCloud([[0]*3], labels=[-(2**63)], point_indices=[2**63-1]))
        self.assertEqual(result.labels[0], -(2**63))
        self.assertEqual(result.point_indices[0], 2**63-1)


if __name__ == '__main__':
    unittest.main()
