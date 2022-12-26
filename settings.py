import numpy as np

N_OBJECTS = 100
BALL_SIZE = 0.2  # m
BOX_SIZE = 10  # m
XML_PATH = 'neurevon.xml'
CHARGES = np.random.choice([-2, -1, 0, 1, 2], p=[0.1, 0.1, 0.6, 0.1, 0.1], size=N_OBJECTS).astype('float64')  # C
CHARGES -= CHARGES

MASSES = np.zeros(N_OBJECTS) + 1  # kg

VALENCE_E = np.random.choice([1, 4, 5, 6, 7], p=[0.6, 0.1, 0.1, 0.1, 0.1], size=N_OBJECTS)
VALENCE_E_CAP = np.array([2 if ve == 1 else 8 for ve in VALENCE_E])


def electronegativity(valence_e):
    if valence_e == 1:
        return 3.5
    return valence_e
ELECTRONEG = np.array([electronegativity(ve) for ve in VALENCE_E])


def get_settings():
    return N_OBJECTS, BALL_SIZE, BOX_SIZE, XML_PATH, \
           MASSES, CHARGES, VALENCE_E, VALENCE_E_CAP, ELECTRONEG