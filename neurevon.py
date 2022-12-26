import mujoco as mj
from mujoco.glfw import glfw
import numpy as np
from settings import get_settings
from generate_xml import generate_XML_file

N_OBJECTS, BALL_SIZE, BOX_SIZE, XML_PATH, \
MASSES, CHARGES, VALENCE_E, VALENCE_E_CAP, ELECTRONEG = get_settings()

generate_XML_file()

sim_time = 180  # seconds
print_camera_config = 0  # set to 1 to print camera config

k_e = 10  # N m^2 C^(-2)
EFF_VALENCE_E = VALENCE_E.copy()
COVALENT_FORCE = 1e4  # N
COVALENT_BONDS_adj = {}
COVALENT_BONDS_edge = []
VSEPR_FORCE = COVALENT_FORCE / 5  # N

FREE_SWIMMING_FORCE = 1e2  # N


def charge_color(charge):
    max_charge, min_charge = 1, -1
    rel_charge = (charge - min_charge) / (max_charge - min_charge)
    return np.array([rel_charge, 0, 1-rel_charge, 1])


def add_covalent_bond(i1, i2):
    COVALENT_BONDS_edge.append((i1, i2))
    COVALENT_BONDS_adj.setdefault(i1, []).append(i2)
    COVALENT_BONDS_adj.setdefault(i2, []).append(i1)


def init_controller(model, data):
    # data.qvel[:] = (np.random.rand(N_OBJECTS * 6) - 0.5) * 60
    pass


def controller(model, data):
    ## Coulomb force
    coulomb_forces = np.zeros((N_OBJECTS, 3))
    for i in range(N_OBJECTS):
        if CHARGES[i] == 0:
            continue
        for j in range(i + 1, N_OBJECTS):
            if CHARGES[j] == 0:
                continue
            v = data.xpos[i + 7] - data.xpos[j + 7]
            r = np.linalg.norm(v)
            force = k_e * CHARGES[i] * CHARGES[j] / r ** 2
            coulomb_forces[i] += force * v / r
            coulomb_forces[j] += force * -v / r
    # accels = coulomb_forces / masses.reshape(-1, 1)
    for i in range(N_OBJECTS):
        data.xfrc_applied[i + 7][:3] = coulomb_forces[i]

    ## Covalent bonding
    for i1, i2 in zip(data.contact.geom1, data.contact.geom2):
        i1, i2 = i1 - 6, i2 - 6
        if i1 < 0 or i2 < 0:
            continue
        if i1 in COVALENT_BONDS_adj and i2 in COVALENT_BONDS_adj[i1]:
            continue
        if EFF_VALENCE_E[i1] < VALENCE_E_CAP[i1] and EFF_VALENCE_E[i2] < VALENCE_E_CAP[i2]:
            e_to_share = min(VALENCE_E_CAP[i1] - EFF_VALENCE_E[i1], VALENCE_E_CAP[i2] - EFF_VALENCE_E[i2])
            EFF_VALENCE_E[i1] += e_to_share
            EFF_VALENCE_E[i2] += e_to_share
            add_covalent_bond(i1, i2)
            ## add partial charge
            i1_pref = (ELECTRONEG[i1] - ELECTRONEG[i2]) / 8
            CHARGES[i1] -= i1_pref
            CHARGES[i2] += i1_pref
            model.geom_rgba[i1 + 6] = charge_color(CHARGES[i1])
            model.geom_rgba[i2 + 6] = charge_color(CHARGES[i2])
    ## attractive covalent force
    for i1, i2 in COVALENT_BONDS_edge:
        v = data.xpos[i1 + 7] - data.xpos[i2 + 7]
        data.xfrc_applied[i1 + 7][:3] += -v * COVALENT_FORCE
        data.xfrc_applied[i2 + 7][:3] += v * COVALENT_FORCE
    ## repulsive force around covalent bonds
    for _, adj in COVALENT_BONDS_adj.items():
        for i in range(len(adj)):
            for j in range(i + 1, len(adj)):
                v = data.xpos[adj[i] + 7] - data.xpos[adj[j] + 7]
                data.xfrc_applied[adj[i] + 7][:3] += v * VSEPR_FORCE
                data.xfrc_applied[adj[j] + 7][:3] += -v * VSEPR_FORCE

    ## unbonded atoms keep moving
    for i in range(N_OBJECTS):
        if i not in COVALENT_BONDS_adj.keys():
            data.xfrc_applied[i + 7][:3] += (np.random.rand(3) - 0.5) * FREE_SWIMMING_FORCE


########################################################################################################################
# For callback functions
button_left = False
button_middle = False
button_right = False
lastx = 0
lasty = 0


def keyboard(window, key, scancode, act, mods):
    if act == glfw.PRESS and key == glfw.KEY_BACKSPACE:
        mj.mj_resetData(model, data)
        mj.mj_forward(model, data)


def mouse_button(window, button, act, mods):
    # update button state
    global button_left
    global button_middle
    global button_right

    button_left = (glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS)
    button_middle = (glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_MIDDLE) == glfw.PRESS)
    button_right = (glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS)

    # update mouse position
    glfw.get_cursor_pos(window)


def mouse_move(window, xpos, ypos):
    # compute mouse displacement, save
    global lastx
    global lasty
    global button_left
    global button_middle
    global button_right

    dx = xpos - lastx
    dy = ypos - lasty
    lastx = xpos
    lasty = ypos

    # no buttons down: nothing to do
    if not button_left and not button_middle and not button_right:
        return

    # get current window size
    width, height = glfw.get_window_size(window)

    # get shift key state
    PRESS_LEFT_SHIFT = glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
    PRESS_RIGHT_SHIFT = glfw.get_key(window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS
    mod_shift = (PRESS_LEFT_SHIFT or PRESS_RIGHT_SHIFT)

    # determine action based on mouse button
    if button_right:
        if mod_shift:
            action = mj.mjtMouse.mjMOUSE_MOVE_H
        else:
            action = mj.mjtMouse.mjMOUSE_MOVE_V
    elif button_left:
        if mod_shift:
            action = mj.mjtMouse.mjMOUSE_ROTATE_H
        else:
            action = mj.mjtMouse.mjMOUSE_ROTATE_V
    else:
        action = mj.mjtMouse.mjMOUSE_ZOOM

    mj.mjv_moveCamera(model, action, dx / height, dy / height, scene, cam)


def scroll(window, xoffset, yoffset):
    action = mj.mjtMouse.mjMOUSE_ZOOM
    mj.mjv_moveCamera(model, action, 0.0, -0.05 * yoffset, scene, cam)


model = mj.MjModel.from_xml_path(XML_PATH)
data = mj.MjData(model)
cam = mj.MjvCamera()
opt = mj.MjvOption()

glfw.init()
window = glfw.create_window(1200, 900, 'Demo', None, None)
glfw.make_context_current(window)
glfw.swap_interval(1)

mj.mjv_defaultCamera(cam)
mj.mjv_defaultOption(opt)
scene = mj.MjvScene(model, maxgeom=10000)
context = mj.MjrContext(model, mj.mjtFontScale.mjFONTSCALE_150.value)

glfw.set_key_callback(window, keyboard)
glfw.set_cursor_pos_callback(window, mouse_move)
glfw.set_mouse_button_callback(window, mouse_button)
glfw.set_scroll_callback(window, scroll)

cam.azimuth = -135
cam.elevation = -45
cam.distance = 25
cam.lookat = np.array([BOX_SIZE / 2, BOX_SIZE / 2, BOX_SIZE / 2])

########################################################################################################################

init_controller(model, data)
mj.set_mjcb_control(controller)

while not glfw.window_should_close(window):
    time_prev = data.time

    while data.time - time_prev < 1 / 60:
        mj.mj_step(model, data)

    if data.time >= sim_time:
        break

    # get framebuffer viewport
    viewport_width, viewport_height = glfw.get_framebuffer_size(window)
    viewport = mj.MjrRect(0, 0, viewport_width, viewport_height)

    if print_camera_config == 1:
        print('cam.azimuth =', cam.azimuth, '; cam.elevation =', cam.elevation, '; cam.distance =', cam.distance)
        print('cam.lookat = np.array([', cam.lookat[0], ',', cam.lookat[1], ',', cam.lookat[2], '])')

    # Update scene and render
    mj.mjv_updateScene(model, data, opt, None, cam, mj.mjtCatBit.mjCAT_ALL.value, scene)
    mj.mjr_render(viewport, scene, context)

    # swap OpenGL buffers (blocking call due to v-sync)
    glfw.swap_buffers(window)

    # process pending GUI events, call GLFW callbacks
    glfw.poll_events()

glfw.terminate()
