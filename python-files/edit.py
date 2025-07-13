from PIL import Image
import os
import shutil

def get_tongue_color():
    color_code = EB7861
    if len(color_code) == 6 and all(c in '0123456789abcdefABCDEF' for c in color_code):
        red = int(color_code[0:2], 16)
        green = int(color_code[2:4], 16)
        blue = int(color_code[4:6], 16)
        return (red, green, blue)
    else:
        print("Invalid color code. Please enter a valid 6-digit hex color code.")
        return get_tongue_color()  # Recursively call if invalid

#############################################################
# Helpers for extracting specific rows and re-merging them
#############################################################
def extract_rows(dog_img, row_list, box_size=32):
    """
    Creates a new image that only retains the specified rows in row_list,
    making all other rows transparent.
    """
    w, h = dog_img.size
    new_img = Image.new("RGBA", (w, h), (0,0,0,0))

    for row_idx in row_list:
        row_top = row_idx * box_size
        row_bottom = row_top + box_size

        row_crop = dog_img.crop((0, row_top, w, row_bottom))
        new_img.paste(row_crop, (0, row_top), row_crop)

    return new_img

def clear_rows(dog_img, row_list, box_size=32):
    """
    Overwrites the rows in row_list with full transparency.
    """
    w, h = dog_img.size
    for row_idx in row_list:
        row_top = row_idx * box_size
        row_box = Image.new("RGBA", (w, box_size), (0,0,0,0))
        dog_img.paste(row_box, (0, row_top))

def merge_rows_back(original_img, row_img, row_list, box_size=32):
    """
    Pastes only the specified row_list from row_img back into original_img.
    """
    w, h = original_img.size
    for row_idx in row_list:
        row_top = row_idx * box_size
        row_bottom = row_top + box_size

        row_crop = row_img.crop((0, row_top, w, row_bottom))
        original_img.paste(row_crop, (0, row_top), row_crop)

#############################################################
# Main script
#############################################################
def main():
    # 1) Get the color to replace from user
    color_to_replace = get_tongue_color()
    print(f"The color to replace is: {color_to_replace}")

    assets_folder = "assets"
    box_size = 32

    # Rows 12–14 in 1-based => [11,12,13] in 0-based
    target_rows = [7,11,12,13]

    # Original pairs from your code
    source_target_pairs = [
        ((6, 2), (7, 2)),
        ((4, 2), (9, 0)),
        ((4, 3), (9, 1)),
        ((4, 2), (9, 2)),
        ((6, 1), (10, 0)),
        ((6, 0), (10, 1)),
    ]

    # row12..14 shifting
    row_12_targets = [(11, 0, 4), (11, 1, 3), (11, 2, 4), (11, 3, 3)]
    row_13_targets = [(12, 0, 4), (12, 1, 3), (12, 2, 4), (12, 3, 3)]
    row_14_targets = [(13, 0, 2), (13, 1, 1)]

    color_replacement_positions = [(7, 2), (9, 2)]

    # We'll define a function to run your copy/paste logic on an image that only has rows 12–14
    def do_copy_paste_logic(img, full_img):
        """
        Runs the same logic you used, but only modifies 'img' (which presumably has rows 12..14).
        'full_img' is the original reference if we need row1, row2, row3 as sources.
        """
        w,h = img.size

        # 1) regular source->target
        for (src_pos, tgt_pos) in source_target_pairs:
            sx_left = src_pos[1]*box_size
            sx_top  = src_pos[0]*box_size
            sprite = full_img.crop((sx_left, sx_top, sx_left+box_size, sx_top+box_size))

            # target
            ty_row, ty_col = tgt_pos
            # if the target row is in [11..13], we paste into 'img'
            if ty_row in target_rows:
                # local coords
                left_t = ty_col*box_size
                top_t  = ty_row*box_size
                # We just paste directly; if you had shift logic for these pairs, do it:
                img.paste(sprite, (left_t, top_t))

                # color replacement
                if (ty_row, ty_col) in color_replacement_positions:
                    tile_crop = img.crop((left_t, top_t, left_t+box_size, top_t+box_size))
                    pix = tile_crop.load()
                    for yy in range(box_size):
                        for xx in range(box_size):
                            pc = pix[xx,yy]
                            if pc[:3]==color_to_replace:
                                if xx>0:
                                    left_c = pix[xx-1,yy]
                                    pix[xx,yy]= left_c
                    img.paste(tile_crop, (left_t, top_t))

        # 2) row12,13,14 shifting
        # We'll replicate your shifting logic:
        for (r,c, shift_up) in row_12_targets:
            if r in target_rows:
                if r==11: # row12
                    sx_left=0
                    sx_top = 0
                    sprite= full_img.crop((sx_left, sx_top, sx_left+box_size, sx_top+box_size))
                    left_t = c*box_size
                    top_t  = r*box_size - shift_up
                    # clamp if negative
                    if top_t<0: top_t=0
                    img.paste(sprite,(left_t, top_t))
        for (r,c, shift_up) in row_13_targets:
            if r in target_rows:
                if r==12: # row13
                    sx_left=0
                    sx_top = box_size
                    # if c>0 => up2 => your code, but let's keep it same
                    sprite= full_img.crop((sx_left, sx_top, sx_left+box_size, sx_top+box_size))
                    left_t= c*box_size
                    top_t = r*box_size - shift_up
                    if top_t<0: top_t=0
                    img.paste(sprite,(left_t, top_t))
        for (r,c, shift_up) in row_14_targets:
            if r in target_rows:
                if r==13: # row14
                    if c==0:
                        sx_left=0
                        sx_top= 2*box_size
                    else:
                        sx_left=2*box_size
                        sx_top= 2*box_size
                    sprite= full_img.crop((sx_left,sx_top, sx_left+box_size, sx_top+box_size))
                    left_t= c*box_size
                    top_t= r*box_size - shift_up
                    if top_t<0: top_t=0
                    img.paste(sprite,(left_t, top_t))

        # 3) final step: partial alpha removal
        for row_ in target_rows:
            for col_ in range(4):  # up to 4 columns
                L= col_*box_size
                U= row_*box_size
                region= img.crop((L,U,L+box_size,U+box_size)).convert("RGBA")
                px= region.load()
                for yy in range(box_size):
                    for xx in range(box_size):
                        pc= px[xx,yy]
                        if pc[3]<229:
                            px[xx,yy]=(0,0,0,0)
                img.paste(region, (L,U))

        return img

    #  main loop
    for filename in os.listdir(assets_folder):
        if not filename.lower().endswith('.png'):
            continue

        file_path = os.path.join(assets_folder, filename)
        with Image.open(file_path) as dog_img:
            dog_img = dog_img.convert("RGBA")
            w,h = dog_img.size
            print(f"\nProcessing => {filename}, size=({w},{h})")

            # 1) Create subfolder
            file_stem= os.path.splitext(filename)[0]
            folder_path= os.path.join(assets_folder,file_stem)
            os.makedirs(folder_path, exist_ok=True)

            # 2) Extract just rows 12..14 => combined into one "row12-14" image
            #    or you can do them separately. We'll do them combined in one image:
            row_img_12_14 = extract_rows(dog_img, target_rows, box_size=box_size)
            combined_filename= f"{file_stem}_row12_14.png"
            combined_path= os.path.join(folder_path, combined_filename)
            row_img_12_14.save(combined_path)
            print(f"  Created => {combined_filename} with only rows 12..14")

            # 3) We keep those rows also in the original file, so do NOT clear them here
            #    but if we want to avoid overlap, let's do it the same approach:
            dog_img_cleared = dog_img.copy()
            # we don't want to remove them from the final, so skip clearing them
            # unless you do want to remove overlap => we do it anyway:
            #clear_rows(dog_img_cleared, target_rows, box_size)

            # 4) do the copy/paste logic on row_img_12_14
            row_img_12_14_updated= row_img_12_14.copy()
            row_img_12_14_updated= do_copy_paste_logic(row_img_12_14_updated,dog_img)
            updated_name= f"{file_stem}_row12_14_updated.png"
            updated_path= os.path.join(folder_path, updated_name)
            row_img_12_14_updated.save(updated_path)
            print(f"  Updated => {updated_name}")

            # 5) re-merge this updated row image into the original dog_img
            #    If you want to see the new shifts in the final file
            #    We only paste rows12..14
            final_merged= dog_img.copy()
            merge_rows_back(final_merged, row_img_12_14_updated, target_rows, box_size=box_size)

            # 6) Overwrite
            final_merged.save(file_path)
            print(f"Overwritten => {file_path}")

            # 7) delete folder
            shutil.rmtree(folder_path, ignore_errors=True)
            print(f"Deleted => {folder_path}")

    print("\nAll copy/paste done. Rows 12–14 were extracted, updated, re-merged, folder removed.")


if __name__=="__main__":
    main()

