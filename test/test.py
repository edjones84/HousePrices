from unittest import TestCase

from src.api import postcode_to_region
import os

##TODO add way more and get better coverage
class Test(TestCase):
    def test_london_postcode_to_region(self):
        region = postcode_to_region("W42BE")
        self.assertEqual("london", region)

    def test_somerset_postcode_to_region(self):
        region = postcode_to_region("BS82TU")
        self.assertEqual("somerset", region)
