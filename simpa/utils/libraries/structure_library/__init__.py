# SPDX-FileCopyrightText: 2021 Division of Intelligent Medical Systems, DKFZ
# SPDX-FileCopyrightText: 2021 Janek Groehl
# SPDX-License-Identifier: MIT

import traceback
import torch
from simpa.log import Logger
from simpa.utils import Settings, Tags

from simpa.utils.libraries.structure_library.BackgroundStructure import Background, \
    define_background_structure_settings
from simpa.utils.libraries.structure_library.CircularTubularStructure import CircularTubularStructure, \
    define_circular_tubular_structure_settings
from simpa.utils.libraries.structure_library.EllipticalTubularStructure import EllipticalTubularStructure, \
    define_elliptical_tubular_structure_settings
from simpa.utils.libraries.structure_library.HorizontalLayerStructure import HorizontalLayerStructure, \
    define_horizontal_layer_structure_settings
from simpa.utils.libraries.structure_library.ParallelepipedStructure import ParallelepipedStructure, \
    define_parallelepiped_structure_settings
from simpa.utils.libraries.structure_library.RectangularCuboidStructure import RectangularCuboidStructure, \
    define_rectangular_cuboid_structure_settings
from simpa.utils.libraries.structure_library.SphericalStructure import SphericalStructure, \
    define_spherical_structure_settings
from simpa.utils.libraries.structure_library.VesselStructure import VesselStructure, \
    define_vessel_structure_settings


def priority_sorted_structures(settings: Settings, volume_creator_settings: dict, volume_size: torch.Tensor):
    """
    A generator function to lazily construct structures in descending order of priority
    """
    logger = Logger()
    if not Tags.STRUCTURES in volume_creator_settings:
        logger.warning("Did not find any structure definitions in the settings file!")
        return
    sorted_structure_settings = sorted(
        [structure_setting for structure_setting in volume_creator_settings[Tags.STRUCTURES].values()],
        key=lambda s: s[Tags.PRIORITY] if Tags.PRIORITY in s else 0, reverse=True)

    for structure_setting in sorted_structure_settings:
        if structure_setting[Tags.STRUCTURE_TYPE] == Tags.HORIZONTAL_LAYER_STRUCTURE:
            for molecule in structure_setting[Tags.MOLECULE_COMPOSITION]:
                old_vol = getattr(molecule, "volume_fraction")
                if isinstance(old_vol, torch.Tensor):
                    structure_start_voxels = (torch.tensor(structure_setting[Tags.STRUCTURE_START_MM]) /
                                              settings[Tags.SPACING_MM])
                    structure_end_voxels = (torch.tensor(structure_setting[Tags.STRUCTURE_END_MM]) /
                                            settings[Tags.SPACING_MM])
                    structure_size = structure_end_voxels - structure_start_voxels
                    if volume_size[2] != old_vol.shape[2]:
                        if (volume_size[2] == structure_size[2]).any:
                            pad_start = structure_start_voxels.flip(dims=[0])
                            pad_end = (volume_size - structure_end_voxels).flip(dims=[0])
                            for count, structure_end in enumerate(structure_end_voxels):
                                if structure_end == 0:
                                    pad_end[2 - count] = 0
                            if (pad_start > 1e-6).any() or (pad_end > 1e-6).any():
                                padding_list = torch.flatten(torch.stack((pad_start, pad_end), 1)).tolist()
                                padding = tuple(map(int, padding_list))
                                padded_vol = torch.nn.functional.pad(old_vol, padding, mode='constant', value=0)
                                setattr(molecule, "volume_fraction", padded_vol)
                        else:
                            logger.critical("Tensor does not have the same dimensionality as the area it should fill" +
                                            "{} or the dimensions of the entire ".format(old_vol.shape) +
                                            "simulation volume{}! Please change this.".format(volume_size.shape))

        try:
            structure_class = globals()[structure_setting[Tags.STRUCTURE_TYPE]]
            yield structure_class(settings, structure_setting)
            torch.cuda.empty_cache()
        except Exception as e:
            logger.critical("An exception has occurred while trying to parse " +
                            str(structure_setting[Tags.STRUCTURE_TYPE]) +
                            " from the dictionary.")
            logger.critical("The structure type was " + str(structure_setting[Tags.STRUCTURE_TYPE]))
            logger.critical(traceback.format_exc())
            logger.critical("trying to continue as normal...")
            raise e
