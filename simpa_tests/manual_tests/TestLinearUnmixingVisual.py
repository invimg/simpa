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

from simpa.utils import Tags, TISSUE_LIBRARY
from simpa.core.simulation import simulate
from simpa.algorithms.multispectral import linear_unmixing as lu
import numpy as np
from simpa.core import *
from simpa.utils.path_manager import PathManager
from simpa.io_handling import load_data_field
import matplotlib.pyplot as plt
from simpa.log import Logger
import os
from simpa.core.device_digital_twins import PencilBeamIlluminationGeometry


class TestLinearUnmixingVisual:

    def setup(self):

        self.logger = Logger()
        # TODO: Please make sure that a valid path_config.env file is located in your home directory, or that you
        #  point to the correct file in the PathManager().
        self.path_manager = PathManager()

        RANDOM_SEED = 471
        self.VISUAL_WAVELENGTHS = [750, 800, 850]
        np.random.seed(RANDOM_SEED)

        # Initialize global settings and prepare for simulation pipeline including
        # volume creation and optical forward simulation
        general_settings = {
            Tags.RANDOM_SEED: RANDOM_SEED,
            Tags.VOLUME_NAME: "LinearUnmixingManualTest_" + str(RANDOM_SEED),
            Tags.SIMULATION_PATH: self.path_manager.get_hdf5_file_save_path(),
            Tags.SPACING_MM: 2,
            Tags.DIM_VOLUME_Z_MM: 60,
            Tags.DIM_VOLUME_X_MM: 60,
            Tags.DIM_VOLUME_Y_MM: 30,
            Tags.WAVELENGTHS: self.VISUAL_WAVELENGTHS
        }
        self.settings = Settings(general_settings)
        self.settings.set_volume_creation_settings({
            Tags.SIMULATE_DEFORMED_LAYERS: True,
            Tags.STRUCTURES: self.create_example_tissue()
        })

        # Set component settings for linear unmixing.
        # Performs linear spectral unmixing on the defined data field.
        self.settings["linear_unmixing"] = {
            Tags.DATA_FIELD: Tags.PROPERTY_ABSORPTION_PER_CM,
            Tags.LINEAR_UNMIXING_OXYHEMOGLOBIN: self.VISUAL_WAVELENGTHS,
            Tags.LINEAR_UNMIXING_DEOXYHEMOGLOBIN: self.VISUAL_WAVELENGTHS,
            Tags.LINEAR_UNMIXING_COMPUTE_SO2: True
        }

        self.device = PencilBeamIlluminationGeometry()

        # Run simulation pipeline for all wavelengths in Tag.WAVELENGTHS
        pipeline = [
            VolumeCreationModelModelBasedAdapter(self.settings)
        ]
        simulate(pipeline, self.settings, self.device)

        # Run linear unmixing component with above specified settings
        lu.LinearUnmixingProcessingComponent(self.settings, "linear_unmixing").run(self.device)

    def perform_test(self):

        self.logger.info("Performing visual linear unmixing test...")

        lu_results = load_data_field(self.settings[Tags.SIMPA_OUTPUT_PATH], Tags.LINEAR_UNMIXING_RESULT)
        sO2 = lu_results["sO2"]

        mua = load_data_field(self.settings[Tags.SIMPA_OUTPUT_PATH], Tags.PROPERTY_ABSORPTION_PER_CM,
                              wavelength=self.VISUAL_WAVELENGTHS[0])

        y_dim = int(mua.shape[1] / 2)
        plt.figure(figsize=(15, 15))
        plt.suptitle("Linear Unmixing - Visual Test")
        plt.subplot(121)
        plt.title("Absorption coefficients")
        plt.imshow(np.rot90(mua[:, y_dim, :], -1))
        plt.colorbar(fraction=0.05)
        plt.subplot(122)
        plt.title("Blood oxygen saturation")
        plt.imshow(np.rot90(sO2[:, y_dim, :], -1))
        plt.colorbar(fraction=0.05)
        plt.show()

        # clean up files after test
        os.remove(self.settings[Tags.SIMPA_OUTPUT_PATH])

    def create_example_tissue(self):
        """
        This is a very simple example script of how to create a tissue definition.
        It contains a muscular background, an epidermis layer on top of the muscles
        and a blood vessel.
        """
        background_dictionary = Settings()
        background_dictionary[Tags.MOLECULE_COMPOSITION] = TISSUE_LIBRARY.constant(1e-4, 1e-4, 0.9)
        background_dictionary[Tags.STRUCTURE_TYPE] = Tags.BACKGROUND

        muscle_dictionary = Settings()
        muscle_dictionary[Tags.PRIORITY] = 1
        muscle_dictionary[Tags.STRUCTURE_START_MM] = [0, 0, 10]
        muscle_dictionary[Tags.STRUCTURE_END_MM] = [0, 0, 100]
        muscle_dictionary[Tags.MOLECULE_COMPOSITION] = TISSUE_LIBRARY.muscle()
        muscle_dictionary[Tags.CONSIDER_PARTIAL_VOLUME] = True
        muscle_dictionary[Tags.ADHERE_TO_DEFORMATION] = True
        muscle_dictionary[Tags.STRUCTURE_TYPE] = Tags.HORIZONTAL_LAYER_STRUCTURE

        vessel_1_dictionary = Settings()
        vessel_1_dictionary[Tags.PRIORITY] = 3
        vessel_1_dictionary[Tags.STRUCTURE_START_MM] = [self.settings[Tags.DIM_VOLUME_X_MM] / 2,
                                                        10,
                                                        self.settings[Tags.DIM_VOLUME_Z_MM] / 2]
        vessel_1_dictionary[Tags.STRUCTURE_END_MM] = [self.settings[Tags.DIM_VOLUME_X_MM] / 2,
                                                      12,
                                                      self.settings[Tags.DIM_VOLUME_Z_MM] / 2]
        vessel_1_dictionary[Tags.STRUCTURE_RADIUS_MM] = 3
        vessel_1_dictionary[Tags.MOLECULE_COMPOSITION] = TISSUE_LIBRARY.blood(oxygenation=0.99)
        vessel_1_dictionary[Tags.CONSIDER_PARTIAL_VOLUME] = True
        vessel_1_dictionary[Tags.STRUCTURE_TYPE] = Tags.CIRCULAR_TUBULAR_STRUCTURE

        epidermis_dictionary = Settings()
        epidermis_dictionary[Tags.PRIORITY] = 8
        epidermis_dictionary[Tags.STRUCTURE_START_MM] = [0, 0, 9]
        epidermis_dictionary[Tags.STRUCTURE_END_MM] = [0, 0, 10]
        epidermis_dictionary[Tags.MOLECULE_COMPOSITION] = TISSUE_LIBRARY.epidermis()
        epidermis_dictionary[Tags.CONSIDER_PARTIAL_VOLUME] = True
        epidermis_dictionary[Tags.ADHERE_TO_DEFORMATION] = True
        epidermis_dictionary[Tags.STRUCTURE_TYPE] = Tags.HORIZONTAL_LAYER_STRUCTURE

        tissue_dict = Settings()
        tissue_dict[Tags.BACKGROUND] = background_dictionary
        tissue_dict["muscle"] = muscle_dictionary
        tissue_dict["epidermis"] = epidermis_dictionary
        tissue_dict["vessel_1"] = vessel_1_dictionary
        return tissue_dict


if __name__ == '__main__':
    test = TestLinearUnmixingVisual()
    test.setup()
    test.perform_test()
