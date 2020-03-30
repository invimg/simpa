from simulate import Tags
from simulate.simulation import simulate
from simulate.structures import create_random_structures

import numpy as np

spacings = [0.8, 0.4, 0.2, 0.1]
photons = [5e6, 1e7, 5e7, 1e8]

seed_index = 0
while seed_index < 450:
    random_seed = 78000 + seed_index
    seed_index += 1

    for [spacing, num_photons] in zip(spacings, photons):
        np.random.seed(random_seed)
        wavelength = np.random.randint(700, 950)
        print("Wavelength: ", wavelength)

        print(np.random.random())

        settings = {
            Tags.WAVELENGTHS: [wavelength],
            Tags.RANDOM_SEED: random_seed,
            Tags.VOLUME_NAME: "Structure_"+str(random_seed).zfill(7)+"/spacing_"+str(spacing),
            Tags.SIMULATION_PATH: "/home/kris/hard_drive/data/upsampling_data",
            Tags.RUN_OPTICAL_MODEL: True,
            Tags.OPTICAL_MODEL_NUMBER_PHOTONS: num_photons,
            Tags.OPTICAL_MODEL_BINARY_PATH: "/home/kris/hard_drive/mcx_test/mcx",
            Tags.OPTICAL_MODEL: Tags.MODEL_MCX,
            Tags.RUN_ACOUSTIC_MODEL: False,
            Tags.SIMULATION_EXTRACT_FIELD_OF_VIEW: True,
            Tags.SPACING_MM: spacing,
            Tags.DIM_VOLUME_Z_MM: 21,
            Tags.DIM_VOLUME_X_MM: 40,
            Tags.DIM_VOLUME_Y_MM: 25,
            Tags.AIR_LAYER_HEIGHT_MM: 12,
            Tags.GELPAD_LAYER_HEIGHT_MM: 18,
            Tags.STRUCTURES: create_random_structures()
        }
        print("Simulating ", random_seed)
        [settings_path, optical_path, acoustic_path] = simulate(settings)
        print("Simulating ", random_seed, "[Done]")