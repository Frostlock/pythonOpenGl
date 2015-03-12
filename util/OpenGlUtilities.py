import numpy as np
import random
#from math import cos,sin

def rotationMatrix44(angle_x, angle_y, angle_z):
    """Makes a rotation Matrix44 about 3 axis."""

    cx = np.cos(angle_x)
    sx = np.sin(angle_x)
    cy = np.cos(angle_y)
    sy = np.sin(angle_y)
    cz = np.cos(angle_z)
    sz = np.sin(angle_z)

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
#M  = |  BDE+AF  -BDF+AE  -BC  0 |
#     | -ADE+BF   ADF+BE   AC  0 |
#     |  0        0        0   1 |

    M = np.array([[cy*cz,  sxsy*cz+cx*sz,  -cxsy*cz+sx*sz, 0.0],
                  [-cy*sz, -sxsy*sz+cx*cz, cxsy*sz+sx*cz,  0.0],
                  [sy,     -sx*cy,         cx*cy,          0.0],
                  [0.,     0.,             0.,             1.0]], 'f')
    return M

def translationMatrix44(x, y, z):
    """Makes a translation Matrix44."""

    M = np.array([[1.,       0.,       0.,       0.],
                  [0.,       1.,       0.,       0.],
                  [0.,       0.,       1.,       0.],
                  [float(x), float(y), float(z), 1.]], 'f')
    return M


def otranslationMatrix44(x, y, z):
    """Makes a translation Matrix44."""

    M = np.array([[1.,       0.,       0.,       float(x)],
                  [0.,       1.,       0.,       float(y)],
                  [0.,       0.,       1.,       float(z)],
                  [0.,       0.,       0.,       1.]], 'f')
    return M

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