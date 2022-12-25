import numpy as np

N_OBJECTS = 27
BALL_SIZE = 0.2
BOX_SIZE = 10
XML_PATH = 'neurevon.xml'
CHARGES = np.random.randint(-2, 3, size=N_OBJECTS) * 1.602e-19  # C
CHARGES -= CHARGES

VALENCE_E = np.random.choice([1, 4, 5, 6, 7], p=[0.6, 0.1, 0.1, 0.1, 0.1], size=N_OBJECTS)
VALENCE_E_CAP = np.array([2 if ve == 1 else 8 for ve in VALENCE_E])


def get_settings():
    return N_OBJECTS, BALL_SIZE, BOX_SIZE, XML_PATH, \
           CHARGES, VALENCE_E, VALENCE_E_CAP