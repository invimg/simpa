# SPDX-FileCopyrightText: 2021 Division of Intelligent Medical Systems, DKFZ
# SPDX-FileCopyrightText: 2021 Janek Groehl
# SPDX-License-Identifier: MIT

from simpa.core.simulation_modules.reconstruction_module.reconstruction_utils import compute_image_dimensions
from simpa.utils import Tags, Settings, round_x5_away_from_zero
from simpa.utils.constants import property_tags, wavelength_independent_properties, toolkit_tags
from simpa.io_handling import load_data_field, save_data_field
from simpa.core.processing_components import ProcessingComponentBase
from simpa.core.device_digital_twins import DigitalDeviceTwinBase, PhotoacousticDevice
import numpy as np


class FieldOfViewCropping(ProcessingComponentBase):

    def __init__(self, global_settings, settings_key=None):
        if settings_key is None:
            global_settings["FieldOfViewCropping"] = Settings({
                Tags.DATA_FIELD: property_tags + toolkit_tags
                + [Tags.DATA_FIELD_FLUENCE, Tags.DATA_FIELD_INITIAL_PRESSURE]})
        super(FieldOfViewCropping, self).__init__(global_settings, "FieldOfViewCropping")
    """
    Applies Gaussian noise to the defined data field.
    The noise will be applied to all wavelengths.
    Component Settings
       **Tags.DATA_FIELD required
    """

    def run(self, device: DigitalDeviceTwinBase):
        self.logger.info("Cropping field of view...")

        if Tags.DATA_FIELD not in self.component_settings.keys():
            msg = f"The field {Tags.DATA_FIELD} must be set in order to use the fov cropping."
            self.logger.critical(msg)
            raise KeyError(msg)

        if not isinstance(self.component_settings[Tags.DATA_FIELD], list):
            msg = f"The field {Tags.DATA_FIELD} must be of type list."
            self.logger.critical(msg)
            raise TypeError(msg)

        data_fields = self.component_settings[Tags.DATA_FIELD]

        if isinstance(device, PhotoacousticDevice):
            field_of_view_mm = device.detection_geometry.get_field_of_view_mm()
        else:
            field_of_view_mm = device.get_field_of_view_mm()
        self.logger.debug(f"FOV (mm): {field_of_view_mm}")
        _, _, _, xdim_start, xdim_end,  ydim_start, ydim_end, zdim_start, zdim_end = compute_image_dimensions(
            field_of_view_mm, self.global_settings[Tags.SPACING_MM], self.logger)
        field_of_view_voxels = [xdim_start, xdim_end, zdim_start, zdim_end, ydim_start, ydim_end]  # change ordering
        field_of_view_voxels = [int(dim) for dim in field_of_view_voxels]  # cast to int
        self.logger.debug(f"FOV (voxels): {field_of_view_voxels}")

        # In case it should be cropped from A to A, then crop from A to A+1
        x_offset_correct = 1 if (field_of_view_voxels[1] - field_of_view_voxels[0]) < 1 else 0
        y_offset_correct = 1 if (field_of_view_voxels[3] - field_of_view_voxels[2]) < 1 else 0
        z_offset_correct = 1 if (field_of_view_voxels[5] - field_of_view_voxels[4]) < 1 else 0

        self.logger.debug(f"field of view to crop: {field_of_view_voxels}")

        wavelength = self.global_settings[Tags.WAVELENGTH]

        for data_field in data_fields:
            # Crop wavelength-independent properties only in the last wavelength run
            if (data_field in wavelength_independent_properties
                    and wavelength != self.global_settings[Tags.WAVELENGTHS][-1]):
                continue
            try:
                self.logger.debug(f"Cropping data field {data_field}...")
                data_array = load_data_field(self.global_settings[Tags.SIMPA_OUTPUT_FILE_PATH], data_field, wavelength)

                self.logger.debug(f"data array shape before cropping: {np.shape(data_array)}")
                self.logger.debug(f"data array shape len: {len(np.shape(data_array))}")
            except KeyError:
                continue

            # input validation
            if not isinstance(data_array, np.ndarray):
                self.logger.warning(f"The data field {data_field} was not of type np.ndarray. Skipping...")
                continue
            data_field_shape = np.shape(data_array)
            if len(data_field_shape) == 3:
                if ((np.array([field_of_view_voxels[1] - field_of_view_voxels[0],
                              field_of_view_voxels[3] - field_of_view_voxels[2],
                              field_of_view_voxels[5] - field_of_view_voxels[4]]) - data_field_shape) == 0).all():
                    self.logger.warning(f"The data field {data_field} is already cropped. Skipping...")
                    continue

                # crop
                data_array = np.squeeze(data_array[field_of_view_voxels[0]:field_of_view_voxels[1] + x_offset_correct,
                                        field_of_view_voxels[2]:field_of_view_voxels[3] + y_offset_correct,
                                        field_of_view_voxels[4]:field_of_view_voxels[5] + z_offset_correct])

            elif len(data_field_shape) == 2:
                # Assumption that the data field is already in 2D shape in the y-plane
                if (np.array([field_of_view_voxels[1] - field_of_view_voxels[0],
                              field_of_view_voxels[5] - field_of_view_voxels[4]]) - data_field_shape == 0).all():
                    self.logger.warning(f"The data field {data_field} is already cropped. Skipping...")
                    continue

                # crop
                data_array = np.squeeze(data_array[field_of_view_voxels[0]:field_of_view_voxels[1] + x_offset_correct,
                                        field_of_view_voxels[4]:field_of_view_voxels[5] + z_offset_correct])

            self.logger.debug(f"data array shape after cropping: {np.shape(data_array)}")
            # save
            save_data_field(data_array, self.global_settings[Tags.SIMPA_OUTPUT_FILE_PATH], data_field, wavelength)

        self.logger.info("Cropping field of view...[Done]")
