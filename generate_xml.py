import numpy as np
from settings import get_settings

N_OBJECTS, BALL_SIZE, BOX_SIZE, XML_PATH, \
MASSES, CHARGES, VALENCE_E, VALENCE_E_CAP, ELECTRONEG = get_settings()

def arr_to_spaced(arr):
    return ' '.join(str(x) for x in arr)

def charge_color(charge):
    max_charge, min_charge = np.max(CHARGES), np.min(CHARGES)
    if max_charge == 0 and min_charge == 0:
        max_charge, min_charge = 1, -1
    rel_charge = (charge - min_charge) / (max_charge - min_charge)
    return np.array([rel_charge, 0, 1-rel_charge, 1])

XML = '<mujoco>\n'

XML += '\t<option gravity="0 0 0" timestep="0.007"/>\n'

XML += '\t<worldbody>\n'

box_face_pos = [[BOX_SIZE/2, BOX_SIZE/2, 0],
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
for i, (face, ori) in enumerate(zip(box_face_pos, box_face_orientations)):
    XML += '\t\t<body name="p{}" pos="{}">\n'.format(i, arr_to_spaced(face)) +\
           '\t\t\t<geom type="plane" size="{} {} 0.1" axisangle="{}" rgba="1 1 1 0.3"/>\n'\
               .format(BOX_SIZE/2, BOX_SIZE/2, arr_to_spaced(ori)) +\
           '\t\t</body>\n'

XML += '\n'

coords = np.random.rand(N_OBJECTS, 3) * (BOX_SIZE - BALL_SIZE) + BALL_SIZE
charge_colors = [charge_color(charge) for charge in CHARGES]
for i in range(N_OBJECTS):
    XML += '\t\t<body name="{}" pos="{}">\n'.format(i, arr_to_spaced(coords[i])) +\
           '\t\t\t<joint type="free"/>\n' \
           '\t\t\t<geom name="{}" type="sphere" mass="{}" condim="6" size="{} {} {}" rgba="{}"/>\n'.format(i, MASSES[i], BALL_SIZE, BALL_SIZE, BALL_SIZE, arr_to_spaced(charge_colors[i])) +\
           '\t\t</body>\n'
    XML += '\n'

XML += '\t</worldbody>\n'


XML += '\t<contact>\n'

# for i in range(6):
#     for j in range(N_OBJECTS):
#         XML += '\t\t<exclude body1="p{}" body2="{}"/>'.format(i, j)
# XML += '\n'

# XML += '\t\t<pair geom1="{}" geom2="{}"/>'.format(6, 7)

XML += '\t</contact>\n'

XML += '</mujoco>'


def generate_XML_file():
    with open(XML_PATH, 'w') as f:
        f.write(XML)
