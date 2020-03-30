from simulate import Tags
from simulate.simulation import simulate
from simulate.structures import create_random_structures

import numpy as np

seed_index = 0
while seed_index < 1:
    random_seed = 1000 + seed_index
    seed_index += 1
    np.random.seed(random_seed)

    relative_shift = ((np.random.random() - 0.5) * 2) * 12.5
    background_oxy = (np.random.random() * 0.6) + 0.2

    wavelength = np.random.randint(700, 950)
    print("Wavelength: ", wavelength)

    print(np.random.random())

    settings = {
        Tags.WAVELENGTHS: [wavelength],
        Tags.RANDOM_SEED: random_seed,
        Tags.VOLUME_NAME: "Structure_"+str(random_seed).zfill(6),
        Tags.SIMULATION_PATH: "/home/janek/simulation_test/",
        Tags.RUN_OPTICAL_MODEL: True,
        Tags.OPTICAL_MODEL_NUMBER_PHOTONS: 1e8,
        Tags.OPTICAL_MODEL_BINARY_PATH: "/home/janek/simulation_test/mcx",
        Tags.OPTICAL_MODEL: Tags.MODEL_MCX,
        Tags.RUN_ACOUSTIC_MODEL: False,
        Tags.SPACING_MM: 0.15,
        Tags.SIMULATION_EXTRACT_FIELD_OF_VIEW: True,
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