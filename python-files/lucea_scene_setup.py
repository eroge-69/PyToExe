
import bpy

# Yeni sahne
bpy.ops.wm.read_factory_settings(use_empty=True)

# Kamera ekle
bpy.ops.object.camera_add(location=(0, -6, 2), rotation=(1.2, 0, 0))
camera = bpy.context.active_object
bpy.context.scene.camera = camera

# Işık ekle (ambient)
bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
light = bpy.context.active_object
light.data.energy = 1500

# Basit salon zemini
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.active_object
mat_floor = bpy.data.materials.new(name="FloorMaterial")
mat_floor.use_nodes = True
bsdf = mat_floor.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.9, 0.85, 0.8, 1)
floor.data.materials.append(mat_floor)

# Basit koltuk (placeholder cube)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 2, 1))
sofa = bpy.context.active_object
mat_sofa = bpy.data.materials.new(name="SofaMaterial")
mat_sofa.use_nodes = True
bsdf = mat_sofa.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.3, 0.2, 0.1, 1)
sofa.data.materials.append(mat_sofa)

# Avize (basit silindir placeholder)
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.5, location=(0, 0, 3))
chandelier = bpy.context.active_object
mat_chandelier = bpy.data.materials.new(name="ChandelierMaterial")
mat_chandelier.use_nodes = True
bsdf = mat_chandelier.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.9, 0.8, 0.5, 1)
chandelier.data.materials.append(mat_chandelier)

# Kamera animasyonu (frame 1 -> frame 180)
camera.location = (0, -6, 2)
camera.keyframe_insert(data_path="location", frame=1)
camera.location = (0, -3, 1.5)
camera.keyframe_insert(data_path="location", frame=180)

# Render ayarları
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 64
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.fps = 30
bpy.context.scene.frame_end = 180

print("Sahne hazır. Lütfen Blender içinde scripti çalıştırın.")
