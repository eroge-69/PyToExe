import maya.standalone
maya.standalone.initialize(name='python')

import maya.cmds as cmds
import os

def get_user_cameras():
    default_cams = {"persp", "top", "front", "side"}
    user_cams = []
    for cam_shape in cmds.ls(type="camera"):
        cam_transform = cmds.listRelatives(cam_shape, parent=True, fullPath=True)[0]
        if cam_transform.split("|")[-1] not in default_cams:
            user_cams.append((cam_transform, cam_shape))
    return user_cams

def copy_focal_length(source, target):
    attr = "focalLength"
    try:
        if cmds.listConnections(f"{source}.{attr}", s=True, d=False):
            cmds.copyKey(source, at=attr)
            cmds.pasteKey(target, at=attr, option="replace")
        else:
            val = cmds.getAttr(f"{source}.{attr}")
            cmds.setAttr(f"{target}.{attr}", val)
    except:
        pass

def copy_film_back(source, target):
    attrs = [
        "filmFit", "horizontalFilmAperture", "verticalFilmAperture",
        "horizontalFilmOffset", "verticalFilmOffset",
        "lensSqueezeRatio", "cameraScale", "filmFitOffset"
    ]
    for attr in attrs:
        try:
            val = cmds.getAttr(f"{source}.{attr}")
            cmds.setAttr(f"{target}.{attr}", val)
        except:
            pass

def process_scene(scene_path):
    if not os.path.exists(scene_path):
        print(f"[ERROR] Scene not found: {scene_path}")
        return

    cmds.file(scene_path, open=True, force=True)

    scene_name = os.path.splitext(os.path.basename(scene_path))[0]
    scene_dir = os.path.dirname(scene_path)

    user_cams = get_user_cameras()
    if not user_cams:
        print(f"[SKIP] No user cameras found in {scene_path}")
        return

    source_transform, source_shape = user_cams[0]  # Only 1st cam for now

    new_cam_name = f"{scene_name}_cam"
    new_transform, new_shape = cmds.camera()
    new_transform = cmds.rename(new_transform, new_cam_name)
    new_shape = cmds.listRelatives(new_transform, shapes=True)[0]

    # Constraints
    point_con = cmds.pointConstraint(source_transform, new_transform, offset=(0, 0, 0), weight=1)[0]
    orient_con = cmds.orientConstraint(source_transform, new_transform, offset=(0, 0, 0), weight=1)[0]

    # Copy attributes
    copy_focal_length(source_shape, new_shape)
    copy_film_back(source_shape, new_shape)

    # Bake simulation
    start = cmds.playbackOptions(q=True, min=True)
    end = cmds.playbackOptions(q=True, max=True)
    cmds.bakeResults(
        new_transform,
        t=(start, end),
        simulation=True,
        hierarchy="below",
        sampleBy=1,
        disableImplicitControl=True,
        preserveOutsideKeys=True,
        sparseAnimCurveBake=False,
        removeBakedAttributeFromLayer=False,
        bakeOnOverrideLayer=False,
        minimizeRotation=True,
        at=["translate", "rotate"]
    )

    cmds.delete([point_con, orient_con])

    # FBX export
    if not cmds.pluginInfo("fbxmaya", q=True, loaded=True):
        cmds.loadPlugin("fbxmaya")

    cmds.select(new_transform)
    export_path = os.path.join(scene_dir, new_cam_name + ".fbx")
    cmds.file(export_path, force=True, options="v=0;", typ="FBX export", es=True)

    print(f"[OK] Exported FBX: {export_path}")

def batch_process_scenes(folder_path):
    files = [f for f in os.listdir(folder_path) if f.lower().endswith((".ma", ".mb"))]
    for file in files:
        full_path = os.path.join(folder_path, file)
        print(f"[...] Processing: {file}")
        process_scene(full_path)

# Entry point for mayapy execution
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        folder = sys.argv[1]
        batch_process_scenes(folder)
    else:
        print("[ERROR] No folder path provided.")
