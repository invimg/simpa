# SPDX-FileCopyrightText: 2021 Computer Assisted Medical Interventions Group, DKFZ
# SPDX-FileCopyrightText: 2021 Janek Groehl
# SPDX-License-Identifier: MIT

from simpa.core.device_digital_twins import IlluminationGeometryBase
from simpa.utils import Settings, Tags


class DiskIlluminationGeometry(IlluminationGeometryBase):
    """
    This class represents a disk illumination geometry.
    The device position is defined as the middle of the disk.
    """
    def __init__(self, beam_radius_mm=None, device_position_mm=None, field_of_view_extent_mm=None):
        """
        :param beam_radius_mm: Radius of the disk in mm.
        :type beam_radius_mm: int, float
        :param device_position_mm: Each device has an internal position which serves as origin for internal \
        representations of illuminator positions.
        :type device_position_mm: ndarray
        :param field_of_view_extent_mm: Field of view which is defined as a numpy array of the shape \
        [xs, xe, ys, ye, zs, ze], where x, y, and z denote the coordinate axes and s and e denote the start and end \
        positions.
        :type field_of_view_extent_mm: ndarray
        """
        super(DiskIlluminationGeometry, self).__init__(device_position_mm=device_position_mm,
                                                       field_of_view_extent_mm=field_of_view_extent_mm)
        if beam_radius_mm is None:
            beam_radius_mm = 1

        self.beam_radius_mm = beam_radius_mm

    def get_mcx_illuminator_definition(self, global_settings: Settings, probe_position_mm) -> dict:
        source_type = Tags.ILLUMINATION_TYPE_DISK

        spacing = global_settings[Tags.SPACING_MM]

        device_position = probe_position_mm / spacing + 0.5

        source_direction = [0, 0, 1]

        source_param1 = [int(round(self.beam_radius_mm / spacing)), 0, 0, 0]

        source_param2 = [0, 0, 0, 0]

        return {
            "Type": source_type,
            "Pos": list(device_position),
            "Dir": source_direction,
            "Param1": source_param1,
            "Param2": source_param2
        }