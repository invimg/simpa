# The MIT License (MIT)
#
# Copyright (c) 2018 Computer Assisted Medical Interventions Group, DKFZ
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

import matplotlib.pyplot as plt
from simpa.utils import Tags
from scipy.interpolate import interp2d
from scipy.ndimage import gaussian_filter
import numpy as np


def create_deformation_settings(bounds_mm, maximum_z_elevation_mm=1, filter_sigma=1, cosine_scaling_factor=4):
    """
    FIXME
    """
    deformation_settings = dict()
    maximum_z_elevation_mm = -maximum_z_elevation_mm

    number_of_boundary_points = np.random.randint(4, 6, size=2)
    surface_elevations = np.random.random(size=(number_of_boundary_points[0],
                                                number_of_boundary_points[1]))
    surface_elevations = gaussian_filter(surface_elevations, sigma=filter_sigma)
    surface_elevations = surface_elevations / np.max(surface_elevations)

    x_positions_vector = np.linspace(bounds_mm[0][0], bounds_mm[0][1], number_of_boundary_points[0])
    y_positions_vector = np.linspace(bounds_mm[1][0], bounds_mm[1][1], number_of_boundary_points[1])

    xx, yy = np.meshgrid(x_positions_vector, y_positions_vector, indexing='ij')

    # Add random permutations to the y-axis of the division knots
    for x_idx, x_position in enumerate(x_positions_vector):
        for y_idx, y_position in enumerate(y_positions_vector):
            scaling_value = (np.cos(x_position / (bounds_mm[0][1] * (cosine_scaling_factor / np.pi)) -
                                    np.pi/(cosine_scaling_factor * 2)) ** 2 *
                             np.cos(y_position / (bounds_mm[1][1] * (cosine_scaling_factor / np.pi)) -
                                    np.pi/(cosine_scaling_factor * 2)) ** 2)

            surface_elevations[x_idx, y_idx] = scaling_value * surface_elevations[x_idx, y_idx]

    # This rescales and sets the maximum to 0.
    surface_elevations *= maximum_z_elevation_mm
    surface_elevations = surface_elevations - np.max(surface_elevations)

    deformation_settings[Tags.DEFORMATION_X_COORDINATES_MM] = xx
    deformation_settings[Tags.DEFORMATION_Y_COORDINATES_MM] = yy
    deformation_settings[Tags.DEFORMATION_Z_ELEVATIONS_MM] = surface_elevations

    return deformation_settings


def get_functional_from_deformation_settings(deformation_settings: dict):
    """
    FIXME
    """

    if Tags.DEFORMATION_X_COORDINATES_MM not in deformation_settings:
        raise KeyError("x coordinates not defined in deformation settings")
    if Tags.DEFORMATION_Y_COORDINATES_MM not in deformation_settings:
        raise KeyError("y coordinates not defined in deformation settings")
    if Tags.DEFORMATION_Z_ELEVATIONS_MM not in deformation_settings:
        raise KeyError("z elevations not defined in deformation settings")

    x_coordinates_mm = deformation_settings[Tags.DEFORMATION_X_COORDINATES_MM]
    y_coordinates_mm = deformation_settings[Tags.DEFORMATION_Y_COORDINATES_MM]
    z_elevations_mm = deformation_settings[Tags.DEFORMATION_Z_ELEVATIONS_MM]
    order = "cubic"

    functional_mm = interp2d(x_coordinates_mm, y_coordinates_mm, z_elevations_mm, kind=order)
    return functional_mm


if __name__ == "__main__":
    x_bounds = [0, 9]
    y_bounds = [0, 9]
    settings = create_deformation_settings([x_bounds, y_bounds], filter_sigma=1, cosine_scaling_factor=4)
    functional = get_functional_from_deformation_settings(settings)

    x_positions_vector = np.linspace(x_bounds[0], x_bounds[1], 100)
    y_positions_vector = np.linspace(y_bounds[0], y_bounds[1], 100)

    xx, yy = np.meshgrid(x_positions_vector, y_positions_vector, indexing='ij')

    values = functional(x_positions_vector, y_positions_vector)

    plt3d = plt.figure().gca(projection='3d')
    plt3d.plot_surface(xx, yy, values, cmap="viridis")
    plt3d.set_zlim(0, -1)
    plt.show()
