import numpy as np

# For performance use the math functions, numpy also has these for multi dimensional arrays.
# For single values the math variants are faster
from math import sin, cos

import random
#from math import cos,sin

def rotationMatrix44(angle_x, angle_y, angle_z):
    """Makes a rotation Matrix44 about 3 axis."""

    cx = cos(angle_x)
    sx = sin(angle_x)
    cy = cos(angle_y)
    sy = sin(angle_y)
    cz = cos(angle_z)
    sz = sin(angle_z)

    sxsy = sx*sy
    cxsy = cx*sy

    # http://web.archive.org/web/20041029003853/http:/www.j3d.org/matrix_faq/matrfaq_latest.html#Q35
    #A = cos(angle_x)
    #B = sin(angle_x)
    #C = cos(angle_y)
    #D = sin(angle_y)
    #E = cos(angle_z)
    #F = sin(angle_z)

    #     |  CE      -CF       D   0 |
    # M = |  BDE+AF  -BDF+AE  -BC  0 |
    #     | -ADE+BF   ADF+BE   AC  0 |
    #     |  0        0        0   1 |

    M = np.array([[cy*cz,  sxsy*cz+cx*sz,  -cxsy*cz+sx*sz, 0.0],
                  [-cy*sz, -sxsy*sz+cx*cz, cxsy*sz+sx*cz,  0.0],
                  [sy,     -sx*cy,         cx*cy,          0.0],
                  [0.,     0.,             0.,             1.0]], 'f')
    return M

def rotationMatrix(angle, axis):
    '''
    http://www.arcsynthesis.org/gltut/Positioning/Tut06%20Rotation.html
    :param angle: Angle of rotation in radians
    :param axis: Vec3 defining the axis of the rotation
    :return: 4x4 matrix for the rotation
    '''
    x, y, z = axis
    C = cos(angle)
    S = sin(angle)
    iC = 1 - C
    iS = 1 - S
    xx = x*x
    yy = y*y
    zz = z*z

    R = np.array([[xx+(1-xx)*C,  iC*x*y+z*S,   iC*x*z-y*S,   0.0],
                  [iC*x*y-z*S,   yy+(1-yy)*C,  iC*y*z+x*S,   0.0],
                  [iC*x*z+y*S,   iC*y*z-x*S,   zz+(1-zz)*C,  0.0],
                  [0.0,          0.0,          0.0,          1.0]], 'f')

    return R

def translationMatrix44(x, y, z):
    """Makes a translation Matrix44."""

    # Translation(x,y,z)

    #     | 1  0  0  x |
    # M = | 0  1  0  y |
    #     | 0  0  1  z |
    #     | 0  0  0  1 |

    T = np.array([[1.,       0.,       0.,       0.],
                  [0.,       1.,       0.,       0.],
                  [0.,       0.,       1.,       0.],
                  [float(x), float(y), float(z), 1.]], 'f')
    return T

# def old_translationMatrix44(x, y, z):
#     """Makes a translation Matrix44."""
#
#     M = np.array([[1.,       0.,       0.,       float(x)],
#                   [0.,       1.,       0.,       float(y)],
#                   [0.,       0.,       1.,       float(z)],
#                   [0.,       0.,       0.,       1.]], 'f')
#     return M

def lookAtMatrix44(eye, center, up):
    '''
    Based on http://learnopengl.com/#!Getting-started/Camera
    :param eye: vec3 - x,y,z coordinate representing the position of the camera
    :param center: vec3 - x,y,z coordinate towards which the camera is looking
    :param up: vec3 - x,y,z coordinate used to determine what is up for the camera
    :return:
    '''
    M1 = np.array([[1.,       0.,       0.,       0.],
                  [ 0.,       1.,       0.,       0.],
                  [ 0.,       0.,       1.,       0.],
                  [ -eye.x,   -eye.y,   -eye.z,   1.]], 'f')


    D = (eye - center).normalize()
    R = up.cross(D).normalize()
    U = D.cross(R)

    M2 = np.array([[R.x,      U.x,      D.x,      0.],
                  [ R.y,      U.y,      D.y,      0.],
                  [ R.z,      U.z,      D.z,      0.],
                  [ 0.,       0.,       0.,       1.]], 'f')

    return M1.dot(M2)

class plant():
    def __init__(self,partSize):
        self.parts = []
        self.partSize = partSize
        root = (0.0, 0.0, 0.0)
        self.parts.append(part(partSize, root))

    def grow(self):
        parent = self.parts[random.randrange(0,len(self.parts))]
        newChild = parent.tryToCreateNewChild()
        if newChild is not None:
            self.parts.append(newChild)

class part():
    def __init__(self, partSize, root, parentPart=None):
        self.partSize = partSize
        self.parentPart = parentPart
        self.vertexData = []
        self.colorData = []
        self.normalsData = []
        self.elementData = []

        self.rootIndices = [0, 1, 2]

        offset = partSize / 3
        height = partSize * 3

        if parentPart is None:
            elemOffset = 0
        else:
            elemOffset = parentPart.elemOffset

        # Store the vertex coordinates: 4 components per vertex: x, y, z, w
        self.vertexData.extend((root[0] + offset, root[1], root[2] + height, 1.0))
        self.vertexData.extend((root[0] + offset, root[1] + offset, root[2] + height, 1.0))
        self.vertexData.extend((root[0], root[1] + offset, root[2] + height, 1.0))
        self.vertexData.extend((root[0], root[1], root[2], 1.0))

        # Store the vertex color: 4 components per color: R, G, B, A
        color = (1.0, 0.5, 0.3)
        self.colorData.extend((color[0], color[1], color[2], 1.0))
        self.colorData.extend((color[0], color[1], color[2], 1.0))
        self.colorData.extend((color[0], color[1], color[2], 1.0))
        self.colorData.extend((color[0], color[1], color[2], 1.0))

        # Store the vertex normals: 3 components per normal: x, y, z
        self.normalsData.extend((-1.0, 1.0, -0.2))
        self.normalsData.extend((1.0, 1.0, -0.2))
        self.normalsData.extend((1.0, -1.0, -0.2))
        self.normalsData.extend((0.0, 0.0, 1.0))

        # Store the indices for the element drawing (triangles, clockwise from front)
        self.elementData.extend((1 + elemOffset, 2 + elemOffset, 0 + elemOffset))
        self.elementData.extend((2 + elemOffset, 3 + elemOffset, 0 + elemOffset))
        self.elementData.extend((0 + elemOffset, 3 + elemOffset, 1 + elemOffset))
        self.elementData.extend((1 + elemOffset, 3 + elemOffset, 2 + elemOffset))

        self.elemOffset = elemOffset + 4

    def tryToCreateNewChild(self):
        if len(self.rootIndices) == 0:
            return None
        else:
            i = random.randrange(0, len(self.rootIndices))
            root = self.vertexData[self.rootIndices[i]:self.rootIndices[i]+3]
            print root
            del self.rootIndices[i]
            return part(self.partSize,root,self)

if __name__ == '__main__':
    pass
    from util.vec3 import vec3
    eye = vec3(1.0, 1.0, 1.0)
    center = vec3(0.0, 0.0, 0.0)
    up = vec3(0.0, 0.0, 1.0)
    M = lookAtMatrix44(eye,center,up)
    print M

    # test = vec3(3,1,2)
    # print test.length()
    # print test.normalize()