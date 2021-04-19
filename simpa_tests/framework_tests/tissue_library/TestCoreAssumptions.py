# The MIT License (MIT)
#
# Copyright (c) 2021 Computer Assisted Medical Interventions Group, DKFZ
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated simpa_documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
from simpa.utils import TISSUE_LIBRARY
from simpa.utils.libraries.tissue_library import TissueLibrary
from simpa.utils.libraries.molecule_library import MolecularComposition
import inspect


class TestCoreAssumptions(unittest.TestCase):

    def test_volume_fractions_sum_to_less_or_equal_one(self):
        for (method_name, method) in self.get_all_tissue_library_methods():
            total_volume_fraction = 0
            for molecule in method(TISSUE_LIBRARY):
                total_volume_fraction += molecule.volume_fraction
            self.assertLessEqual(total_volume_fraction, 1.0, f"Volume fraction was greater than 1.0 for {method_name}")

    @staticmethod
    def get_all_tissue_library_methods():
        methods = []
        for method in inspect.getmembers(TissueLibrary, predicate=inspect.isfunction):
            if isinstance(method[1](TISSUE_LIBRARY), MolecularComposition):
                methods.append(method)
        return methods