from os.path import exists, basename
from os import mkdir
from sys import exit
import csv
import cv2
import numpy as np
import matplotlib.pyplot as plt
import config as cfg
from glob import glob
from tqdm import tqdm

def main():
    # read template & target images
    img_tmp = cv2.imread(cfg.template_image_file, cv2.IMREAD_GRAYSCALE)
    target_files = glob(cfg.target_image_path)
    if len(target_files) < 1:
        print("[ERROR] Failed to find any target file in {}".format(cfg.target_image_path))
        exit(-1)
    else:
        print("[INFO] {} target file(s) were found".format(len(target_files)))

    # plotting directory
    plot_dir = "./ouput"
    if not exists(plot_dir):
        mkdir(plot_dir)

    # start matching            
    found_files = []
    print("[INFO] Start matching...")
    for tf in tqdm(target_files):
        img_tar = cv2.imread(tf, cv2.IMREAD_GRAYSCALE) # convert to gray scale
        res = cv2.matchTemplate(img_tar, img_tmp, cfg.method) # matching
        max_score = np.max(res)
        found = 1 if max_score > cfg.threshold else 0
        if found:
            found_files.append(tf)
            
            min_val, max_val, min_location, max_location = cv2.minMaxLoc(res)
            top_left = max_location
            height, width = img_tmp.shape[0], img_tmp.shape[1]
            
            plt.imshow(img_tar, cmap="grey")
            plt.gca().add_patch(
                plt.Rectangle(
                    (top_left[0], top_left[1]),
                    width, height,
                    edgecolor="red",
                    facecolor="none",
                    linewidth=2
                )
            )

            tar_file_name = basename(tf)
            tar_fig_name = plot_dir+"\\"+"matching_"+tar_file_name
            plt.tight_layout()
            plt.savefig(tar_fig_name)

    # save results
    if len(found_files) > 0:
        print("[INFO] Save the results in matching_output.csv ({} matched)".format(len(found_files)))
        with open("matching_output.csv", "w", newline="") as file:
            writer = csv.writer(file)
            for v in found_files:
                writer.writerow([v])
    else:
        print("[INFO] None of the target file were matched.")


if __name__ == "__main__":
    main()