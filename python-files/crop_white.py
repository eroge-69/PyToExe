#!/usr/bin/env python3

from gimpfu import *

def crop_to_white_area(image, drawable):
    pdb.gimp_image_undo_group_start(image)

    # Set image active
    pdb.gimp_image_set_active_layer(image, drawable)

    # Duplicate the layer (to preserve original)
    temp_layer = pdb.gimp_layer_copy(drawable, True)
    pdb.gimp_image_insert_layer(image, temp_layer, None, -1)

    # Use "Select by Color" to select the white area
    pdb.gimp_context_set_threshold(30)
    pdb.gimp_image_select_color(image, CHANNEL_OP_REPLACE, temp_layer, (255, 255, 255))

    # Shrink selection slightly to avoid anti-aliasing edge
    pdb.gimp_selection_shrink(image, 1)

    # Get the bounds of the selection
    x, y, width, height = pdb.gimp_selection_bounds(image)[1:]

    # Crop the image to the selection bounds
    pdb.gimp_image_crop(image, width, height, x, y)

    # Remove the temporary layer
    pdb.gimp_image_remove_layer(image, temp_layer)

    pdb.gimp_selection_none(image)
    pdb.gimp_image_undo_group_end(image)

    # Update the display
    pdb.gimp_displays_flush()

register(
    "python_fu_crop_to_white_area",
    "Zuschneiden auf weißen Bereich",
    "Entfernt den schwarzen Rand und schneidet das Bild auf den weißen Bereich zu.",
    "Dein Name",
    "Dein Name",
    "2025",
    "Zuschneiden auf weißen Bereich",
    "*",      # Alternativ: "RGB*, GRAY*"
    [
        (PF_IMAGE, "image", "Input Image", None),
        (PF_DRAWABLE, "drawable", "Input Drawable", None)
    ],
    [],
    crop_to_white_area,
    menu="<Image>/Filter/Anpassen/"
)

main()
