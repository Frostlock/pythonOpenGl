__author__ = 'pi'

import random
from util.vec3 import vec3

class SceneObject(object):
    '''
    SceneObject defines an object that can be rendered in OpenGl
    The number of vertexes = number of normals = number of colors
    The triangleIndices is a list of counter clock wise triangles defined by vertex/normal/color sequence number
    '''

    @property
    def vertices(self):
        return self._vertices

    @property
    def normals(self):
        return self._normals

    @property
    def colors(self):
        return self._colors

    @property
    def texCoords(self):
        return self._texCoords
    @property
    def triangleIndices(self):
        return self._triangleIndices

    @property
    def vertexCount(self):
        return len(self._vertices) / 4

    def __init__(self):
        self._vertices = []
        self._normals = []
        self._colors = []
        self._texCoords = []
        self._triangleIndices = []

class AxisSceneObject(SceneObject):

    def __init__(self, scale=1.0, length=2.0, width=0.01):
        super(AxisSceneObject, self).__init__()

        # X-axis
        elemOffset = len(self.vertices) / 4
        # Store the vertex coordinates: 4 components per vertex: x, y, z, w
        self._vertices.extend((0.0, 0.0, 0.0, 1.0))
        self._vertices.extend((0.0, -width * scale, 0.0, 1.0))
        self._vertices.extend((length * scale, 0.0, 0.0, 1.0))
        self._vertices.extend((0.0, 0.0, 0.0, 1.0))
        self._vertices.extend((0.0, -width * scale, 0.0, 1.0))
        self._vertices.extend((length * scale, 0.0, 0.0, 1.0))
        # Store the vertex color: 4 components per color: R, G, B, A
        color = (1.0, 0.0, 0.0)
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        # Store the vertex normals: 3 components per normal: x, y, z
        self._normals.extend((0.0, 0.0, 1.0))
        self._normals.extend((0.0, 0.0, 1.0))
        self._normals.extend((0.0, 0.0, 1.0))
        self._normals.extend((0.0, 0.0, -1.0))
        self._normals.extend((0.0, 0.0, -1.0))
        self._normals.extend((0.0, 0.0, -1.0))
        # Store the indices for the element drawing (triangles, counter clockwise from front)
        self._triangleIndices.extend((0 + elemOffset, 1 + elemOffset, 2 + elemOffset))
        self._triangleIndices.extend((2 + elemOffset, 1 + elemOffset, 0 + elemOffset))

        # Y-axis
        elemOffset = len(self.vertices) / 4
        # Store the vertex coordinates: 4 components per vertex: x, y, z, w
        self._vertices.extend((0.0, 0.0, 0.0, 1.0))
        self._vertices.extend((0.0, 0.0, -width * scale, 1.0))
        self._vertices.extend((0.0, length * scale, 0.0, 1.0))
        self._vertices.extend((0.0, 0.0, 0.0, 1.0))
        self._vertices.extend((0.0, 0.0, -width * scale, 1.0))
        self._vertices.extend((0.0, length * scale, 0.0, 1.0))
        # Store the vertex color: 4 components per color: R, G, B, A
        color = (0.0, 0.0, 1.0)
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        # Store the vertex normals: 3 components per normal: x, y, z
        self._normals.extend((-1.0, 0.0, 0.0))
        self._normals.extend((-1.0, 0.0, 0.0))
        self._normals.extend((-1.0, 0.0, 0.0))
        self._normals.extend((1.0, 0.0, 0.0))
        self._normals.extend((1.0, 0.0, 0.0))
        self._normals.extend((1.0, 0.0, 0.0))
        # Store the indices for the element drawing (triangles, counter clockwise from front)
        self._triangleIndices.extend((0 + elemOffset, 1 + elemOffset, 2 + elemOffset))
        self._triangleIndices.extend((2 + elemOffset, 1 + elemOffset, 0 + elemOffset))

        # Z-axis
        elemOffset = len(self.vertices) / 4
        # Store the vertex coordinates: 4 components per vertex: x, y, z, w
        self._vertices.extend((0.0, 0.0, 0.0, 1.0))
        self._vertices.extend((-width * scale, 0.0, 0.0, 1.0))
        self._vertices.extend((0.0, 0.0, length * scale, 1.0))
        self._vertices.extend((0.0, 0.0, 0.0, 1.0))
        self._vertices.extend((-width * scale, 0.0, 0.0, 1.0))
        self._vertices.extend((0.0, 0.0, length * scale, 1.0))
        # Store the vertex color: 4 components per color: R, G, B, A
        color = (0.0, 1.0, 0.0)
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        self._colors.extend((color[0], color[1], color[2], 1.0))
        # Store the vertex normals: 3 components per normal: x, y, z
        self._normals.extend((0.0, -1.0, 0.0))
        self._normals.extend((0.0, -1.0, 0.0))
        self._normals.extend((0.0, -1.0, 0.0))
        self._normals.extend((0.0, 1.0, 0.0))
        self._normals.extend((0.0, 1.0, 0.0))
        self._normals.extend((0.0, 1.0, 0.0))
        # Store the indices for the element drawing (triangles, counter clockwise from front)
        self._triangleIndices.extend((0 + elemOffset, 1 + elemOffset, 2 + elemOffset))
        self._triangleIndices.extend((2 + elemOffset, 1 + elemOffset, 0 + elemOffset))

class OBJ(SceneObject):

    def __init__(self, filename, swapyz=False):
        super(OBJ, self).__init__()

        OBJvertices = []
        OBJnormals = []
        OBJtexCoords = []

        self.faces = []
        material = None

        #Parse OBJ file
        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = map(float, values[1:4])
                if swapyz:
                    v = v[0], v[2], v[1]
                OBJvertices.append(v)
            elif values[0] == 'vn':
                v = map(float, values[1:4])
                if swapyz:
                    v = v[0], v[2], v[1]
                OBJnormals.append(v)
            elif values[0] == 'vt':
                OBJtexCoords.append(map(float, values[1:3]))
            elif values[0] in ('usemtl', 'usemat'):
                material = values[1]
            elif values[0] == 'mtllib':
                #Pieter
                #self.mtl = MTL(values[1])
                pass
            elif values[0] == 'f':
                face = []
                texcoords = []
                norms = []
                for v in values[1:]:
                    w = v.split('/')
                    face.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        texcoords.append(int(w[1]))
                    else:
                        texcoords.append(0)
                    if len(w) >= 3 and len(w[2]) > 0:
                        norms.append(int(w[2]))
                    else:
                        norms.append(0)
                self.faces.append((face, norms, texcoords, material))

        # Hard code color
        color = (0.3, 0.3, 0.3, 0.7)

        # Parse the faces of the OBJ object to come to one element index
        # The number of vertices = the number of colors = the number of normals
        ind = 0
        for f in self.faces:
            # Every face should be a counter clockwise triangle
            faceVerts, faceNorms, faceTexCoords, faceMaterial = f
            for i in range (0,3):
                self.vertices.extend(OBJvertices[faceVerts[i] - 1])
                self.vertices.append(1.0) #add W coord
                self.normals.extend(OBJnormals[faceNorms[i] - 1])
                self.colors.extend(color)
                # TODO: very unefficient currently all vertex, normals and color data is duplicated for each face.
                self.triangleIndices.append(ind)
                ind += 1
            # print len(self.vertices)
            # print len(self.normals)
            # print len(self.colors)
            # print len(self.triangleIndex)

    def __str__(self):
        output = str(len(self._vertices)) + ' Vertices\n'
        output += str(self._vertices) + '\n'
        output += str(len(self._normals)) + ' Normals\n'
        output += str(self._normals) + '\n'
        output += str(len(self.faces)) + ' Faces (Triangles), expected to be counter clockwise\n'
        output += '(face vertices, normal for every vertex, texcoords for every vertex, material for the face)\n'
        output += str(self.faces) + '\n'
        return output

class PlantSceneObject(SceneObject):
    def __init__(self,partSize):
        super(PlantSceneObject, self).__init__()
        self.parts = []
        self.futureRoots = []
        self.partSize = partSize
        root = vec3(0.0, 0.0, 0.0)
        self.parts.append(PlantSceneObject.PlantPart(self, partSize, root))

    def grow(self):
        if len(self.futureRoots) > 0:
            root = self.futureRoots[random.randrange(0, len(self.futureRoots))]
            self.futureRoots.remove(root)
            self.parts.append(PlantSceneObject.PlantPart(self, self.partSize, root))

    class PlantPart():
        def __init__(self,parentPlant, partSize, root, parentPart=None):
            self.parentPlant = parentPlant
            self.partSize = partSize
            self.parentPart = parentPart

            offset = partSize / 3
            height = partSize * 3

            elemOffset = parentPlant.vertexCount

            # Store the vertex coordinates: 4 components per vertex: x, y, z, w
            parentPlant.vertices.extend((root.x + offset, root.y, root.z + height, 1.0))
            parentPlant.vertices.extend((root.x + offset, root.y + offset, root.z + height, 1.0))
            parentPlant.vertices.extend((root.x, root.y + offset, root.z + height, 1.0))
            parentPlant.vertices.extend((root.x, root.y, root.z, 1.0))

            # Store the vertex color: 4 components per color: R, G, B, A
            color = (1.0, 0.5, 0.3)
            parentPlant.colors.extend((color[0], color[1], color[2], 1.0))
            parentPlant.colors.extend((color[0], color[1], color[2], 1.0))
            parentPlant.colors.extend((color[0], color[1], color[2], 1.0))
            parentPlant.colors.extend((color[0], color[1], color[2], 1.0))

            # Store the vertex normals: 3 components per normal: x, y, z
            parentPlant.normals.extend((-1.0, 1.0, -0.2))
            parentPlant.normals.extend((1.0, 1.0, -0.2))
            parentPlant.normals.extend((1.0, -1.0, -0.2))
            parentPlant.normals.extend((0.0, 0.0, 1.0))

            # Store the indices for the element drawing (triangles, clockwise from front)
            parentPlant.triangleIndices.extend((1 + elemOffset, 2 + elemOffset, 0 + elemOffset))
            parentPlant.triangleIndices.extend((2 + elemOffset, 3 + elemOffset, 0 + elemOffset))
            parentPlant.triangleIndices.extend((0 + elemOffset, 3 + elemOffset, 1 + elemOffset))
            parentPlant.triangleIndices.extend((1 + elemOffset, 3 + elemOffset, 2 + elemOffset))

            # Store future roots for the parent plant
            parentPlant.futureRoots.append(vec3(root.x + offset, root.y, root.z + height))
            parentPlant.futureRoots.append(vec3(root.x + offset, root.y + offset, root.z + height))
            parentPlant.futureRoots.append(vec3(root.x, root.y + offset, root.z + height))

if __name__ == '__main__':
    print "obj loader starting"
    #parse("./sphere.obj")

    obj = OBJ("./cube.obj")

    print obj

    sceneObj = SceneObject(obj)

    # example output
    #
    # 8 Vertices
    # [[-1.0, -1.0, 1.0], [-1.0, -1.0, -1.0], [1.0, -1.0, -1.0], [1.0, -1.0, 1.0], [-1.0, 1.0, 1.0], [-1.0, 1.0, -1.0], [1.0, 1.0, -1.0], [1.0, 1.0, 1.0]]
    # 6 Normals
    # [[-1.0, 0.0, 0.0], [0.0, 0.0, -1.0], [1.0, -0.0, 0.0], [0.0, -0.0, 1.0], [0.0, -1.0, 0.0], [0.0, 1.0, 0.0]]
    # 12 Faces (Triangles), expected to be counter clockwise
    # (face vertices, normal for every vertex, texcoords for every vertex, material for the face)
    # [([5, 6, 2], [1, 1, 1], [0, 0, 0], None), ([6, 7, 3], [2, 2, 2], [0, 0, 0], None),

