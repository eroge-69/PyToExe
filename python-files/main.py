import os
import glob
import mmap
from distutils.dir_util import copy_tree
import argparse
import time

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage="%(prog)s workig_dir output_dir link_to_find ",
        description="Check logs for specified link/s."
    )
    parser.add_argument('working_dir')
    parser.add_argument('output_dir')
    parser.add_argument('find_link')
    return parser


if __name__ == '__main__':
    parser = init_argparse()
    args = parser.parse_args()

    working_dir = os.path.abspath(args.working_dir)
    output_dir = os.path.abspath(args.output_dir)
    find_link = args.find_link

    entry_count = 0
    os.mkdir(output_dir)
    start_time = time.time()
    with open(os.path.join(output_dir + '\\log.txt'), 'w') as log_file:
        for entry in os.listdir():
            if os.path.isdir(entry) and (entry is not output_dir):
                os.chdir(entry)
                for file in glob.glob("*.txt", recursive=True):
                    with open(file, 'rb', 0) as txt_file:
                        if os.stat(file).st_size != 0:
                            with mmap.mmap(txt_file.fileno(), 0, access=mmap.ACCESS_READ) as s:
                                if s.find(find_link.encode()) != -1:
                                    if not os.path.exists(os.path.join(output_dir, entry)):
                                        copy_tree(os.path.join(working_dir, entry), os.path.join(output_dir, entry))
                                        log_file.write('[' + file + ']: ' + os.path.join(output_dir, entry) + '\n')
                                        entry_count += 1
                os.chdir(working_dir)
    print('Found ' + str(entry_count) + ' entries!')
    print('Elapsed: ' + str(time.time() - start_time) + ' seconds!')

