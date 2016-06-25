# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from UM.Mesh.MeshData import MeshData
from UM.Mesh.MeshData import MeshType
from UM.Math.Vector import Vector
from UM.Math.Matrix import Matrix
from UM.Logger import Logger

import numpy
import math
from time import time

##  Builds new meshes by adding primitives.
#
#   This class functions in much the same way as a normal StringBuilder would.
#   Each instance of MeshBuilder creates one mesh. This mesh starts empty, but
#   you can add primitives to it via the various methods of this class. The
#   result can then be converted to a normal mesh.
class MeshBuilder:
    ##  Creates a new MeshBuilder with an empty mesh.
    def __init__(self):
        self._vertices = None
        self._normals = None
        self._indices = None
        self._colors = None
        self._uvs = None
        self._vertex_count = 0
        self._face_count = 0
        self._type = MeshType.faces
        self._file_name = None
        # original center position
        self._center_position = None

    ##  Build a MeshData object.
    #
    #   \return A Mesh data.
    def build(self):
        return MeshData(vertices=self.getVertices(), normals=self.getNormals(), indices=self.getIndices(),
                        colors=self.getColors(), uvs=self.getUVCoordinates(), file_name=self.getFileName(),
                        center_position=self.getCenterPosition())

    def setCenterPosition(self, position):
        self._center_position = position

    def getCenterPosition(self):
        return self._center_position

    ##  Set the type of the mesh
    #   \param mesh_type MeshType enum
    def setType(self, mesh_type):
        if isinstance(mesh_type, MeshType):
            self._type = mesh_type

    def getType(self):
        return self._type

    def getFaceCount(self):
        return self._face_count

    ##  Get the array of vertices
    def getVertices(self):
        if self._vertices is None:
            return None

        return self._vertices[0 : self._vertex_count] #Only return up until point where data was filled

    ##  Get the number of vertices
    def getVertexCount(self):
        return self._vertex_count

    ##  Get a vertex by index
    def getVertex(self, index):
        try:
            return self._vertices[index]
        except IndexError:
            return None

    #   Remove vertex by index or list of indices
    #   \param index Either a single index or a list of indices to be removed.
    def removeVertex(self, index):
        try:
            #print("deleting ", index)
            #print( self._vertices)
            self._vertices = numpy.delete(self._vertices, index,0)
            if self.hasNormals():
               self._normals = numpy.delete(self._normals,index,0)
            #print( self._vertices)
            self._vertex_count = len(self._vertices)
        except IndexError:
            pass
        # self._dataChanged()

    ##  Return whether this mesh has vertex normals.
    def hasNormals(self):
        return self._normals is not None

    ##  Return the list of vertex normals.
    def getNormals(self):
        if self._normals is None:
            return None

        return self._normals[0:self._vertex_count]

    ##  Return whether this mesh has indices.
    def hasIndices(self):
        return self._indices is not None

    ##  Get the array of indices
    #   \return \type{numpy.ndarray}
    def getIndices(self):
        if self._indices is None:
            return None

        return self._indices[0:self._face_count]

    def hasColors(self):
        return self._colors is not None

    def getColors(self):
        if self._colors is None:
            return None

        return self._colors[0:self._vertex_count]

    def hasUVCoordinates(self):
        return self._uvs is not None

    def getUVCoordinates(self):
        if self._uvs is None:
            return None
        return self._uvs[0 : self._vertex_count]

    def getFileName(self):
        return self._file_name

    def setFileName(self, file_name):
        self._file_name = file_name

    ##  Set the amount of faces before loading data to the mesh.
    #
    #   This way we can create the array before we fill it. This method will reserve
    #   `(num_faces * 3)` amount of space for vertices, `(num_faces * 3)` amount of space
    #   for normals and `num_faces` amount of space for indices.
    #
    #   \param num_faces Number of faces for which memory must be reserved.
    def reserveFaceCount(self, num_faces):
        if type(num_faces) == float:
            Logger.log("w", "Had to convert 'num_faces' with int(): %s -> %s ", num_faces, int(num_faces))
            num_faces = int(num_faces)

        self._vertices = numpy.zeros((num_faces * 3, 3), dtype=numpy.float32)
        self._normals = numpy.zeros((num_faces * 3, 3), dtype=numpy.float32)
        self._indices = numpy.zeros((num_faces, 3), dtype=numpy.int32)

        self._vertex_count = 0
        self._face_count = 0

    ##  Preallocate space for vertices before loading data to the mesh.
    #
    #   This way we can create the array before we fill it. This method will reserve
    #   `num_vertices` amount of space for vertices. It deletes any existing normals
    #   and indices but does not reserve space for them.
    #
    #   \param num_vertices Number of verts to be reserved.
    def reserveVertexCount(self, num_vertices):
        self._vertices = numpy.zeros((num_vertices, 3), dtype=numpy.float32)
        self._normals = None
        self._indices = None

        self._vertex_count = 0
        self._face_count = 0

    ##  Add a vertex to the mesh.
    #   \param x x coordinate of vertex.
    #   \param y y coordinate of vertex.
    #   \param z z coordinate of vertex.
    def addVertex(self, x, y, z):
        if self._vertices is None:
            self._vertices = numpy.zeros((10, 3), dtype=numpy.float32)

        if len(self._vertices) == self._vertex_count:
            self._vertices.resize((self._vertex_count * 2, 3))

        self._vertices[self._vertex_count, 0] = x
        self._vertices[self._vertex_count, 1] = y
        self._vertices[self._vertex_count, 2] = z
        self._vertex_count += 1

    ##  Add a vertex to the mesh.
    #   \param x x coordinate of vertex.
    #   \param y y coordinate of vertex.
    #   \param z z coordinate of vertex.
    #   \param nx x part of normal.
    #   \param ny y part of normal.
    #   \param nz z part of normal.
    def addVertexWithNormal(self, x, y, z, nx, ny, nz):
        if self._vertices is None:
            self._vertices = numpy.zeros((10, 3), dtype=numpy.float32)
        if self._normals is None: #Specific case, reserve vert count does not reservere size for normals
            self._normals = numpy.zeros((10, 3), dtype=numpy.float32)

        if len(self._vertices) == self._vertex_count:
            self._vertices.resize((self._vertex_count * 2, 3))

        if self._normals is None:
            self._normals = numpy.zeros((self._vertex_count, 3), dtype=numpy.float32)

        if len(self._normals) == self._vertex_count:
            self._normals.resize((self._vertex_count * 2, 3))

        self._vertices[self._vertex_count, 0] = x
        self._vertices[self._vertex_count, 1] = y
        self._vertices[self._vertex_count, 2] = z
        self._normals[self._vertex_count, 0] = nx
        self._normals[self._vertex_count, 1] = ny
        self._normals[self._vertex_count, 2] = nz
        self._vertex_count += 1

    ##  Add a face by providing three verts.
    #   \param x0 x coordinate of first vertex.
    #   \param y0 y coordinate of first vertex.
    #   \param z0 z coordinate of first vertex.
    #   \param x1 x coordinate of second vertex.
    #   \param y1 y coordinate of second vertex.
    #   \param z1 z coordinate of second vertex.
    #   \param x2 x coordinate of third vertex.
    #   \param y2 y coordinate of third vertex.
    #   \param z2 z coordinate of third vertex.
    def addFaceByPoints(self, x0, y0, z0, x1, y1, z1, x2, y2, z2):
        if self._indices is None:
            self._indices = numpy.zeros((10, 3), dtype=numpy.int32)

        if len(self._indices) == self._face_count:
            self._indices.resize((self._face_count * 2, 3))

        self._indices[self._face_count, 0] = self._vertex_count
        self._indices[self._face_count, 1] = self._vertex_count + 1
        self._indices[self._face_count, 2] = self._vertex_count + 2
        self._face_count += 1

        self.addVertex(x0, y0, z0)
        self.addVertex(x1, y1, z1)
        self.addVertex(x2, y2, z2)

    ##  Add a face by providing three vertices and the normals that go with those vertices.
    #
    #   \param x0 The X coordinate of the first vertex.
    #   \param y0 The Y coordinate of the first vertex.
    #   \param z0 The Z coordinate of the first vertex.
    #   \param nx0 The X coordinate of the normal of the first vertex.
    #   \param ny0 The Y coordinate of the normal of the first vertex.
    #   \param nz0 The Z coordinate of the normal of the first vertex.
    #
    #   \param x1 The X coordinate of the second vertex.
    #   \param y1 The Y coordinate of the second vertex.
    #   \param z1 The Z coordinate of the second vertex.
    #   \param nx1 The X coordinate of the normal of the second vertex.
    #   \param ny1 The Y coordinate of the normal of the second vertex.
    #   \param nz1 The Z coordinate of the normal of the second vertex.
    #
    #   \param x2 The X coordinate of the third vertex.
    #   \param y2 The Y coordinate of the third vertex.
    #   \param z2 The Z coordinate of the third vertex.
    #   \param nx2 The X coordinate of the normal of the third vertex.
    #   \param ny2 The Y coordinate of the normal of the third vertex.
    #   \param nz2 The Z coordinate of the normal of the third vertex.
    def addFaceWithNormals(self,x0, y0, z0, nx0, ny0, nz0, x1, y1, z1, nx1, ny1, nz1, x2, y2, z2, nx2, ny2, nz2):
        if self._indices is None:
            self._indices = numpy.zeros((10, 3), dtype=numpy.int32)

        if len(self._indices) == self._face_count:
            self._indices.resize((self._face_count * 2, 3))

        self._indices[self._face_count, 0] = self._vertex_count
        self._indices[self._face_count, 1] = self._vertex_count + 1
        self._indices[self._face_count, 2] = self._vertex_count + 2
        self._face_count += 1

        self.addVertexWithNormal(x0, y0, z0, nx0, ny0, nz0)
        self.addVertexWithNormal(x1, y1, z1, nx1, ny1, nz1)
        self.addVertexWithNormal(x2, y2, z2, nx2, ny2, nz2)

    ##  Sets the color for a vertex
    #
    #   \param index \type{int} the index of the vertex in the vertices array.
    #   \param color \type{UM.Math.Color} the color of the vertex.
    def setVertexColor(self, index, color):
        if self._colors is None:
            self._colors = numpy.zeros((10, 4), dtype=numpy.float32)

        if len(self._colors) < len(self._vertices):
            self._colors.resize((len(self._vertices), 4))

        self._colors[index, 0] = color.r
        self._colors[index, 1] = color.g
        self._colors[index, 2] = color.b
        self._colors[index, 3] = color.a

    def setVertexUVCoordinates(self, index, u, v):
        if self._uvs is None:
            self._uvs = numpy.zeros((10, 2), dtype=numpy.float32)

        if len(self._uvs) < len(self._vertices):
            self._uvs.resize((len(self._vertices), 2))

        self._uvs[index, 0] = u
        self._uvs[index, 1] = v

    def addVertices(self, vertices):
        if self._vertices is None:
            self._vertices = vertices
            self._vertex_count = len(vertices)
        else:
            self._vertices = numpy.concatenate((self._vertices[0:self._vertex_count], vertices))
            self._vertex_count  += len(vertices)

    def addIndices(self, indices):
        if self._indices is None:
            self._indices = indices
            self._face_count = len(indices)
        else:
            self._indices = numpy.concatenate((self._indices[0:self._face_count], indices))
            self._face_count += len(indices)

    def addColors(self, colors):
        if self._colors is None:
            self._colors = colors
        else:
            self._colors = numpy.concatenate((self._colors[0:self._vertex_count], colors))

    ##
    # /param colors is a vertexCount by 4 numpy array with floats in range of 0 to 1.
    def setColors(self, colors):
        self._colors = colors

    ##  Calculate the normals of this mesh, assuming it was created by using addFace (eg; the verts are connected)
    #
    #   Keyword arguments:
    #   - fast: A boolean indicating whether or not to use a fast method of normal calculation that assumes each triangle
    #           is stored as a set of three unique vertices.
    def calculateNormals(self, **kwargs):
        if self._vertices is None:
            return
        start_time = time()
        # Numpy magic!
        # First, reset the normals
        self._normals = numpy.zeros((self._vertex_count, 3), dtype=numpy.float32)

        if self.hasIndices() and not kwargs.get("fast", False):
            for face in self._indices[0:self._face_count]:
                #print(self._vertices[face[0]])
                #print(self._vertices[face[1]])
                #print(self._vertices[face[2]])
                self._normals[face[0]] = numpy.cross(self._vertices[face[0]] - self._vertices[face[1]], self._vertices[face[0]] - self._vertices[face[2]])
                length = numpy.linalg.norm(self._normals[face[0]])
                self._normals[face[0]] /= length
                self._normals[face[1]] = self._normals[face[0]]
                self._normals[face[2]] = self._normals[face[0]]
        else: #Old way of doing it, asuming that each face has 3 unique verts
            # Then, take the cross product of each pair of vectors formed from a set of three vertices.
            # The [] operator on a numpy array returns itself a numpy array. The slicing syntax is [begin:end:step],
            # so in this case we perform the cross over a two arrays. The first array is built from the difference
            # between every second item in the array starting at two and every third item in the array starting at
            # zero. The second array is built from the difference between every third item in the array starting at
            # two and every third item in the array starting at zero. The cross operation then returns an array of
            # the normals of each set of three vertices.
            n = numpy.cross(self._vertices[1:self._vertex_count:3] - self._vertices[:self._vertex_count:3], self._vertices[2:self._vertex_count:3] - self._vertices[:self._vertex_count:3])
            # We then calculate the length for each normal and perform normalization on the normals.
            l = numpy.linalg.norm(n, axis=1)
            n[:, 0] /= l
            n[:, 1] /= l
            n[:, 2] /= l
            # Finally, we store the normals per vertex, with each face normal being repeated three times, once for
            # every vertex.
            self._normals = n.repeat(3, axis=0)
        end_time = time()
        Logger.log("d", "Calculating normals took %s seconds", end_time - start_time)

    ##  Adds a 3-dimensional line to the mesh of this mesh builder.
    #
    #   \param v0 One endpoint of the line to add.
    #   \param v1 The other endpoint of the line to add.
    #   \param color (Optional) The colour of the line, if any. If no colour is
    #   provided, the colour is determined by the shader.
    def addLine(self, v0, v1, color = None):
        self.addVertex(v0.x, v0.y, v0.z)
        self.addVertex(v1.x, v1.y, v1.z)

        if color: #Add colours to the vertices, if we have them.
            self.setVertexColor(self.getVertexCount() - 2, color)
            self.setVertexColor(self.getVertexCount() - 1, color)

    ##  Adds a triangle to the mesh of this mesh builder.
    #
    #   \param v0 The first corner of the triangle.
    #   \param v1 The second corner of the triangle.
    #   \param v2 The third corner of the triangle.
    #   \param normal (Optional) The normal vector for the triangle. If no
    #   normal vector is provided, it will be calculated automatically.
    #   \param color (Optional) The colour for the triangle. If no colour is
    #   provided, the colour is determined by the shader.
    def addFace(self, v0, v1, v2, normal = None, color = None):
        if normal:
            self.addFaceWithNormals(
                                v0.x, v0.y, v0.z,
                                normal.x, normal.y, normal.z,
                                v1.x, v1.y, v1.z,
                                normal.x, normal.y, normal.z,
                                v2.x, v2.y, v2.z,
                                normal.x, normal.y, normal.z
                            )
        else:
            self.addFaceByPoints(v0.x, v0.y, v0.z, v1.x, v1.y, v1.z, v2.x, v2.y, v2.z) #Computes the normal by itself.

        if color: #Add colours to the vertices if we have them.
            self.setVertexColor(self.getVertexCount() - 3, color)
            self.setVertexColor(self.getVertexCount() - 2, color)
            self.setVertexColor(self.getVertexCount() - 1, color)

    ##  Add a quadrilateral to the mesh of this mesh builder.
    #
    #   The quadrilateral will be constructed as two triangles. v0 and v2 are
    #   the two vertices across the diagonal of the quadrilateral.
    #
    #   \param v0 The first corner of the quadrilateral.
    #   \param v1 The second corner of the quadrilateral.
    #   \param v2 The third corner of the quadrilateral.
    #   \param v3 The fourth corner of the quadrilateral.
    #   \param normal (Optional) The normal vector for the quadrilateral. Both
    #   triangles will get the same normal vector, if provided. If no normal
    #   vector is provided, the normal vectors for both triangles are computed
    #   automatically.
    #   \param color (Optional) The colour for the quadrilateral. If no colour
    #   is provided, the colour is determined by the shader.
    def addQuad(self, v0, v1, v2, v3, normal = None, color = None):
        self.addFace(v0, v2, v1,
            color = color,
            normal = normal
        )
        self.addFace(v0, v3, v2, #v0 and v2 are shared with the other triangle!
            color = color,
            normal = normal
        )

    ##  Add a rectangular cuboid to the mesh of this mesh builder.
    #
    #   A rectangular cuboid is a square block with arbitrary width, height and
    #   depth.
    #
    #   \param width The size of the rectangular cuboid in the X dimension.
    #   \param height The size of the rectangular cuboid in the Y dimension.
    #   \param depth The size of the rectangular cuboid in the Z dimension.
    #   \param center (Optional) The position of the centre of the rectangular
    #   cuboid in space. If not provided, the cuboid is placed at the coordinate
    #   origin.
    #   \param color (Optional) The colour for the rectangular cuboid. If no
    #   colour is provided, the colour is determined by the shader.
    def addCube(self, width, height, depth, center = Vector(0, 0, 0), color = None):
        #Compute the actual positions of the planes.
        minW = -width / 2 + center.x
        maxW = width / 2 + center.x
        minH = -height / 2 + center.y
        maxH = height / 2 + center.y
        minD = -depth / 2 + center.z
        maxD = depth / 2 + center.z

        start = self.getVertexCount()

        verts = numpy.asarray([ #All 8 corners.
            [minW, minH, maxD],
            [minW, maxH, maxD],
            [maxW, maxH, maxD],
            [maxW, minH, maxD],
            [minW, minH, minD],
            [minW, maxH, minD],
            [maxW, maxH, minD],
            [maxW, minH, minD],
        ], dtype=numpy.float32)
        self.addVertices(verts)

        indices = numpy.asarray([ #All 6 quads (12 triangles).
            [start, start + 2, start + 1],
            [start, start + 3, start + 2],

            [start + 3, start + 7, start + 6],
            [start + 3, start + 6, start + 2],

            [start + 7, start + 5, start + 6],
            [start + 7, start + 4, start + 5],

            [start + 4, start + 1, start + 5],
            [start + 4, start + 0, start + 1],

            [start + 1, start + 6, start + 5],
            [start + 1, start + 2, start + 6],

            [start + 0, start + 7, start + 3],
            [start + 0, start + 4, start + 7]
        ], dtype=numpy.int32)
        self.addIndices(indices)

        if color: #If we have a colour, add a colour to all of the vertices.
            vertex_count = self.getVertexCount()
            for i in range(1, 9):
                self.setVertexColor(vertex_count - i, color)

    ##  Add an arc to the mesh of this mesh builder.
    #
    #   An arc is a curve that is also a segment of a circle.
    #
    #   \param radius The radius of the circle this arc is a segment of.
    #   \param axis The axis perpendicular to the plane on which the arc lies.
    #   \param angle (Optional) The length of the arc, in radians. If not
    #   provided, the entire circle is used (2 pi).
    #   \param center (Optional) The position of the centre of the arc in space.
    #   If no position is provided, the arc is centred around the coordinate
    #   origin.
    #   \param sections (Optional) The resolution of the arc. The arc is
    #   approximated by this number of line segments.
    #   \param color (Optional) The colour for the arc. If no colour is
    #   provided, the colour is determined by the shader.
    def addArc(self, radius, axis, angle = math.pi * 2, center = Vector(0, 0, 0), sections = 32, color = None):
        #We'll compute the vertices of the arc by computing an initial point and
        #rotating the initial point with a rotation matrix.
        if axis == Vector.Unit_Y:
            start = axis.cross(Vector.Unit_X).normalized() * radius
        else:
            start = axis.cross(Vector.Unit_Y).normalized() * radius

        angle_increment = angle / sections
        current_angle = 0

        point = start + center
        m = Matrix()
        while current_angle <= angle: #Add each of the vertices.
            self.addVertex(point.x, point.y, point.z)
            current_angle += angle_increment
            m.setByRotationAxis(current_angle, axis)
            point = start.multiply(m) + center #Get the next vertex by rotating the start position with a matrix.
            self.addVertex(point.x, point.y, point.z)

            if color: #If we have a colour, add that colour to the new vertex.
                self.setVertexColor(self.getVertexCount() - 2, color)
                self.setVertexColor(self.getVertexCount() - 1, color)

    ##  Adds a torus to the mesh of this mesh builder.
    #
    #   The torus is the shape of a doughnut. This doughnut is delicious and
    #   moist, but not very healthy.
    #
    #   \param inner_radius The radius of the hole inside the torus. Must be
    #   smaller than outer_radius.
    #   \param outer_radius The radius of the outside of the torus. Must be
    #   larger than inner_radius.
    #   \param width The radius of the torus in perpendicular direction to its
    #   perimeter. This is the "thickness".
    #   \param center (Optional) The position of the centre of the torus. If no
    #   position is provided, the torus will be centred around the coordinate
    #   origin.
    #   \param sections (Optional) The resolution of the torus in the
    #   circumference. The resolution of the intersection of the torus cannot be
    #   changed.
    #   \param color (Optional) The colour of the torus. If no colour is
    #   provided, a colour will be determined by the shader.
    #   \param angle (Optional) An angle of rotation to rotate the torus by, in
    #   radians.
    #   \param axis (Optional) An axis of rotation to rotate the torus around.
    #   If no axis is provided and the angle of rotation is nonzero, the torus
    #   will be rotated around the Y-axis.
    def addDonut(self, inner_radius, outer_radius, width, center = Vector(0, 0, 0), sections = 32, color = None, angle = 0, axis = Vector.Unit_Y):
        vertices = []
        indices = []
        colors = []

        start = self.getVertexCount() #Starting index.

        for i in range(sections):
            v1 = start + i * 3 #Indices for each of the vertices we'll add for this section.
            v2 = v1 + 1
            v3 = v1 + 2
            v4 = v1 + 3
            v5 = v1 + 4
            v6 = v1 + 5

            if i+1 >= sections: # connect the end to the start
                v4 = start
                v5 = start + 1
                v6 = start + 2

            theta = i * math.pi / (sections / 2) #Angle of this piece around torus perimeter.
            c = math.cos(theta) #X-coordinate around torus perimeter.
            s = math.sin(theta) #Y-coordinate around torus perimeter.

            #One vertex on the inside perimeter, two on the outside perimiter (up and down).
            vertices.append( [inner_radius * c, inner_radius * s, 0] )
            vertices.append( [outer_radius * c, outer_radius * s, width] )
            vertices.append( [outer_radius * c, outer_radius * s, -width] )

            #Connect the vertices to the next segment.
            indices.append( [v1, v4, v5] )
            indices.append( [v2, v1, v5] )

            indices.append( [v2, v5, v6] )
            indices.append( [v3, v2, v6] )

            indices.append( [v3, v6, v4] )
            indices.append( [v1, v3, v4] )

            if color: #If we have a colour, add it to the vertices.
                colors.append( [color.r, color.g, color.b, color.a] )
                colors.append( [color.r, color.g, color.b, color.a] )
                colors.append( [color.r, color.g, color.b, color.a] )

        #Rotate the resulting torus around the specified axis.
        matrix = Matrix()
        matrix.setByRotationAxis(angle, axis)
        vertices = numpy.asarray(vertices, dtype = numpy.float32)
        vertices = vertices.dot(matrix.getData()[0:3, 0:3])
        vertices[:] += center.getData() #And translate to the desired position.

        self.addVertices(vertices)
        self.addIndices(numpy.asarray(indices, dtype = numpy.int32))
        self.addColors(numpy.asarray(colors, dtype = numpy.float32))

    ##  Adds a pyramid to the mesh of this mesh builder.
    #
    #   \param width The width of the base of the pyramid.
    #   \param height The height of the pyramid (from base to notch).
    #   \param depth The depth of the base of the pyramid.
    #   \param angle (Optional) An angle of rotation to rotate the pyramid by,
    #   in degrees.
    #   \param axis (Optional) An axis of rotation to rotate the pyramid around.
    #   If no axis is provided and the angle of rotation is nonzero, the pyramid
    #   will be rotated around the Y-axis.
    #   \param center (Optional) The position of the centre of the base of the
    #   pyramid. If not provided, the pyramid will be placed on the coordinate
    #   origin.
    #   \param color (Optional) The colour of the pyramid. If no colour is
    #   provided, a colour will be determined by the shader.
    def addPyramid(self, width, height, depth, angle = 0, axis = Vector.Unit_Y, center = Vector(0, 0, 0), color = None):
        angle = math.radians(angle)

        minW = -width / 2
        maxW = width / 2
        minD = -depth / 2
        maxD = depth / 2

        start = self.getVertexCount() #Starting index.

        matrix = Matrix()
        matrix.setByRotationAxis(angle, axis)
        verts = numpy.asarray([ #All 5 vertices of the pyramid.
            [minW, 0, maxD],
            [maxW, 0, maxD],
            [minW, 0, minD],
            [maxW, 0, minD],
            [0, height, 0]
        ], dtype=numpy.float32)
        verts = verts.dot(matrix.getData()[0:3,0:3]) #Rotate the pyramid around the axis.
        verts[:] += center.getData()
        self.addVertices(verts)

        indices = numpy.asarray([ #Connect the vertices to each other (6 triangles).
            [start, start + 1, start + 4], #The four sides of the pyramid.
            [start + 1, start + 3, start + 4],
            [start + 3, start + 2, start + 4],
            [start + 2, start, start + 4],
            [start, start + 3, start + 1], #The base of the pyramid.
            [start, start + 2, start + 3]
        ], dtype=numpy.int32)
        self.addIndices(indices)

        if color: #If we have a colour, add the colour to each of the vertices.
            vertex_count = self.getVertexCount()
            for i in range(1, 6):
                self.setVertexColor(vertex_count - i, color)
