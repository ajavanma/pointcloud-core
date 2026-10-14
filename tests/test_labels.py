import unittest

import numpy as np

from pointcloud_core import LabelMap, PointCloudError


class LabelTests(unittest.TestCase):
    def test_round_trip_uses_declared_order(self):
        mapping = LabelMap((42, 0, 7), ignore_label=255)
        source = np.array([[7, 42], [255, 0]])
        encoded = mapping.encode(source)
        np.testing.assert_array_equal(encoded, [[2, 0], [-1, 1]])
        np.testing.assert_array_equal(mapping.decode(encoded), source)
        self.assertEqual(encoded.dtype, np.dtype('int64'))
        self.assertFalse(np.shares_memory(encoded, source))

    def test_negative_original_classes_are_supported(self):
        mapping = LabelMap([-10, -1, 0], ignore_label=-99)
        self.assertEqual(mapping.class_ids, (-10, -1, 0))
        np.testing.assert_array_equal(mapping.encode([-10, -1, -99]), [0, 1, -1])

    def test_scalar_and_typed_empty_arrays(self):
        mapping = LabelMap((5,))
        self.assertEqual(mapping.encode(np.int64(5)).shape, ())
        self.assertEqual(mapping.decode(np.int64(0)).item(), 5)
        self.assertEqual(mapping.encode(np.array([], dtype=int)).shape, (0,))

    def test_rejects_invalid_label_map(self):
        for classes, ignored in (((), -1), ((1, 1), -1), ((1,), 1), ((True,), -1), ((1.0,), -1), ((2**63,), -1), ((1,), True), ((1,), 2**63), (None, -1), ('12', -1)):
            with self.subTest(classes=classes, ignored=ignored), self.assertRaises(PointCloudError):
                LabelMap(classes, ignored)

    def test_unknown_original_labels_are_rejected(self):
        with self.assertRaisesRegex(PointCloudError, 'unknown class IDs.*999'):
            LabelMap((0, 7), 255).encode([0, 999])

    def test_rejects_bad_encoded_ids(self):
        mapping = LabelMap((4, 7))
        for labels in ([-2], [2], [0.0], [True], np.array([2**63], dtype=np.uint64)):
            with self.subTest(labels=labels), self.assertRaises(PointCloudError):
                mapping.decode(labels)


if __name__ == '__main__':
    unittest.main()
