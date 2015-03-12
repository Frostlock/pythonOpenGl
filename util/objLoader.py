__author__ = 'pi'

class OBJ:
    def __init__(self, filename, swapyz=False):
        """Loads a Wavefront OBJ file. """
        self.vertices = []
        self.normals = []
        self.texcoords = []
        self.faces = []

        material = None
        for line in open(filename, "r"):
            if line.startswith('#'): continue
            values = line.split()
            if not values: continue
            if values[0] == 'v':
                v = map(float, values[1:4])
                if swapyz:
                    v = v[0], v[2], v[1]
                self.vertices.append(v)
            elif values[0] == 'vn':
                v = map(float, values[1:4])
                if swapyz:
                    v = v[0], v[2], v[1]
                self.normals.append(v)
            elif values[0] == 'vt':
                self.texcoords.append(map(float, values[1:3]))
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

    def __str__(self):
        output = str(len(self.vertices)) + ' Vertices\n'
        output += str(self.vertices) + '\n'
        output += str(len(self.normals)) + ' Normals\n'
        output += str(self.normals) + '\n'
        output += str(len(self.faces)) + ' Faces (Triangles), expected to be counter clockwise\n'
        output += '(face vertices, normal for every vertex, texcoords for every vertex, material for the face)\n'
        output += str(self.faces) + '\n'
        return output

class SceneObject:
    def __init__(self, objObject):
        self.vertices = []
        self.normals = []
        self.colors = []
        self.triangleIndex = []

        color = (0.3, 0.3, 0.3, 0.7)

        # we need to parse the OBJ object to come to one element index
        # The number of vertices = the number of colors = the number of normals
        ind = 0
        for f in objObject.faces:
            # Every face should be a counter clockwise triangle
            faceVerts, faceNorms, faceTexCoords, faceMaterial = f
            for i in range (0,3):
                self.vertices.extend(objObject.vertices[faceVerts[i] - 1])
                self.vertices.append(1.0) #add W coord
                self.normals.extend(objObject.normals[faceNorms[i] - 1])
                self.colors.extend(color)
                # TODO: very unefficient currently all data is duplicated and the element index is useless
                self.triangleIndex.append(ind)
                ind +=1
            # print len(self.vertices)
            # print len(self.normals)
            # print len(self.colors)
            # print len(self.triangleIndex)



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

