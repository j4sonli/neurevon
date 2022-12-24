import numpy as np

N_OBJECTS = 100
BALL_SIZE = 0.2
BOX_SIZE = 10
XML_PATH = 'neurevon.xml'
CHARGES = np.random.randint(-2, 3, size=N_OBJECTS) * 1.602e-19  # C


def get_settings():
    return N_OBJECTS, BALL_SIZE, BOX_SIZE, XML_PATH, CHARGES