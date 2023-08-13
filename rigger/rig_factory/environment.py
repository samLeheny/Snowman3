import os
#import rig_factory
from collections import OrderedDict

#root_package_directory = os.path.dirname(rig_factory.__file__.replace('\\', '/'))
#images_directory = '%s/static/images' % root_package_directory
state_string = 'face_rig_state'

# Loads the build directory from whatever the user has decided to load the rig_blueprint from
'''local_build_directory = 'Y:/{}/assets/type/{}/{}/work/rig/Maya/{}/build'.format(
    os.environ['PROJECT_CODE'],
    os.environ['TT_ASSTYPE'],
    os.environ['ENTITY_NAME'],
    os.environ['USERNAME']
)'''

handle_colors = OrderedDict([
    (0, {u'redA': (90,0,0)}),
    (1, {u'redB':(148,5,0)}),
    (2, {u'redC': (210,10,5)}),
    (3, {u'redD': (255.0,25.5,12.75)}),
    (4, {u'redE': (255,50,25)}),
    (5, {u'redF': (255,80,50)}),
    (6, {u'redG': (255,110,80)}),
    (7, {u'orangeA': (100,30,0)}),
    (8, {u'orangeB':(150,60,0)}),
    (9, {u'orangeC': (200,90,0)}),
    (10, {u'orangeD': (255,126.225,0.0)}),
    (11, {u'orangeE': (255,140,0)}),
    (12, {u'orangeF': (255,170,0)}),
    (13, {u'orangeG': (255,190,0)}),
    (14, {u'yellowA': (100,100,0)}),
    (15, {u'yellowB': (135,135,5)}),
    (16, {u'yellowC': (170,170,10)}),
    (17, {u'yellowD': (204.0,204.0,25.5)}),
    (18, {u'yellowE': (220,220,35)}),
    (19, {u'yellowF': (240,240,50)}),
    (20, {u'yellowG': (255,255,70)}),
    (21, {u'greenA': (0,70,0)}),
    (22, {u'greenB':(5,105,5)}),
    (23, {u'greenC':(20,140,20)}),
    (24, {u'greenD':(40,175,40)}),
    (25, {u'greenE': (60,190,60)}),
    (26, {u'greenF':(80,208,80)}),
    (27, {u'greenG': (100,238,100)}),
    (49, {u'cyanA': (0,80,80)}),
    (50, {u'cyanB':(0,120,120)}),
    (51, {u'cyanC': (0,150,150)}),
    (52, {u'cyanD': (0,180,180)}),
    (53, {u'cyanE': (10,210,210)}),
    (54, {u'cyanF': (30,230,230)}),
    (55, {u'cyanG': (60,255,255)}),
    (28, {u'blueA':(0,0,90)}),
    (29, {u'blueB':(0,5,125)}),
    (30, {u'blueC': (5,10,200)}),
    (31, {u'blueD': (12.75,25.5,255.0)}),
    (32, {u'blueE': (20,40,255.0)}),
    (33, {u'blueF': (40,70,255)}),
    (34, {u'blueG':(70,100,255)}),
    (35, {u'purpleA':(45,0,100)}),
    (36, {u'purpleB': (65,5,135)}),
    (37, {u'purpleC':(90,10,170)}),
    (38, {u'purpleD': ((125,15,205))}),
    (39, {u'purpleE':(155,25,230)}),
    (40, {u'purpleF': (200,40,255)}),
    (41, {u'purpleG':(235,60,255)}),
    (42, {u'brownA': (30,5,0)}),
    (43, {u'brownB': (50,20,0)}),
    (44, {u'brownC': (80,40,5)}),
    (45, {u'brownD': (110,60,10)}),
    (46, {u'brownE':(140,80,30)}),
    (47, {u'brownF':(170,120,70)}),
    (48, {u'brownG':(210,160,100)})
])

handle_gimbal_colors = OrderedDict([
    (0, {u'redA':(157,38, 34)}),
    (15, {u'redB': (255.0, 25.5, 12.75)}),
    (1, {u'orangeA':(255,97,0)}),
    (14, {u'orangeB': (255,67,50)}),
    (13, {u'yellowB':(204.0, 204.0, 25.5)}),
    (2, {u'yellowA': (97,97,0)}),
    (3, {u'greenA':(53,117, 29)}),
    (12, {u'greenB':(77,160,105)}),
    (10, {u'blueB': (76.5, 178.5, 229.5)}),
    (4, {u'cyanA':(0,80,80)}),
    (5, {u'blueA':(30,30,133)}),
    (11, {u'cyanB':(65,89,200)}),
    (9, {u'purpleA':(126,70,220)}),
    (6, {u'purpleB': (180,70,152)}),
    (7, {u'brownA': (50,20,0)}),
    (8, {u'none':(148,5,0)})
])

# Only to really be used within show code, when needed
# This directory will change based on what is currently loading in a build setup. When you are building a child rig
# it will first set the directory to the parent, then go to the child next, then to accessory next.
current_build_directory = None

publish_types = ('full', 'anim', 'realtime')  # For geo LOD on publishes

# colors
colors = {
    'left': [0.05, 0.1, 1.0],
    'right': [1.0, 0.1, 0.05],
    'center': [0.8, 0.8, 0.1],
    'highlight': [4.435, 0.495, 0.0],
    'bindJoints': [0.6, 0.7, 1.0],
    'mocapJoints': [1.0, 0.7, 0.6],
    'reverseSpine': [0.9, 0.1, 0.0],
    'lattice': (0.6, 0.3, 0.6),
    'latticeSquish': (0.1, 0.3, 0.6),
    'newlatticeSquish': (0.8, 0.3, 0.1),
    None: [0.8, 0.8, 0.1]
}


secondary_colors = {
    'left': (0.3, 0.7, 0.9),
    'right': (0.9, 0.4, 0.3),
    'center': (0.2, 0.45, 0.0),
    'highlight': (1.0, 1.0, 1.0),
    'bindJoints': (0.5, 0.7, 1.0),
    'mocapJoints': (1.0, 0.78, 0.7),
    'reverseSpine': (0.9, 0.3, 0.25),
    None: (0.8, 0.8, 0.25),
}


# This affects orientations system wide
aim_vector = [0.0, 1.0, 0.0]
up_vector = [0.0, 0.0, -1.0]

side_aim_vectors = {
    'left': aim_vector,
    'right': [x * -1.0 for x in aim_vector],
    'center': aim_vector,
    None: aim_vector
}

side_up_vectors = {
    'left': up_vector,
    'right': [x * -1.0 for x in up_vector],
    'center': up_vector,
    None: up_vector
}

side_cross_vectors = {  # NOTE it would be better to have dynamic (not hardcoded ) values
    'left': [-1.0, 0.0, 0.0],
    'right': [1.0, 0.0, 0.0],
    'center': [-1.0, 0.0, 0.0],
    None: [-1.0, 0.0, 0.0]
}
side_cross_vectorsElbowUp = {  # NOTE it would be better to have dynamic (not hardcoded ) values
    'left': [0.0, 0.0, 1.0],
    'right': [0.0, 0.0, -1.0],
    'center': [0.0, 0.0, 1.0],
    None: [0.0, 0.0, 1.0]
}

# this affects world space positioning of joints / handles
side_world_vectors = dict(
    left=[1.0, 0.0, 0.0],
    right=[-1.0, 0.0, 0.0],
    center=[1.0, 1.0, 0.0]
)

# sides
side_mirror_dictionary = dict(
    left='right',
    right='left'
)

# This needs cleanup
override_colors = {
    'mediumGrey': 0, 'black': 1, 'darkGrey': 2, 'lightGrey': 3, 'maroon': 4, 'darkBlue': 5, 'blue': 6,
    'mediumGreen': 7, 'darkPurple': 8, 'pink': 9, 'mediumBrown': 10, 'darkBrown': 11, 'mediumRed': 12,
    'red': 13, 'green': 14, 'mediumBlue': 15, 'white': 16, 'yellow': 17, 'lightBlue': 18,
    'lightGreen': 19, 'salmon': 20, 'tan': 21, 'lightYelow': 22, 'emerald': 23, 'mediumBrown': 24,
    'greenYellow': 25, 'yellowGreen': 26, 'mediumBrown': 27
}

index_colors = {
    'left': 6,
    'right': 13,
    'center': 17,
    None: 9
}


def vector_to_string(vector):
    axis = ['x', 'y', 'z']
    for ax, v in zip(axis, vector):
        if v > 0.0:
            return ax
        elif v < 0.0:
            return '-{0}'.format(ax)


aim_vector_axis = vector_to_string(aim_vector)
up_vector_axis = vector_to_string(up_vector)

side_vector_axis = dict(
    left=vector_to_string(side_world_vectors['left']),
    right=vector_to_string(side_world_vectors['right']),
    center=vector_to_string(side_world_vectors['center'])
)


# Spline ik settings
ik_twist_dict = {'y': 0, '-y': 1, 'z': 3, '-z': 4, 'x': 6, '-x': 7}

ik_twist_forward_axis = dict(
    left=ik_twist_dict[side_vector_axis['left']],
    right=ik_twist_dict[side_vector_axis['right']],
    center=ik_twist_dict[side_vector_axis['center']]
)
ik_twist_up_axis = dict(
    left=ik_twist_dict[side_vector_axis['left']],
    right=ik_twist_dict[side_vector_axis['right']],
    center=ik_twist_dict[side_vector_axis['center']]
)

rotation_order_dict = {'xy': 0, 'yz': 1, 'zx': 2, 'xz': 3, 'yx': 4, 'zy': 5}
ik_joints_rotation_order = rotation_order_dict[aim_vector_axis[-1] + up_vector_axis[-1]]

rotation_orders = ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx']

# Control groups
top_group_suffix = 'Zro'
bottom_group_suffix = 'Cns'
zip_group_suffix = 'Zip'
roll_group_suffixes = ('Rzr', 'Rol', 'Rpz')  # Offset roll group (offset axis zero, roll group and 'roll post-zero')
standard_group_suffixes = ('Tpx', 'Tpp', 'Top', 'Ofs', 'Drv', 'Cfx')
supported_group_suffixes = tuple(
    [top_group_suffix, bottom_group_suffix] +
    list(standard_group_suffixes) +
    list(roll_group_suffixes) +
    [zip_group_suffix])
standard_group_count = 5  # Ie. 'Zro', 'Ofs', 'Drv', 'Cfx', 'Cns'

# Constant IDs
driven_group_id = 'Drv'  # SDK setups
shard_group_id = 'Ofs'

# AnimCurve data:
# ((point x, point y), (tangent x, tangent y))
falloff_curves = {
    # Curves  |  /`-..  |  .-""-.  |  ..-'\  |  for standard lip roll overlap/falloff
    # Ensure order is character right (-X) to left if updating
    'lip_roll': [
        [
            ((0.0, 0.0), (0.166665, 0.740505)),
            ((0.071663, 0.292985), (0.119987, 0.431434)),
            ((0.159148, 0.477023), (0.083333, 0.059991)),
            ((0.248745, 0.478588), (0.088344, -0.048969)),
            ((0.33333, 0.392968), (0.083333, -0.102398)),
            ((0.416663, 0.287252), (0.083335, -0.101988)),
            ((0.499999, 0.192854), (0.083333, -0.086135)),
            ((0.583328, 0.11553), (0.08333, -0.068092)),
            ((0.66666, 0.05794), (0.083333, -0.044966)),
            ((0.749993, 0.025241), (0.083332, -0.023274)),
            ((0.833325, 0.009181), (0.083333, -0.01043)),
            ((0.927077, 0.002483), (0.125009, -0.005175)),
            ((1.0, 0.0), (0.166685, -0.004757))
        ],
        [
            ((0.0, 0.0), (0.166645, 0.141864)),
            ((0.074161, 0.070896), (0.13, 0.141722)),
            ((0.174172, 0.211682), (0.083332, 0.138262)),
            ((0.25124, 0.350436), (0.078321, 0.146866)),
            ((0.33332, 0.497627), (0.083333, 0.124321)),
            ((0.416654, 0.587677), (0.08334, 0.056175)),
            ((0.5, 0.612969), (0.083332, 0.0)),
            ((0.583319, 0.58794), (0.083325, -0.05512)),
            ((0.66665, 0.499209), (0.083333, -0.124321)),
            ((0.74873, 0.350699), (0.078321, -0.147921)),
            ((0.825798, 0.211682), (0.083333, -0.138262)),
            ((0.925816, 0.070896), (0.13003, -0.141722)),
            ((1.0, 0.0), (0.166705, -0.141864))
        ],
        [
            ((0.0, 0.0), (0.166685, 0.004757)),
            ((0.072923, 0.002483), (0.125009, 0.005175)),
            ((0.166675, 0.009181), (0.083333, 0.01043)),
            ((0.250008, 0.025241), (0.083333, 0.023274)),
            ((0.33334, 0.05794), (0.083333, 0.044966)),
            ((0.416672, 0.11553), (0.08333, 0.068092)),
            ((0.500001, 0.192854), (0.083333, 0.086135)),
            ((0.583337, 0.287252), (0.083335, 0.101988)),
            ((0.66667, 0.392968), (0.083332, 0.102398)),
            ((0.751255, 0.478588), (0.088344, 0.048969)),
            ((0.840852, 0.477023), (0.083333, -0.059991)),
            ((0.928337, 0.292985), (0.119987, -0.431434)),
            ((1.0, 0.0), (0.166665, -0.740505))
        ]
    ],
    # Curves  | ./`-...  |  ..-""-..  |  ...-'\.  | lip roll with smoother ends for partial-mouth roll
    # Ensure order is character right (-X) to left if updating
    'lip_roll_smooth_ends': [
        [
            ((0.0, 0.0), (0.0752, 0.034273)),
            ((0.035355, 0.03654), (0.06622, 0.111886)),
            ((0.096, 0.217353), (0.06188, 0.232369)),
            ((0.165078, 0.454092), (0.081395, 0.164109)),
            ((0.259812, 0.512493), (0.104997, -0.03646)),
            ((0.373218, 0.397946), (0.121185, -0.169934)),
            ((0.5, 0.204067), (0.128647, -0.177639)),
            ((0.625492, 0.065398), (0.116028, -0.094429)),
            ((0.732453, 0.011538), (0.104997, -0.025902)),
            ((0.833633, 0.002367), (0.086552, -0.002284)),
            ((0.904, 0.001471), (0.06188, -0.000664)),
            ((0.964645, 0.000536), (0.06622, -0.001052)),
            ((1.0, 0.0), (0.0752, -0.001092))
        ],
        [
            ((0.0, 0.0), (0.0752, 0.00068)),
            ((0.035355, 0.002057), (0.06622, 0.007549)),
            ((0.096, 0.020611), (0.06188, 0.037829)),
            ((0.166367, 0.096188), (0.086552, 0.141999)),
            ((0.267547, 0.297312), (0.104997, 0.216979)),
            ((0.374508, 0.496485), (0.116028, 0.157312)),
            ((0.5, 0.587525), (0.128647, -0.0)),
            ((0.624203, 0.496485), (0.110871, -0.157312)),
            ((0.724718, 0.297312), (0.104997, -0.216979)),
            ((0.832344, 0.096188), (0.091709, -0.141999)),
            ((0.904, 0.020611), (0.06188, -0.037829)),
            ((0.964645, 0.002057), (0.06622, -0.007549)),
            ((1.0, 0.0), (0.0752, -0.00068))
        ],
        [
            ((0.0, 0.0), (0.0752, 0.001092)),
            ((0.035355, 0.000536), (0.06622, 0.001052)),
            ((0.096, 0.001471), (0.06188, 0.000664)),
            ((0.166367, 0.002367), (0.086552, 0.002284)),
            ((0.267547, 0.011538), (0.104997, 0.025902)),
            ((0.374508, 0.065398), (0.116028, 0.094429)),
            ((0.5, 0.204067), (0.128647, 0.177639)),
            ((0.626782, 0.397946), (0.121185, 0.169934)),
            ((0.740188, 0.512493), (0.104997, 0.03646)),
            ((0.834922, 0.454092), (0.081395, -0.164109)),
            ((0.904, 0.217353), (0.06188, -0.232369)),
            ((0.964645, 0.03654), (0.06622, -0.111886)),
            ((1.0, 0.0), (0.0752, -0.034273))
        ]
    ],
    # Defines 9 points along a remapValue to make a smooth 0.0 to 1.0 curve through a dynamic mid point value,
    #  plus an extra point past each end (-0.125 or 1.125) to control the tangent. Driver is the mid point value.
    'auto_interpolation_remap_points': [
        [
            ((0.0, 0.0), (0.999559, -0.029685)),
            ((0.01, -0.000297), (0.999592, -0.028559)),
            ((0.05, -0.001429), (0.999768, -0.021523)),
            ((0.15, -0.006478), (0.998454, -0.055582)),
            ((0.33, -0.046439), (0.948777, -0.315946)),
            ((0.5, -0.125), (0.87937, -0.476139)),
            ((0.67, -0.231), (0.793141, -0.609038)),
            ((0.85, -0.393759), (0.627925, -0.778274)),
            ((0.95, -0.62713), (0.243821, -0.96982)),
            ((0.99, -1.101902), (0.03685, -0.999321)),
            ((1.0, -1.483656), (0.026186, -0.999657))
        ],
        [
            ((0.0, 0.0), (1.0, 0.0)),
            ((1.0, 0.0), (1.0, 0.0))
        ],
        [
            ((0.0, 0.0), (0.999268, 0.038264)),
            ((0.01, 0.000383), (0.999201, 0.039968)),
            ((0.05, 0.002), (0.998719, 0.050609)),
            ((0.15, 0.012), (0.990376, 0.1384)),
            ((0.33, 0.056), (0.951632, 0.307241)),
            ((0.5, 0.125), (0.917799, 0.397045)),
            ((0.67, 0.203), (0.88305, 0.469278)),
            ((0.85, 0.311), (0.795887, 0.605445)),
            ((0.95, 0.416001), (0.538801, 0.842433)),
            ((0.99, 0.529895), (0.247329, 0.968932)),
            ((1.0, 0.61188), (0.121076, 0.992643))
        ],
        [
            ((0.0, 0.0), (0.995584, 0.093871)),
            ((0.01, 0.000943), (0.995037, 0.099504)),
            ((0.05, 0.005), (0.990917, 0.134474)),
            ((0.15, 0.037), (0.914583, 0.404399)),
            ((0.33, 0.131), (0.854246, 0.51987)),
            ((0.5, 0.25), (0.80226, 0.596975)),
            ((0.67, 0.384), (0.753909, 0.656978)),
            ((0.85, 0.555), (0.653832, 0.75664)),
            ((0.95, 0.708027), (0.449782, 0.893138)),
            ((0.99, 0.833), (0.2682, 0.963363)),
            ((1.0, 0.887625), (0.180073, 0.983653))
        ],
        [
            ((0.0, 0.0), (0.950068, 0.312042)),
            ((0.01, 0.003284), (0.946773, 0.321903)),
            ((0.05, 0.017), (0.924524, 0.381125)),
            ((0.15, 0.079), (0.808237, 0.588858)),
            ((0.33, 0.221), (0.763552, 0.645747)),
            ((0.5, 0.375), (0.72927, 0.684226)),
            ((0.67, 0.54), (0.700071, 0.714073)),
            ((0.85, 0.732), (0.652709, 0.757609)),
            ((0.95, 0.865), (0.540367, 0.841429)),
            ((0.99, 0.95), (0.278875, 0.960327)),
            ((1.0, 0.981519), (0.302415, 0.953176))
        ],
        [
            ((0.0, 0.0), (0.707107, 0.707107)),
            ((1.0, 1.0), (0.707107, 0.707107))
        ],
        [
            ((0.0, 0.018481), (0.302415, 0.953176)),
            ((0.01, 0.05), (0.278875, 0.960327)),
            ((0.05, 0.135), (0.540367, 0.841429)),
            ((0.15, 0.268), (0.652709, 0.757609)),
            ((0.33, 0.46), (0.700071, 0.714073)),
            ((0.5, 0.625), (0.729568, 0.683908)),
            ((0.67, 0.779), (0.763552, 0.645747)),
            ((0.85, 0.921), (0.808237, 0.588858)),
            ((0.95, 0.983), (0.924524, 0.381125)),
            ((0.99, 0.996716), (0.946773, 0.321903)),
            ((1.0, 1.0), (0.950068, 0.312042))
        ],
        [
            ((0.0, 0.112375), (0.180073, 0.983653)),
            ((0.01, 0.167), (0.2682, 0.963363)),
            ((0.05, 0.291973), (0.449782, 0.893138)),
            ((0.15, 0.445), (0.653832, 0.75664)),
            ((0.33, 0.616), (0.753909, 0.656978)),
            ((0.5, 0.75), (0.80226, 0.596975)),
            ((0.67, 0.869), (0.854246, 0.51987)),
            ((0.85, 0.963), (0.914583, 0.404399)),
            ((0.95, 0.995), (0.990917, 0.134474)),
            ((0.99, 0.999057), (0.995037, 0.099504)),
            ((1.0, 1.0), (0.995584, 0.093871))
        ],
        [
            ((0.0, 0.38812), (0.121076, 0.992643)),
            ((0.01, 0.470105), (0.247329, 0.968932)),
            ((0.05, 0.583999), (0.538801, 0.842433)),
            ((0.15, 0.689), (0.795887, 0.605445)),
            ((0.33, 0.797), (0.88305, 0.469278)),
            ((0.5, 0.875), (0.917884, 0.39685)),
            ((0.67, 0.944), (0.951632, 0.307241)),
            ((0.85, 0.988), (0.990376, 0.1384)),
            ((0.95, 0.998), (0.998719, 0.050609)),
            ((0.99, 0.999617), (0.999201, 0.039968)),
            ((1.0, 1.0), (0.999268, 0.038264))
        ],
        [
            ((0.0, 1.0), (1.0, 0.0)),
            ((1.0, 1.0), (1.0, 0.0))
        ],
        [
            ((0.0, 2.483656), (0.026186, -0.999657)),
            ((0.01, 2.101902), (0.03685, -0.999321)),
            ((0.05, 1.62713), (0.243821, -0.96982)),
            ((0.15, 1.393759), (0.627925, -0.778274)),
            ((0.33, 1.231), (0.793141, -0.609038)),
            ((0.5, 1.125), (0.878822, -0.477149)),
            ((0.67, 1.046439), (0.948777, -0.315946)),
            ((0.85, 1.006478), (0.998454, -0.055582)),
            ((0.95, 1.001429), (0.999768, -0.021523)),
            ((0.99, 1.000297), (0.999592, -0.028559)),
            ((1.0, 1.0), (0.999559, -0.029685))
        ]
    ]
}

'''
# Code for getting the falloff curve data in scene from nurbsCurves as point and tangents for driven keys
# Select curve SHAPES from right to left and run
import maya.OpenMaya as om
import maya.cmds as mc
import rig_factory.build.utilities.controller_utilities as cut
import pprint

controller = cut.get_controller()

crv_keys = []
for obj in mc.ls(sl=1):
    degree = mc.getAttr(obj+'.degree')
    f_crv = controller.initialize_node(obj)
    m_crv = om.MFnNurbsCurve(f_crv.m_object)
    num_cvs = m_crv.numCVs()
    pts = []
    for param_val in controller.scene.get_predicted_params_at_cvs(num_cvs, degree):
        mPt = om.MPoint()
        m_crv.getPointAtParam(param_val, mPt)
        mTangent = m_crv.tangent(param_val)
        pts.append(( (round(mPt.x, 6), round(mPt.y, 6) ), ( round(mTangent.x, 6), round(mTangent.y, 6) )))

    crv_keys.append(pts)
pprint.pprint(crv_keys, indent=4)


# Code for getting the falloff curve data in scene from animcurves
import maya.cmds as mc
import pprint
import rig_factory.build.utilities.controller_utilities as cut

controller = cut.get_controller()

curve_data_all = []
for obj in mc.ls(sl=1):
    curve_data = controller.scene.get_animcurve_data(obj)
    curve_data_all.append(curve_data)
pprint.pprint(curve_data_all)


# Code to visualise curves (in Maya graph editor)
# Also helpful for checking the curve order...
import rig_factory.environment as env
import rig_factory.build.utilities.controller_utilities as cut
controller = cut.get_controller()
temp_grp = controller.scene.createNode('transform', n='temp_grp#')
for curve_data, c in zip(env.falloff_curves['lip_roll'], 'xyz'):  # R, C, L
    controller.scene.create_animcurve_from_data(temp_grp+'.sx', temp_grp+'.t'+c, curve_data, subrange=None)

for curve_data, c in zip(env.falloff_curves['auto_interpolation_remap_points'], 'ABCDEFGHIJK'):
    temp_grp = controller.scene.createNode('transform', n='temp_grp'+c)
    controller.scene.create_animcurve_from_data(temp_grp+'.sx', temp_grp+'.tx', curve_data, subrange=None)
'''
