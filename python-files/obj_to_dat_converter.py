def convert_obj_to_dat(obj_path, dat_path):
    """
    Converts a Wavefront .OBJ file to a simple .DAT format.
    The .DAT format will contain only vertex and face data.
    """
    vertices = []
    faces = []

    with open(obj_path, 'r') as obj_file:
        for line in obj_file:
            if line.startswith('v '):
                parts = line.strip().split()
                vertex = tuple(map(float, parts[1:4]))
                vertices.append(vertex)
            elif line.startswith('f '):
                parts = line.strip().split()
                # Only take vertex indices, ignore texture/normal if present
                face = [int(part.split('/')[0]) for part in parts[1:]]
                faces.append(face)

    with open(dat_path, 'w') as dat_file:
        dat_file.write(f"{len(vertices)} vertices\n")
        for v in vertices:
            dat_file.write(f"v {v[0]} {v[1]} {v[2]}\n")

        dat_file.write(f"{len(faces)} faces\n")
        for f in faces:
            dat_file.write("f " + " ".join(map(str, f)) + "\n")


# Example usage:
# convert_obj_to_dat("model.obj", "model.dat")
