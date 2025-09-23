import os

print("Log:")

def conv_dsp_log_to_asam(src_file_in, dest_file_in):             
    print(src_file_in + ' -> ' + dest_file_in)

    file = open ('./trace/' + src_file_in, 'r')              # open source file and read data
    file_content = file.readlines()
    file.close()

    file = open ('./export/' + dest_file_in, 'w')            # open destination file in write mode

    line_content = file_content[11]                          # read variable names 
    line_content = line_content.replace('\t', ',', -1)       # replace tab stops with comma

    file.writelines('time[s],' + line_content)               # add a column for time stamp and write the content in file 

    time_stamp_calc_s_x10 = 0.0                              # variable for time stamp calculation in 0.1s
    loop_cnt = 0                                             # counter for loop 
    
    while loop_cnt < 50:                                     # read the 50 data setsform the log
        line_content = file_content[12 + loop_cnt]           # read from line 12 the data
        line_content = line_content.replace('\t', ',', -1)   # replace tab stops with comma
        file.writelines(str(round(-3.9 + time_stamp_calc_s_x10, 1)) + ',' + line_content)  # add a column with time stamp and write the content in file 
        time_stamp_calc_s_x10 = time_stamp_calc_s_x10 + 0.1  # increment time stamp
        loop_cnt = loop_cnt + 1                              # increment loop count

    file.close()                                             # close destination file


if not os.path.exists('export'):                             # create an export folder
    os.mkdir('export')

file_list = os.listdir('./trace')                            # create list with file names in trace folder

for file_name in file_list:
    if (file_name.endswith('.fast_log')):
        src_file = file_name
        dest_file = src_file.replace('.fast_log', '_fast_log_ASAM.csv', 1)  # change naming of destination file
        conv_dsp_log_to_asam(src_file, dest_file)            # call convertion function

