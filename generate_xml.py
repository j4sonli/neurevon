import numpy as np
from settings import get_settings

N_OBJECTS, BALL_SIZE, BOX_SIZE, XML_PATH = get_settings()

def arr_to_spaced(arr):
    return ' '.join(str(x) for x in arr)

XML = '<mujoco>\n\t<option gravity="0 0 0"/>\n\t<worldbody>\n'

box_face_pos = [[BOX_SIZE/2, BOX_SIZE/2, 0,],
                [BOX_SIZE/2, BOX_SIZE/2, BOX_SIZE],
                [0, BOX_SIZE/2, BOX_SIZE/2],
                [BOX_SIZE/2, 0, BOX_SIZE/2],
                [BOX_SIZE, BOX_SIZE/2, BOX_SIZE/2],
                [BOX_SIZE/2, BOX_SIZE, BOX_SIZE/2]]
box_face_orientations = [np.array([0, 0, 1, 0]),
                         np.array([1, 0, 0, 180]),
                         np.array([0, 1, 0, 90]),
                         np.array([1, 0, 0, -90]),
                         np.array([0, 1, 0, -90]),
                         np.array([1, 0, 0, 90])]
for face, ori in zip(box_face_pos, box_face_orientations):
    XML += '\t\t<body pos="{}">\n'.format(arr_to_spaced(face)) +\
           '\t\t\t<geom type="plane" size="{} {} 0.1" axisangle="{}" rgba="1 1 1 0.3"/>\n'\
               .format(BOX_SIZE/2, BOX_SIZE/2, arr_to_spaced(ori)) +\
           '\t\t</body>\n'

XML += '\n'

coords = (np.random.rand(N_OBJECTS, 3)-0.5) * BOX_SIZE/2 + BOX_SIZE/2
for i in range(N_OBJECTS):
    XML += '\t\t<body pos="{}">\n'.format(arr_to_spaced(coords[i])) +\
           '\t\t\t<joint type="free"/>\n' \
           '\t\t\t<geom type="sphere" size="{} {} {}" rgba="0 .9 0 1"/>\n'.format(BALL_SIZE, BALL_SIZE, BALL_SIZE) +\
           '\t\t</body>\n'
    XML += '\n'

XML += '\t</worldbody>\n</mujoco>'


def generate_XML_file():
    with open(XML_PATH, 'w') as f:
        f.write(XML)
