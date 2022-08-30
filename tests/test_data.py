"""
Unit tests to test data loaders. These primarily check that the data loaders return values
with expected shapes and ranges.
"""

import os, sys
import unittest

import numpy as np
import torch

SRC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "protdiff")
assert os.path.isdir(SRC_DIR)
sys.path.append(SRC_DIR)
import datasets


class TestCathCanonical(unittest.TestCase):
    """
    Tests for the cath canonical angles dataset (i.e., not the trRosetta ones)
    """

    def setUp(self) -> None:
        # Setup the dataset
        self.pad = 512
        self.dset = datasets.CathCanonicalAnglesDataset(pad=self.pad)

    def test_return_keys(self):
        """Test that returned dictionary has expected keys"""
        d = self.dset[0]
        self.assertEqual(set(d.keys()), set(["angles", "position_ids", "attn_mask"]))

    def test_num_feature(self):
        """Test that we have the expected number of features"""
        d = self.dset[0]
        self.assertEqual(d["angles"].shape[1], 5)

    def test_shapes(self):
        """Test that the returned tensors have expected shapes"""
        d = self.dset[1]
        self.assertEqual(
            d["angles"].shape, (self.pad, len(self.dset.feature_names["angles"]))
        )
        self.assertEqual(d["position_ids"].shape, (self.pad,))
        self.assertEqual(d["attn_mask"].shape, (self.pad,))

    def test_angles(self):
        """Test that angles do not fall outside of -pi and pi range"""
        d = self.dset[2]
        angular_idx = np.where(self.dset.feature_is_angular["angles"])[0]
        self.assertTrue(np.all(d["angles"].numpy()[..., angular_idx] >= -np.pi))
        self.assertTrue(np.all(d["angles"].numpy()[..., angular_idx] <= np.pi))


class TestCathCanonicalAnglesOnly(unittest.TestCase):
    """
    Tests for the CATH canonical angles only dataset (i.e. no distance returned)
    """

    def setUp(self) -> None:
        self.pad = 512
        self.dset = datasets.CathCanonicalAnglesOnlyDataset(pad=self.pad)

    def test_return_keys(self):
        """Test that returned dictionary has expected keys"""
        d = self.dset[0]
        self.assertEqual(set(d.keys()), set(["angles", "position_ids", "attn_mask"]))

    def test_num_features(self):
        """Test that we return the expected number of features and have correctly removed distance"""
        d = self.dset[1]
        self.assertEqual(d["angles"].shape[1], 4)

    def test_all_angular(self):
        """Test that the dataset is all angular features and that this is properly registered"""
        self.assertTrue(all(self.dset.feature_is_angular["angles"]))

    def test_shapes(self):
        """Test that the returned tensors have expected shapes"""
        d = self.dset[1]
        self.assertEqual(
            d["angles"].shape, (self.pad, len(self.dset.feature_names["angles"]))
        )
        self.assertEqual(d["position_ids"].shape, (self.pad,))
        self.assertEqual(d["attn_mask"].shape, (self.pad,))

    def test_angular_range(self):
        """Test that the returned angles are all between -pi and pi"""
        d = self.dset[5]
        self.assertTrue(np.all(d["angles"].numpy() >= -np.pi))
        self.assertTrue(np.all(d["angles"].numpy() <= np.pi))

    def test_repeated_init(self):
        """Test that repeatedly intializing does not break anything"""
        # This can happy because of the way we define subclasses
        dset1 = datasets.CathCanonicalAnglesOnlyDataset(pad=self.pad)
        dset2 = datasets.CathCanonicalAnglesOnlyDataset(pad=self.pad)
        self.assertTrue(
            all(
                [
                    a == b
                    for a, b in zip(
                        dset1.feature_names["angles"], dset2.feature_names["angles"]
                    )
                ]
            )
        )

    def test_repeated_query(self):
        """Test that repeated query is consistent"""
        x1 = self.dset[0]
        x2 = self.dset[0]

        for k1 in x1.keys():
            v1 = x1[k1]
            v2 = x2[k1]
            self.assertTrue(torch.allclose(v1, v2))