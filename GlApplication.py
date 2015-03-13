"""
Created on March 11, 2015

PyOpenGl project using PyGame.

Special thanks to these two for getting me started!
http://www.arcsynthesis.org/gltut/
http://www.willmcgugan.com/blog/tech/2007/6/4/opengl-sample-code-for-pygame/

@author: pi
"""

import pygame
from pygame.locals import *
from OpenGL import GL
from OpenGL.GL.ARB.vertex_array_object import glBindVertexArray
from OpenGL import GLUT
from ctypes import c_void_p
from math import radians, degrees
import sys

import numpy as np

import util.OpenGlUtilities as og_util
import util.PyGameUtilities as pg_util

# TileSize in model space
TILESIZE = 0.25

# 4 bytes in a float
# TODO: Find a better way to deal with this
SIZE_OF_FLOAT = 4

# 4 components in a vector: X, Y, Z, W
VERTEX_COMPONENTS = 4

# Camera modes
CAM_FREE = 0
CAM_MAP = 1
CAM_ACTOR = 2
CAM_FIRSTPERSON = 3

class GlApplication(object):

    @property
    def level(self):
        """
        Returns the level that is currently being shown in the GUI
        """
        return self._level

    @level.setter
    def level(self, level):
        """
        Sets the level to be shown in the GUI.
        This will also load the vertex buffer for the level mesh
        """
        self._level = level
        # Load the mesh for the level in the vertex buffer
        self.loadVAOStaticObjects()

    @property
    def displaySize(self):
        """
        Returns the display size (width, height)
        """
        return self._displaySize

    @property
    def displayWidth(self):
        """
        Returns the display width
        """
        return self.displaySize[0]

    @property
    def displayHeight(self):
        """
        Returns the display height
        """
        return self.displaySize[1]

    @property
    def openGlProgram(self):
        """
        Property to store the program ID of the openGl Program that is in use
        :return: OpenGl ID
        """
        return self._openGlProgram

    @openGlProgram.setter
    def openGlProgram(self, program):
        """
        Sets the OpenGl program ID.
        :param program: OpenGl program ID to be stored
        :return:
        """
        self._openGlProgram = program

    @property
    def cameraMatrix(self):
        """
        Returns the camera matrix
        """
        return self._cameraMatrix

    @cameraMatrix.setter
    def cameraMatrix(self, matrix):
        """
        Sets the camera matrix
        """
        self._cameraMatrix = matrix

    @property
    def cameraMode(self):
        return self._cameraMode

    @cameraMode.setter
    def cameraMode(self, mode):
        self._cameraMode = mode

    @property
    def perspectiveMatrix(self):
        """
        Returns the perspective matrix
        """
        return self._perspectiveMatrix

    @perspectiveMatrix.setter
    def perspectiveMatrix(self, matrix):
        """
        Sets the perspective matrix
        """
        self._perspectiveMatrix = matrix

    @property
    def lightingMatrix(self):
        """
        Returns the lighting matrix
        """
        return self._lightingMatrix

    @lightingMatrix.setter
    def lightingMatrix(self, matrix):
        """
        Sets the lighting matrix
        """
        self._lightingMatrix = matrix

    @property
    def lightPosition(self):
        return (10.866, 5, -15.001)

    @property
    def fogActive(self):
        return False

    def __init__(self):
        """
        Constructor to create a new GlApplication object.
        """
        # Initialize class properties
        self._level = None
        self._displaySize = (800, 600)
        self._openGlProgram = None
        self._cameraMatrix = None
        self._cameraMode = 0
        self._perspectiveMatrix = None
        self._lightingMatrix = None
        self._dragging = False
        self._rotating = False
        self.FPS = 0
        # Initialize uniform class variables
        self.perspectiveMatrixUnif = None
        self.cameraMatrixUnif = None
        self.lightPosUnif = None
        self.lightIntensityUnif = None
        self.ambientIntensityUnif = None
        self.lightingMatrixUnif = None
        self.playerPositionUnif = None
        self.fogDistanceUnif = None
        self.fogActiveUnif = None


        #self.construct = og_util.plant(3*TILESIZE)

        import util.objLoader
        cubeObj = util.objLoader.OBJ("./util/cube.obj")
        lucyObj = util.objLoader.OBJ("./util/lucy.obj")

        self.dynamicObjects = []
        self.dynamicObjects.append(util.objLoader.SceneObject(cubeObj))
        self.dynamicObjects.append(util.objLoader.AxisSceneObject(scale=10))

        self.staticObjects = []
        #self.staticObjects.append(util.objLoader.AxisSceneObject(scale=10))
        #self.staticObjects.append(util.objLoader.SceneObject(cubeObj))


    def resizeWindow(self, displaySize):
        """
        Function to be called whenever window is resized.
        This function will ensure pygame display, glviewport and perspective matrix is recalculated
        """
        self._displaySize = displaySize
        width, height = displaySize
        pygame.display.set_mode(self.displaySize, RESIZABLE | HWSURFACE | DOUBLEBUF | OPENGL)
        # Uncomment to run in fullscreen
        # pygame.display.set_mode(self.displaySize,FULLSCREEN|HWSURFACE|DOUBLEBUF|OPENGL)
        GL.glViewport(0, 0, width, height)
        self.calculatePerspectiveMatrix()

    def calculatePerspectiveMatrix(self):
        """
        Sets the perspective matrix
        """
        pMat = np.zeros((4, 4), 'f')

        fFrustumScale = 1.0
        fzNear = 0.1
        fzFar = 1000.0

        pMat[0, 0] = fFrustumScale * 1
        pMat[1, 1] = fFrustumScale * (float(self.displayWidth) / self.displayHeight)
        pMat[2, 2] = (fzFar + fzNear) / (fzNear - fzFar)
        pMat[3, 2] = (2 * fzFar * fzNear) / (fzNear - fzFar)
        pMat[2, 3] = -1.0

        self.perspectiveMatrix = pMat

    def initOpenGl(self):
        """
        Initializes OpenGl settings and shaders
        """
        GLUT.glutInit([])

        # Compile Shaders into program object
        from OpenGL.GL.shaders import compileShader, compileProgram

        strVertexShader = open("shaders/VertexShader.glsl").read()
        strFragmentShader = open("shaders/FragmentShader.glsl").read()
        self.openGlProgram = compileProgram(
            compileShader(strVertexShader, GL.GL_VERTEX_SHADER),
            compileShader(strFragmentShader, GL.GL_FRAGMENT_SHADER)
        )

        # Create uniform variables for the compiled shaders
        GL.glUseProgram(self.openGlProgram)
        # Camera and perspective projection
        self.perspectiveMatrixUnif = GL.glGetUniformLocation(self.openGlProgram, "perspectiveMatrix")
        self.cameraMatrixUnif = GL.glGetUniformLocation(self.openGlProgram, "cameraMatrix")
        # Lighting
        self.lightPosUnif = GL.glGetUniformLocation(self.openGlProgram, "lightPos")
        self.lightIntensityUnif = GL.glGetUniformLocation(self.openGlProgram, "lightIntensity")
        self.ambientIntensityUnif = GL.glGetUniformLocation(self.openGlProgram, "ambientIntensity")
        self.lightingMatrixUnif = GL.glGetUniformLocation(self.openGlProgram, "lightingMatrix")
        # Fog of War
        self.playerPositionUnif = GL.glGetUniformLocation(self.openGlProgram, "playerPosition")
        self.fogDistanceUnif = GL.glGetUniformLocation(self.openGlProgram, "fogDistance")
        GL.glUniform1f(self.fogDistanceUnif, 4.0)
        self.fogActiveUnif = GL.glGetUniformLocation(self.openGlProgram, "fogActive")

        # Generate Vertex Array Object for the level
        self.VAO_level = GL.GLuint(0)
        GL.ARB.vertex_array_object.glGenVertexArrays(1, self.VAO_level)

        # Generate Vertex Array Object for the actors
        self.VAO_actors = GL.GLuint(0)
        GL.ARB.vertex_array_object.glGenVertexArrays(1, self.VAO_actors)

        # Recalculate the perspective matrix
        self.calculatePerspectiveMatrix()

        GL.glUseProgram(0)

        # Enable depth testing
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(GL.GL_TRUE)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glDepthRange(0.0, 1.0)

        # Enable alpha testing
        GL.glEnable(GL.GL_ALPHA_TEST)
        GL.glAlphaFunc(GL.GL_GREATER, 0.5)

        # Enable face culling
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)  # back side of each face will be culled
        GL.glFrontFace(GL.GL_CCW)  # front of the face is based on counter clockwise order of vertices
        #GL.glFrontFace(GL.GL_CW)  # front of the face is based on clockwise order of vertices

    def showMainMenu(self):
        # Init pygame
        pygame.init()
        self.resizeWindow((800, 600))

        #Initialize fonts
        pg_util.initFonts()

        #Init OpenGl
        self.initOpenGl()

        clock = pygame.time.Clock()

        self.freeCamera()
        self.loadVAOStaticObjects()

        # Initialize speeds
        rotation_speed = radians(90.0)
        movement_speed = 5.0

        while True:
            # handle pygame (GUI) events
            events = pygame.event.get()
            for event in events:
                self.handlePyGameEvent(event)

            # Clear the screen, and z-buffer
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT);

            time_passed = clock.tick()
            time_passed_seconds = time_passed / 1000.
            if time_passed_seconds <> 0: self.FPS = 1 / time_passed_seconds

            pressed = pygame.key.get_pressed()

            # Reset rotation and movement directions
            # rotation_direction.set(0.0, 0.0, 0.0)
            rotation_direction = np.array((0.0, 0.0, 0.0), 'f')
            # movement_direction.set(0.0, 0.0, 0.0)
            movement_direction = np.array((0.0, 0.0, 0.0), 'f')

            # Modify direction vectors for key presses
            if pressed[K_LEFT]:
                # rotation_direction.y = +1.0
                rotation_direction[1] = +1.0
                self.cameraMode = CAM_FREE
            elif pressed[K_RIGHT]:
                # rotation_direction.y = -1.0
                rotation_direction[1] = -1.0
                self.cameraMode = CAM_FREE
            if pressed[K_UP]:
                # rotation_direction.x = -1.0
                rotation_direction[0] = -1.0
                self.cameraMode = CAM_FREE
            elif pressed[K_DOWN]:
                # rotation_direction.x = +1.0
                rotation_direction[0] = +1.0
                self.cameraMode = CAM_FREE
            if pressed[K_PAGEUP]:
                # rotation_direction.z = -1.0
                rotation_direction[2] = -1.0
                self.cameraMode = CAM_FREE
            elif pressed[K_PAGEDOWN]:
                # rotation_direction.z = +1.0
                rotation_direction[2] = +1.0
                self.cameraMode = CAM_FREE
            if pressed[K_HOME]:
                # movement_direction.z = -1.0
                movement_direction[2] = -1.0
                self.cameraMode = CAM_FREE
            elif pressed[K_END]:
                # movement_direction.z = +1.0
                movement_direction[2] = +1.0
                self.cameraMode = CAM_FREE

            # Calculate rotation matrix and multiply by camera matrix    
            rotation = rotation_direction * rotation_speed * time_passed_seconds
            rotation_matrix = og_util.rotationMatrix44(*rotation)
            # if you do this the other way around you rotate the world before moving the camera
            self.cameraMatrix = rotation_matrix.dot(self.cameraMatrix)

            # Calcluate movment and add it to camera matrix translate
            heading = self.cameraMatrix[:3, 2]  # Forward direction
            movement = heading * movement_direction * movement_speed * time_passed_seconds
            movement_matrix = og_util.translationMatrix44(*movement)
            # if you do this the other way around you move the world before moving the camera
            self.cameraMatrix = movement_matrix.dot(self.cameraMatrix)

            # First person camera
            if self.cameraMode == CAM_FIRSTPERSON:
                self.firstPersonCamera()
            elif self.cameraMode == CAM_ACTOR:
                self.centerCameraOnActor(self.game.player)

            # Refresh the actors VAO (some actors might have moved)
            self.loadVAODynamicObjects()

            # Render the 3D view (Vertex Array Buffers
            self.drawVBAs()

            # Render the HUD (health bar, XP bar, etc...)
            self.drawHUD()

            # Show the screen
            pygame.display.flip()

    def freeCamera(self):
        playerRotation = og_util.rotationMatrix44(0, 0, radians(-180))
        # Rotate upward to look ahead
        rotation_matrix = og_util.rotationMatrix44(radians(135), 0, 0)
        translation_matrix = og_util.translationMatrix44(0, 1, 1.0)
        self.cameraMatrix = translation_matrix.dot(rotation_matrix.dot(playerRotation))
        #self.cameraMatrix = translation_matrix

    def centerCameraOnActor(self, actor):
        """
        Centers the camera above the given actor.
        """
        self.cameraMode = CAM_ACTOR
        x = actor.tile.x
        y = actor.tile.y
        self.cameraMatrix = og_util.translationMatrix44(x * TILESIZE, y * TILESIZE, 4.0)

    def centerCameraOnMap(self):
        """
        Centers the camera above the current map.
        """
        self.cameraMode = CAM_MAP
        map = self.game.currentLevel.map
        x = map.width / 2
        y = map.height / 2
        self.cameraMatrix = og_util.translationMatrix44(x * TILESIZE, y * TILESIZE - 1, 10)

    def firstPersonCamera(self):
        """
        Moves the camera to a first person view for the player
        """
        self.cameraMode = CAM_FIRSTPERSON

        # Translate above the player
        x, y, z, w = self.getPlayerPosition()
        self.cameraMatrix = og_util.translationMatrix44(x, y, z)
        # Rotate to look in player direction
        print self.game.player.direction
        dx = self.game.player.direction[0]
        dy = self.game.player.direction[1]
        import numpy as np
        directionAngle = -1 * np.arcsin(dx/(np.sqrt(dx*dx + dy*dy)))
        if dy < 0 :
            directionAngle= np.pi + np.arcsin(dx/(np.sqrt(dx*dx + dy*dy)))

        playerRotation = og_util.rotationMatrix44(0, 0, directionAngle)
        # Rotate upward to look ahead
        rotation_matrix = og_util.rotationMatrix44(radians(90), 0, 0).dot(playerRotation)
        print rotation_matrix
        self.cameraMatrix = rotation_matrix.dot(self.cameraMatrix)

    def getPlayerPosition(self):
        """
        Returns the current position of the player in model space
        :rtype : Tuple (x, y, z, w)
        :return: The position in 3D model space of the player
        """
        # playerX = self.game.player.tile.x * TILESIZE + (TILESIZE / 2)
        # playerY = self.game.player.tile.y * TILESIZE + (TILESIZE / 2)
        # playerZ = TILESIZE / 2
        # return (playerX, playerY, playerZ, 1.0)
        return (0.0, 0.0, 0.0, 1.0)

    def loadVAOStaticObjects(self):
        """
        Initializes the context of the level VAO
        The level VAO contains the basic level mesh
        To optimize performance this will only be called when a new level is loaded
        """
        # Create vertex buffers on the GPU, remember the address IDs
        self.VBO_level_id = GL.glGenBuffers(1)
        self.VBO_level_elements_id = GL.glGenBuffers(1)

        # Construct the data arrays that will be loaded into the buffer
        vertexData = []
        colorData = []
        normalsData = []
        elementData = []

        elemOffset = 0
        for obj in self.staticObjects:
            vertexData.extend(obj.vertices)
            colorData.extend(obj.colors)
            normalsData.extend(obj.normals)
            for elem in obj.triangleIndices:
                 elementData.append(elem + elemOffset)
            elemOffset += obj.vertexCount

        # # Store the vertex coordinates
        # for tileRow in self.game.currentLevel.map.tiles:
        #     for tile in tileRow:
        #         if tile.blocked:
        #             height = TILESIZE
        #         else:
        #             height = 0.0
        #         # 4 components per vertex: x, y, z, w
        #         # 4 vertices: bottom of the rectangular tile area
        #         vertexData.extend((tile.x * TILESIZE, tile.y * TILESIZE, 0.0, 1.0))
        #         vertexData.extend((tile.x * TILESIZE, tile.y * TILESIZE + TILESIZE, 0.0, 1.0))
        #         vertexData.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE + TILESIZE, 0.0, 1.0))
        #         vertexData.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE, 0.0, 1.0))
        #         # 4 vertices: top of the rectangular tile area
        #         vertexData.extend((tile.x * TILESIZE, tile.y * TILESIZE, height, 1.0))
        #         vertexData.extend((tile.x * TILESIZE, tile.y * TILESIZE + TILESIZE, height, 1.0))
        #         vertexData.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE + TILESIZE, height, 1.0))
        #         vertexData.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE, height, 1.0))
        #
        # # Store the vertex colors
        # self.VBO_level_color_offset = len(vertexData)
        # for tileRow in self.game.currentLevel.map.tiles:
        #     for tile in tileRow:
        #         # 4 components per color: R, G, B, A, one color for every vertex
        #         color = self.normalizeColor(tile.color)
        #         # 4 vertices for the bottom
        #         vertexData.extend((color[0], color[1], color[2], 1.0))
        #         vertexData.extend((color[0], color[1], color[2], 1.0))
        #         vertexData.extend((color[0], color[1], color[2], 1.0))
        #         vertexData.extend((color[0], color[1], color[2], 1.0))
        #         # 4 vertices for the top
        #         vertexData.extend((color[0], color[1], color[2], 1.0))
        #         vertexData.extend((color[0], color[1], color[2], 1.0))
        #         vertexData.extend((color[0], color[1], color[2], 1.0))
        #         vertexData.extend((color[0], color[1], color[2], 1.0))
        #
        # # Store the vertex normals
        # self.VBO_level_normals_offset = len(vertexData)
        # for tileRow in self.game.currentLevel.map.tiles:
        #     for tile in tileRow:
        #         # 3 components per normal: x, y, z
        #         # 4 vertex normals for the bottom
        #         vertexData.extend((-1.0, -1.0, -0.01))
        #         vertexData.extend((1.0, -1.0, -0.01))
        #         vertexData.extend((1.0, 1.0, -0.01))
        #         vertexData.extend((-1.0, 1.0, -0.01))
        #         # 4 vertex normals for the top
        #         vertexData.extend((-1.0, -1.0, -1.0))
        #         vertexData.extend((1.0, -1.0, -1.0))
        #         vertexData.extend((1.0, 1.0, -1.0))
        #         vertexData.extend((-1.0, 1.0, -1.0))
        #
        # self.VBO_level_length = len(vertexData)
        #
        # # Create the element array
        # offset = 0
        # for tileRow in self.game.currentLevel.map.tiles:
        #     for tile in tileRow:
        #         # 12 Triangles for a complete block
        #         elementData.extend((0 + offset, 2 + offset, 1 + offset))
        #         elementData.extend((0 + offset, 3 + offset, 2 + offset))
        #         elementData.extend((0 + offset, 4 + offset, 7 + offset))
        #         elementData.extend((0 + offset, 7 + offset, 3 + offset))
        #         elementData.extend((3 + offset, 7 + offset, 6 + offset))
        #         elementData.extend((3 + offset, 6 + offset, 2 + offset))
        #         elementData.extend((2 + offset, 6 + offset, 5 + offset))
        #         elementData.extend((2 + offset, 5 + offset, 1 + offset))
        #         elementData.extend((1 + offset, 5 + offset, 4 + offset))
        #         elementData.extend((1 + offset, 4 + offset, 0 + offset))
        #         elementData.extend((4 + offset, 5 + offset, 6 + offset))
        #         elementData.extend((4 + offset, 6 + offset, 7 + offset))
        #         offset += 8
        #
        # self.VBO_level_elements_length = len(elementData)


        # Remember where each data set begins
        self.VBO_level_color_offset = len(vertexData)
        vertexData.extend(colorData)
        self.VBO_level_normals_offset = len(vertexData)
        vertexData.extend(normalsData)
        self.VBO_level_length = len(vertexData)
        self.VBO_level_elements_length = len(elementData)

        # Set up the VAO context
        GL.glUseProgram(self.openGlProgram)
        glBindVertexArray(self.VAO_level)

        # Load the constructed vertex and color data array into the created array buffer
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO_level_id)
        array_type = (GL.GLfloat * len(vertexData))
        GL.glBufferData(GL.GL_ARRAY_BUFFER, len(vertexData) * SIZE_OF_FLOAT, array_type(*vertexData), GL.GL_STATIC_DRAW)
        # Enable Vertex inputs and define pointer
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, None)
        # Enable Color inputs and define pointer
        GL.glEnableVertexAttribArray(1)
        colorDataStart = self.VBO_level_color_offset * SIZE_OF_FLOAT
        GL.glVertexAttribPointer(1, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, c_void_p(colorDataStart))
        # Enable Normals inputs and define pointer
        GL.glEnableVertexAttribArray(2)
        normalsDataStart = self.VBO_level_normals_offset * SIZE_OF_FLOAT
        GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, False, 0, c_void_p(normalsDataStart))

        # Load the constructed element data array into the created element array buffer
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.VBO_level_elements_id)
        array_type = (GL.GLint * len(elementData))
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, len(elementData) * SIZE_OF_FLOAT, array_type(*elementData),
                        GL.GL_STATIC_DRAW)

        # Done
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glUseProgram(0)

    def loadVAODynamicObjects(self):
        """
        Initializes the context of the actors VAO
        This should be called whenever there is a change in actor positions or visibility
        """
        # Create the vertex buffer on the GPU and remember the address ID
        self.VBO_actors_id = GL.glGenBuffers(1)
        self.VBO_actors_elements_id = GL.glGenBuffers(1)

        # Construct the data arrays that will be loaded into the buffer
        vertexData = []
        colorData = []
        normalsData = []
        elementData = []

        elemOffset = 0
        for obj in self.dynamicObjects:
            vertexData.extend(obj.vertices)
            colorData.extend(obj.colors)
            normalsData.extend(obj.normals)
            for elem in obj.triangleIndices:
                 elementData.append(elem + elemOffset)
            elemOffset += obj.vertexCount

        # for part in self.construct.parts:
        #     vertexData.extend(part.vertexData)
        #     colorData.extend(part.colorData)
        #     normalsData.extend(part.normalsData)
        #     for elem in part.elementData:
        #         elementData.append(elem + elemOffset)
        #     elemOffset = len(elementData)


        # for vTile in self.game.currentLevel.map.visible_tiles:
        #     for actor in vTile.actors:
        #         tile = actor.tile
        #
        #         # Determine scale
        #         if actor is self.game.player:
        #             scale = 0.9
        #         elif isinstance(actor, Portal):
        #             scale = 0.8
        #         elif isinstance(actor, Monster):
        #             scale = 0.7
        #         elif isinstance(actor, Item):
        #             scale = 0.4
        #         else:
        #             scale = 0.2
        #
        #         # Determine height
        #         offset = ((1 - scale) / 2) * TILESIZE
        #         assert isinstance(actor, Actor)
        #         if actor.currentHitPoints > 0:
        #             height = TILESIZE - (2 * offset)
        #         else:
        #             height = 0.05
        #
        #         # Store the vertex coordinates: 4 components per vertex: x, y, z, w
        #         vertexData.extend((tile.x * TILESIZE + offset, tile.y * TILESIZE + offset, 0.0, 1.0))
        #         vertexData.extend((tile.x * TILESIZE + offset, tile.y * TILESIZE + TILESIZE - offset, 0.0, 1.0))
        #         vertexData.extend(
        #             (tile.x * TILESIZE + TILESIZE - offset, tile.y * TILESIZE + TILESIZE - offset, 0.0, 1.0))
        #         vertexData.extend((tile.x * TILESIZE + TILESIZE - offset, tile.y * TILESIZE + offset, 0.0, 1.0))
        #         vertexData.extend((tile.x * TILESIZE + (TILESIZE / 2), tile.y * TILESIZE + (TILESIZE / 2), height, 1.0))
        #
        #         # Store the vertex color: 4 components per color: R, G, B, A
        #         color = self.normalizeColor(actor.color)
        #         colorData.extend((color[0], color[1], color[2], 1.0))
        #         colorData.extend((color[0], color[1], color[2], 1.0))
        #         colorData.extend((color[0], color[1], color[2], 1.0))
        #         colorData.extend((color[0], color[1], color[2], 1.0))
        #         colorData.extend((color[0], color[1], color[2], 1.0))
        #
        #         # Store the vertex normals: 3 components per normal: x, y, z
        #         normalsData.extend((-1.0, 1.0, -0.2))
        #         normalsData.extend((1.0, 1.0, -0.2))
        #         normalsData.extend((1.0, -1.0, -0.2))
        #         normalsData.extend((-1.0, -1.0, -0.2))
        #         normalsData.extend((0.0, 0.0, -1.0))
        #
        #         # Store the indices for the element drawing (triangles, clockwise from front)
        #         elementData.extend((0 + elemOffset, 2 + elemOffset, 1 + elemOffset))
        #         elementData.extend((0 + elemOffset, 3 + elemOffset, 2 + elemOffset))
        #         elementData.extend((0 + elemOffset, 4 + elemOffset, 3 + elemOffset))
        #         elementData.extend((3 + elemOffset, 4 + elemOffset, 2 + elemOffset))
        #         elementData.extend((2 + elemOffset, 4 + elemOffset, 1 + elemOffset))
        #         elementData.extend((1 + elemOffset, 4 + elemOffset, 0 + elemOffset))
        #         elemOffset += 5

        # Remember where each data set begins
        self.VBO_actors_color_offset = len(vertexData)
        vertexData.extend(colorData)
        self.VBO_actors_normals_offset = len(vertexData)
        vertexData.extend(normalsData)
        self.VBO_actors_length = len(vertexData)
        self.VBO_actors_elements_length = len(elementData)

        # Set up the VAO context
        GL.glUseProgram(self.openGlProgram)
        glBindVertexArray(self.VAO_actors)

        # Load the constructed vertex data array into the created array buffer
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO_actors_id)
        array_type = (GL.GLfloat * len(vertexData))
        GL.glBufferData(GL.GL_ARRAY_BUFFER, len(vertexData) * SIZE_OF_FLOAT, array_type(*vertexData), GL.GL_STATIC_DRAW)
        # Enable Vertex inputs and define pointer
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, None)
        # Enable Color inputs and define pointer
        GL.glEnableVertexAttribArray(1)
        colorDataStart = self.VBO_actors_color_offset * SIZE_OF_FLOAT
        GL.glVertexAttribPointer(1, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, c_void_p(colorDataStart))
        # Enable Normals inputs and define pointer
        GL.glEnableVertexAttribArray(2)
        normalsDataStart = self.VBO_actors_normals_offset * SIZE_OF_FLOAT
        GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, False, 0, c_void_p(normalsDataStart))

        # Load the constructed element data array into the created element array buffer
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.VBO_actors_elements_id)
        array_type = (GL.GLint * len(elementData))
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, len(elementData) * SIZE_OF_FLOAT, array_type(*elementData),
                        GL.GL_STATIC_DRAW)

        # Done
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glUseProgram(0)

    def drawVBAs(self):
        DEBUG_GLSL = False
        if DEBUG_GLSL: print '\n\nDEBUG MODE: Simulating GLSL calculation:\n'

        GL.glUseProgram(self.openGlProgram)

        # Bind Level VAO context
        glBindVertexArray(self.VAO_level)
        # Load uniforms
        GL.glUniformMatrix4fv(self.perspectiveMatrixUnif, 1, GL.GL_FALSE, np.reshape(self.perspectiveMatrix, (16)))
        if DEBUG_GLSL: print "perspectiveMatrix"
        if DEBUG_GLSL: print self.perspectiveMatrix

        camMatrix = np.linalg.inv(self.cameraMatrix)
        GL.glUniformMatrix4fv(self.cameraMatrixUnif, 1, GL.GL_FALSE, np.reshape(camMatrix, (16)))
        if DEBUG_GLSL: print "camMatrix"
        if DEBUG_GLSL: print camMatrix

        lightMatrix = camMatrix[:3, :3]  # Extracts 3*3 matrix out of 4*4
        if DEBUG_GLSL: print "LightMatrix"
        if DEBUG_GLSL: print lightMatrix
        GL.glUniformMatrix3fv(self.lightingMatrixUnif, 1, GL.GL_FALSE, np.reshape(lightMatrix, (9)))

        if DEBUG_GLSL: print "Light position: " + self.lightPosition
        GL.glUniform3f(self.lightPosUnif, self.lightPosition[0], self.lightPosition[1], self.lightPosition[2])
        if DEBUG_GLSL: print "Light intensity: (0.8, 0.8, 0.8, 1.0)"
        GL.glUniform4f(self.lightIntensityUnif, 0.8, 0.8, 0.8, 1.0)
        if DEBUG_GLSL: print "Ambient intensity: (0.2, 0.2, 0.2, 1.0)"
        GL.glUniform4f(self.ambientIntensityUnif, 0.2, 0.2, 0.2, 1.0)

        GL.glUniform4f(self.playerPositionUnif, *self.getPlayerPosition())
        GL.glUniform1i(self.fogActiveUnif, 1 if self.fogActive else 0)

        # Bind element array
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.VBO_level_elements_id)
        # Draw elements
        GL.glDrawElements(GL.GL_TRIANGLES, self.VBO_level_elements_length, GL.GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        # Bind Actors VAO context
        glBindVertexArray(self.VAO_actors)
        # Load uniforms
        GL.glUniformMatrix4fv(self.perspectiveMatrixUnif, 1, GL.GL_FALSE, np.reshape(self.perspectiveMatrix, (16)))

        camMatrix = np.linalg.inv(self.cameraMatrix)
        GL.glUniformMatrix4fv(self.cameraMatrixUnif, 1, GL.GL_FALSE, np.reshape(camMatrix, (16)))

        lightMatrix = camMatrix[:3, :3]  # Extracts 3*3 matrix out of 4*4
        GL.glUniformMatrix3fv(self.lightingMatrixUnif, 1, GL.GL_FALSE, np.reshape(lightMatrix, (9)))

        GL.glUniform3f(self.lightPosUnif, self.lightPosition[0], self.lightPosition[1], self.lightPosition[2])
        GL.glUniform4f(self.lightIntensityUnif, 0.8, 0.8, 0.8, 1.0)
        GL.glUniform4f(self.ambientIntensityUnif, 0.2, 0.2, 0.2, 1.0)
        GL.glUniform4f(self.playerPositionUnif, *self.getPlayerPosition())

        # Bind element array
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.VBO_actors_elements_id)
        # Draw elements
        GL.glDrawElements(GL.GL_TRIANGLES, self.VBO_actors_elements_length, GL.GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        GL.glUseProgram(0)


    def normalizeColor(self, color):
        return (float(color[0]) / 250, float(color[1]) / 250, float(color[2]) / 250)

    def setDrawColor(self, color):
        GL.glColor3f(*self.normalizeColor(color))

    def drawText(self, position, textString, textSize):
        font = pygame.font.Font(None, textSize)
        textSurface = font.render(textString, True, (255, 255, 255, 255))  # , (0,0,0,255))
        textData = pygame.image.tostring(textSurface, "RGBA", True)
        GL.glRasterPos3d(*position)
        GL.glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, textData)

    def drawHUD(self):
        """
        For the HUD we use an Orthographic projection and some older style opengl code
        This is not using Vertex Buffers.
        """
        # Switch to Orthographic projection
        GL.glOrtho(0.0, self.displayWidth, self.displayHeight, 0.0, -1.0, 10.0)

        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)

        # Level name
        GL.glLoadIdentity()
        self.drawText((-0.98, 0.9, 0), "Wuuut!", 24)

        # Player name
        GL.glLoadIdentity()
        self.drawText((-0.98, -0.85, 0), "Player" + " (Lvl ?)", 18)

        # Health Bar
        GL.glLoadIdentity()
        GL.glTranslatef(-0.98, -0.94, 0)
        current = 80 #self.game.player.currentHitPoints
        maximum = 100 #self.game.player.maxHitPoints
        barWidth = 0.46
        barHeight = 0.08
        GL.glBegin(GL.GL_QUADS);
        self.setDrawColor(pg_util.COLOR_BAR_HEALTH_BG)
        # Draw vertices (counter clockwise for face culling!)
        GL.glVertex2f(barWidth, 0.0)
        GL.glVertex2f(barWidth, barHeight)
        GL.glVertex2f(0.0, barHeight)
        GL.glVertex2f(0.0, 0.0)
        GL.glEnd()
        if current > 0:
            filWidth = current * barWidth / maximum
            GL.glBegin(GL.GL_QUADS);
            self.setDrawColor(pg_util.COLOR_BAR_HEALTH)
            # Draw vertices (counter clockwise for face culling!)
            GL.glVertex2f(filWidth, 0.0)
            GL.glVertex2f(filWidth, barHeight)
            GL.glVertex2f(0.0, barHeight)
            GL.glVertex2f(0.0, 0.0)
            GL.glEnd()

        # Xp Bar
        GL.glLoadIdentity()
        GL.glTranslatef(-0.98, -0.99, 0)
        current = 99 #self.game.player.xp
        maximum = 111 #self.game.player.nextLevelXp
        barWidth = 0.46
        barHeight = 0.04
        GL.glBegin(GL.GL_QUADS);
        self.setDrawColor(pg_util.COLOR_BAR_XP_BG)
        # Draw vertices (counter clockwise for face culling!)
        GL.glVertex2f(barWidth, 0.0)
        GL.glVertex2f(barWidth, barHeight)
        GL.glVertex2f(0.0, barHeight)
        GL.glVertex2f(0.0, 0.0)
        GL.glEnd()
        if current > 0:
            filWidth = current * barWidth / maximum
            GL.glBegin(GL.GL_QUADS);
            self.setDrawColor(pg_util.COLOR_BAR_XP)
            # Draw vertices (counter clockwise for face culling!)
            GL.glVertex2f(filWidth, 0.0)
            GL.glVertex2f(filWidth, barHeight)
            GL.glVertex2f(0.0, barHeight)
            GL.glVertex2f(0.0, 0.0)
            GL.glEnd()

        # FPS
        GL.glLoadIdentity()
        self.drawText((-0.98, -1, 0), str(self.FPS), 12)

        # # Right side: render game messages
        # GL.glLoadIdentity()
        # widthOffset = 200
        # heightOffset = 100
        # messageCounter = 1
        # nbrOfMessages = len(self.game.messageBuffer)
        # while heightOffset > 0:
        #     if messageCounter > nbrOfMessages: break
        #     # get messages from game message buffer, starting from the back
        #     message = self.game.messageBuffer[nbrOfMessages - messageCounter]
        #     #create textLines for message
        #     textLines = pg_util.wrap_multi_line(message, pg_util.FONT_PANEL, 800 - widthOffset)
        #     nbrOfLines = len(textLines)
        #     #blit the lines
        #     for l in range(1, nbrOfLines + 1):
        #         textSurface = pg_util.FONT_PANEL.render(textLines[nbrOfLines - l], 1,
        #                                                      pg_util.COLOR_PANEL_FONT)
        #         heightOffset = heightOffset - 2 * textSurface.get_height()
        #         textData = pygame.image.tostring(textSurface, "RGBA", True)
        #         GL.glRasterPos3d(-0.5, -0.88 - (heightOffset / 600.), 0)
        #         GL.glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL.GL_RGBA, GL.GL_UNSIGNED_BYTE,
        #                         textData)
        #
        #     messageCounter += 1

    def handlePyGameEvent(self, event):
        # Quit
        if event.type == pygame.QUIT:
            sys.exit()

        # Window resize
        elif event.type == VIDEORESIZE:
            self.resizeWindow(event.dict['size'])

        # mouse
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.eventDraggingStart()
            elif event.button == 3:
                self.eventRotatingStart()
            elif event.button == 4:
                self.eventZoomIn()
            elif event.button == 5:
                self.eventZoomOut()
        elif event.type == MOUSEMOTION:
            self.eventMouseMovement()
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.eventDraggingStop()
            elif event.button == 3:
                self.eventRotatingStop()

        # keyboard
        elif event.type == pygame.KEYDOWN:
            # Handle keys that are always active
            if event.key == pygame.K_ESCAPE:
                sys.exit()
            elif event.key == pygame.K_p:
                self.centerCameraOnActor(self.game.player)
            elif event.key == pygame.K_m:
                self.centerCameraOnMap()
            elif event.key == pygame.K_o:
                self.firstPersonCamera()
            # elif event.key == pygame.K_SPACE:
            #     self.construct.grow()

    def eventDraggingStart(self):
        self._dragging = True
        # call pygame.mouse.get_rel() to make pygame correctly register the starting point of the drag
        pygame.mouse.get_rel()

    def eventDraggingStop(self):
        self._dragging = False

    def eventRotatingStart(self):
        self._rotating = True
        # call pygame.mouse.get_rel() to make pygame correctly register the starting point of the drag
        pygame.mouse.get_rel()

    def eventRotatingStop(self):
        self._rotating = False

    def eventMouseMovement(self):
        # check for on going drag
        if self._dragging:
            # get relative distance of mouse since last call to get_rel()
            mouseMove = pygame.mouse.get_rel()

            # Get the left right direction of the camera from the current modelview matrix
            x = self.cameraMatrix[0, 0]
            y = self.cameraMatrix[1, 0]
            z = self.cameraMatrix[2, 0]
            w = self.cameraMatrix[3, 0]
            factor = -1.0 * mouseMove[0] / (w * w)
            # Translate along this direction
            translation_matrix = og_util.translationMatrix44(factor * x, factor * y, factor * z)
            self.cameraMatrix = translation_matrix.dot(self.cameraMatrix)

            # Get the up down direction of the camera from the current modelview matrix
            x = self.cameraMatrix[0, 1]
            y = self.cameraMatrix[1, 1]
            z = self.cameraMatrix[2, 1]
            w = self.cameraMatrix[3, 1]
            factor = 1.0 * mouseMove[1] / (w * w)
            print self.cameraMatrix[:, 1]
            # Translate along this direction
            translation_matrix = og_util.translationMatrix44(factor * x, factor * y, factor * z)
            self.cameraMatrix = translation_matrix.dot(self.cameraMatrix)

        elif self._rotating:
            # get relative distance of mouse since last call to get_rel()
            mouseMove = pygame.mouse.get_rel()

            # Get the left right direction of the camera from the current modelview matrix
            # We'll use this as the rotation axis for the up down movement
            x = self.cameraMatrix[0, 0] * mouseMove[1]
            y = self.cameraMatrix[1, 0] * mouseMove[1]
            z = self.cameraMatrix[2, 0] * mouseMove[1]
            w = self.cameraMatrix[3, 0] * 100
            rotation_matrix = og_util.rotationMatrix44(x / w, y / w, z / w)
            self.cameraMatrix = rotation_matrix.dot(self.cameraMatrix)

            # Get the up down direction of the camera from the current modelview matrix
            # We'll use this as the rotation axis for the left right movement
            x = self.cameraMatrix[0, 1] * -1.0 * mouseMove[0]
            y = self.cameraMatrix[1, 1] * -1.0 * mouseMove[0]
            z = self.cameraMatrix[2, 1] * -1.0 * mouseMove[0]
            w = self.cameraMatrix[3, 1] * 100
            rotation_matrix = og_util.rotationMatrix44(x / w, y / w, z / w)
            self.cameraMatrix = rotation_matrix.dot(self.cameraMatrix)

    def eventZoomIn(self):
        """
        Event handler for ZoomIn event.
        This will translate the camera matrix to zoom in.
        """
        # Get the direction of the camera from the camera matrix
        heading = self.cameraMatrix[:3, 2] * -1  # backward
        # Translate the camera along z component of this direction
        translation_matrix = og_util.translationMatrix44(0., 0., heading[2])
        self.cameraMatrix = translation_matrix.dot(self.cameraMatrix)

    def eventZoomOut(self):
        """
        Event handler for ZoomOut event.
        This will translate the camera matrix to zoom out.
        """
        # Get the direction of the camera from the camera matrix
        heading = self.cameraMatrix[:3, 2]  # Forward
        # Translate the camera along z component of this direction
        translation_matrix = og_util.translationMatrix44(0., 0., heading[2])
        self.cameraMatrix = translation_matrix.dot(self.cameraMatrix)


if __name__ == '__main__':
    #This is where it all starts!
    _application = GlApplication()
    _application.showMainMenu()