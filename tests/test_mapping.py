import unittest
from fractions import Fraction

import numpy as np

from pointcloud_core import PointCloudError, lift_voxel_values


class MappingTests(unittest.TestCase):
    def test_labels_and_arbitrary_row_order(self):
        source = np.array([7, 42], dtype=np.int32)
        result = lift_voxel_values(source, [1, -1, 0, 1], fill_value=255)
        np.testing.assert_array_equal(result, [42, 255, 7, 42])
        self.assertEqual(result.dtype, source.dtype)
        self.assertFalse(np.shares_memory(result, source))

    def test_multidimensional_payload_and_nan_fill(self):
        values = np.arange(12, dtype=np.float32).reshape(2, 2, 3)
        result = lift_voxel_values(values, [1, -1, 0], fill_value=np.nan)
        np.testing.assert_array_equal(result[0], values[1])
        np.testing.assert_array_equal(result[2], values[0])
        self.assertTrue(np.isnan(result[1]).all())
        self.assertEqual(result.dtype, np.dtype('float32'))

    def test_boolean_payload(self):
        np.testing.assert_array_equal(lift_voxel_values([True, False], [0, -1, 1], fill_value=False), [True, False, False])

    def test_large_integer_fill_for_floating_payload(self):
        result = lift_voxel_values([1.0], [-1], fill_value=10**100)
        self.assertEqual(result[0], 1e100)
        with self.assertRaises(PointCloudError):
            lift_voxel_values([1.0], [-1], fill_value=10**400)

    def test_fraction_fill_for_floating_payload(self):
        result = lift_voxel_values([1.0], [-1], fill_value=Fraction(1, 2))
        self.assertEqual(result[0], 0.5)

    def test_empty_mappings_and_all_excluded_without_voxels(self):
        result = lift_voxel_values(np.empty((0, 2)), [-1, -1], fill_value=0)
        np.testing.assert_array_equal(result, np.zeros((2, 2)))
        self.assertEqual(lift_voxel_values([1], np.array([], dtype=int)).shape, (0,))

    def test_rejects_invalid_mapping(self):
        for mapping in ([-2], [2], [1.0], [True], [[0]], np.array([2**63], dtype=np.uint64)):
            with self.subTest(mapping=mapping), self.assertRaises(PointCloudError):
                lift_voxel_values([7, 42], mapping)

    def test_rejects_invalid_payloads(self):
        for values in (1, ['a'], [1j], [object()], [[1], [1, 2]]):
            with self.subTest(values=values), self.assertRaises(PointCloudError):
                lift_voxel_values(values, [0])

    def test_rejects_fill_truncation_and_overflow(self):
        cases = [(np.array([1], dtype=np.uint8), -1), (np.array([1], dtype=np.int8), 128),
                 (np.array([1], dtype=np.int64), 1.5), (np.array([1], dtype=np.int64), np.nan),
                 (np.array([1], dtype=np.float32), 1e100), (np.array([True]), -1),
                 (np.array([1.0]), [0]), (np.array([1.0]), 1j)]
        for values, fill in cases:
            with self.subTest(values=values, fill=fill), self.assertRaises(PointCloudError):
                lift_voxel_values(values, [-1], fill_value=fill)


if __name__ == '__main__':
    unittest.main()
