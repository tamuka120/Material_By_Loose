bl_info = {
    "name": "MXL",
    "description": "Randomly assign material by loose geometry",
    "blender": (2, 80, 0),
    "category": "Object",
    "author": "Madlaina Kalunder/Aadjou",
    "version": (1, 0),
    "warning": "BSD",
    "location": "Right side panel > \"MXL\" tab",
    "wiki_url": "https://github.com/Aadjou/blender-scripts",
    "support": "COMMUNITY",
}

import bpy
import bmesh
import random
from math import trunc

class MXL(bpy.types.Operator):
    bl_idname = "node.mxl_op"
    bl_label = "MXL"
    bl_options = {'REGISTER', 'UNDO'}
    examined = set()

    def getLinkedFaces(self, face):
        face.tag = False
        if face.tag:
            # If the face is already tagged, return empty list
            return []

        # Add the face to list that will be returned
        result = [face]
        face.tag = True

        # Select edges that link two faces
        edges = [edge for edge in face.edges if len(edge.link_faces) == 2]

        for edge in edges:

            # Select all first-degree linked faces, that are not yet tagged
            faces = [elem for elem in edge.link_faces if not elem.tag]

            # Recursively call this function on all connected faces
            if not len(faces) == 0:
                for elem in faces:

                    # Extend the list with second-degree connected faces
                    result.extend(self.getLinkedFaces(elem))

        # Save result to list of found faces
        self.examined.update(result)

        return result

    def execute(self, context):
        mesh = None
        islands = []
        obj = context.object

        if obj.mode == 'OBJECT':
            mesh = bmesh.new()
            mesh.from_mesh(obj.data)
        else:
            mesh = bmesh.from_edit_mesh(obj.data)

        mesh.faces.ensure_lookup_table()
        mesh.verts.ensure_lookup_table()

        # Get islands from list of mesh faces
        for face in mesh.faces:
            if face in self.examined:
                continue

            links = self.getLinkedFaces(face)
            islands.append(links)

        # For each island assign a random material index
        for island in islands:
            index = trunc(random.uniform(0, len(obj.data.materials)))
            for face in island:
                face.material_index = index

        # update the object's mesh from the bmesh
        if obj.mode == 'OBJECT':
            mesh.to_mesh(obj.data)
            mesh.free()
        else:
            bmesh.update_edit_mesh(obj.data)
        
        self.report({'INFO'}, "MXL Operation: Complete")
        return {'FINISHED'}
    
class MXL_PT_MXL_Panel(bpy.types.Panel):
    bl_idname = "MXL_PT_MXL_Panel"
    bl_label = "MXL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MXL"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Apply Random Material")
        
        # Draw Button
        row = layout.row()
        row.operator(MXL.bl_idname, text="Apply MXL", icon = "MATERIAL_DATA")

classes = (
    MXL_PT_MXL_Panel, 
    MXL)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
