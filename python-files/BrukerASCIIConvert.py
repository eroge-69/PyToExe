#!/usr/bin/env python2.7
# ========================================================================
#               Bruker DTA + DSC to ASCII File Conversion
#
#   Filename:       BrukerASCIIConvert.py
#   Author:         Kipp J van Schooten (kippvs@gmail.com)
#   Version:        0.1 beta
#   Date:           2014-07-19 - 2014-07-30
#
#   Description:    o user pastes file directory to recurse through
#			 		o matches to .DTA and .DSC are found
#			 		o list of matches is itereated through
#			 		    - binary (BE decimal) data is loaded from DTA file as double
#					    - sweep params are loaded from DSC file
#			 		    - composite dataset created
#					    - export to .txt file performed
#
#	Notes:			o data files must have BOTH a .DTA and .DSC file in same directory
#					o will overwrite existing .txt files of same name
#					o all output data columns populated with floats
#					o execution time limited by HDD access speeds (i.e: fileIO)
#					o corrupt DTA files usually result in ValueError (mismatched axis arrays)
# ========================================================================
from __future__ import division
import os
import fnmatch
import numpy as np
import decimal

import time
start_time = time.time()
# ========================================================================
#                     USER PARAMETER INPUT
# ========================================================================

# rootdir = r"C:\Users\Kipp\My Documents\Research\Projects\012 - Inverse Spin Hall Effect"
rootdir = r"C:\Users\Kipp\My Documents\Research\Projects\000 - Python Analysis Scripts\DATfiles"

# ========================================================================
#                     FUNCTIONS USED BY MAIN SEQUENCE
# ========================================================================

def DTA_filepathnames(rootdir):
	DTA_matches = []
	for root, dirnames, filenames in os.walk(rootdir):
	  for filename in fnmatch.filter(filenames, '*.DTA'):
	      DTA_matches.append(os.path.join(root, filename))
	return DTA_matches


def DSC_filepathnames(rootdir):
	DSC_matches = []
	for root, dirnames, filenames in os.walk(rootdir):
	  for filename in fnmatch.filter(filenames, '*.DSC'):
	      DSC_matches.append(os.path.join(root, filename))
	return DSC_matches

# FUNCTION IS NOT USED - KEPT FOR FUTURE
# def split_paths_and_names(filepathnames):
# 	""" 
# 	takes in list of N filepaths containing dataset names. returns list of lists having
# 	two x N elements; filepath and dataset name. dataset name has extension removed.
# 	"""

# 	splitsville = []
# 	for i in range(len(filepathnames)-1):
# 		splitsville.append(filepathnames[i].rsplit("\\",1))
# 		splitsville[i][1] = splitsville[i][1][:-4]
# 	return splitsville
    
    
def find_DSC_param_val(DSC_data, param_name, dtype="int"):
    """
    Finds value corresponding to line of param_name in DSC_data (DSC file).
    
    Parameters:
        DSC_data: numpy.ndarray of DSC file [list of str]
        param_name: parameter name to search for in DSC file [str]
        dype: data type to output [int, float, str]
        
    Returns:
        param_val: value of found parameter [int, float, str]
    """
    
    param_val = []
    
    # raise error if wrong dtype entered
    if dtype not in ("int", "float", "str"):
        raise TypeError, "Incorrect dtype <{}>. Expected int, float, or str.".format(dtype)
    
    # search DSC_data for param_name
    # raise errors if not found or duplicates
    param_val = [s for s in DSC_data if param_name in s]
    
    if len(param_val) == 0:
        raise ValueError, "Parameter name {} not found in DSC file".format(param_name)
    if len(param_val) > 1:
        raise ValueError, "Multiple parameter names {} found in DSC file".format(param_name)
    
    param_val = str(param_val[0])
    param_val = param_val.replace(param_name,"",1)
    param_val = param_val.replace(" ","")
    param_val = param_val.replace("\t","")
    
    # if numeric, check for alpha characters, convert to int/float
    # else already a string. raise error if no alpha characters
    if dtype in ("int", "float"):
        if param_val.translate(None,".+-eE").isdigit() == False:    # isdigit() doesn't see eg "."
            raise TypeError, "Cannot convert alphanumeric {} to {}".format(param_val,dtype)
        else:
            if dtype == "float":
                param_val = float(param_val)
            else:
                param_val = int(decimal.Decimal(param_val))
    
    else:
        if param_val.isdigit() == True:
            raise TypeError, "Will not convert numeric {} to {}".format(param_val,dtype)        
    
    return param_val


def load_DSC_vals(DSC_filepathname):
	"""
	Loads DSC file into Numpy array. Parses out relevant parameter values to dict.

	Parameters:
        DSC_filepathname: file path and name of DSC file [str]
        
    Returns:
        DSC_param_dict: dictionary of relevant DSC parameter values [dict]
	"""
	DSC_data = np.loadtxt(DSC_filepathname, dtype="str", delimiter="\n")
	DSC_data = DSC_data[:100]	# truncate file. safe, low memory, high speed

	DSC_param_dict = {}

	# parameter values for complex data, else just real data (default for DSC)
	DSC_param_dict["IKKF"] = find_DSC_param_val(DSC_data, "IKKF", dtype="str")
	DSC_param_dict["IRNAM"] = find_DSC_param_val(DSC_data, "IRNAM", dtype="str")
	DSC_param_dict["IRUNI"] = find_DSC_param_val(DSC_data, "IRUNI", dtype="str")

	if DSC_param_dict["IKKF"] == "CPLX":
		DSC_param_dict["IINAM"] = find_DSC_param_val(DSC_data, "IINAM", dtype="str")
		DSC_param_dict["IIUNI"] = find_DSC_param_val(DSC_data, "IIUNI", dtype="str")

	elif DSC_param_dict["IKKF"] != "REAL":	# just in case data flag is something weird
		TypeError, "Incorrect data format <{}>. Expected IKKF=REAL,CPLX.".format(DSC_param_dict["IKKF"])

	# parameter values for XYZ, XY, or just X (defualt for DSC)
	DSC_param_dict["XTYP"] = find_DSC_param_val(DSC_data, "XTYP", dtype="str")
	DSC_param_dict["YTYP"] = find_DSC_param_val(DSC_data, "YTYP", dtype="str")
	DSC_param_dict["ZTYP"] = find_DSC_param_val(DSC_data, "ZTYP", dtype="str")

	DSC_param_dict["XPTS"] = find_DSC_param_val(DSC_data, "XPTS", dtype="int")
	DSC_param_dict["XMIN"] = find_DSC_param_val(DSC_data, "XMIN", dtype="float")
	DSC_param_dict["XWID"] = find_DSC_param_val(DSC_data, "XWID", dtype="float")
	DSC_param_dict["XNAM"] = find_DSC_param_val(DSC_data, "XNAM", dtype="str")
	DSC_param_dict["XUNI"] = find_DSC_param_val(DSC_data, "XUNI", dtype="str")
	
	if DSC_param_dict["ZTYP"] != "NODATA":
		DSC_param_dict["YPTS"] = find_DSC_param_val(DSC_data, "YPTS", dtype="int")
		DSC_param_dict["YMIN"] = find_DSC_param_val(DSC_data, "YMIN", dtype="float")
		DSC_param_dict["YWID"] = find_DSC_param_val(DSC_data, "YWID", dtype="float")
		DSC_param_dict["YNAM"] = find_DSC_param_val(DSC_data, "YNAM", dtype="str")
		DSC_param_dict["YUNI"] = find_DSC_param_val(DSC_data, "YUNI", dtype="str")

		DSC_param_dict["ZPTS"] = find_DSC_param_val(DSC_data, "ZPTS", dtype="int")
		DSC_param_dict["ZMIN"] = find_DSC_param_val(DSC_data, "ZMIN", dtype="float")
		DSC_param_dict["ZWID"] = find_DSC_param_val(DSC_data, "ZWID", dtype="float")
		DSC_param_dict["ZNAM"] = find_DSC_param_val(DSC_data, "ZNAM", dtype="str")
		DSC_param_dict["ZUNI"] = find_DSC_param_val(DSC_data, "ZUNI", dtype="str")

	elif DSC_param_dict["YTYP"] != "NODATA":
		DSC_param_dict["YPTS"] = find_DSC_param_val(DSC_data, "YPTS", dtype="int")
		DSC_param_dict["YMIN"] = find_DSC_param_val(DSC_data, "YMIN", dtype="float")
		DSC_param_dict["YWID"] = find_DSC_param_val(DSC_data, "YWID", dtype="float")
		DSC_param_dict["YNAM"] = find_DSC_param_val(DSC_data, "YNAM", dtype="str")
		DSC_param_dict["YUNI"] = find_DSC_param_val(DSC_data, "YUNI", dtype="str")

	elif DSC_param_dict["XTYP"] != "NODATA":	# breaks if axis type is IDG or NTUP
		TypeError, "Incorrect data format <{}>. Expected XTYP=IDX.".format(DSC_param_dict["XTYP"])

	# read microwave frequency for g-factor calculation
	DSC_param_dict["MWFQ"] = find_DSC_param_val(DSC_data, "MWFQ", dtype="int")

	return DSC_param_dict


def load_DTA_data(DTA_filepathname, ReIm="CPLX"):
	""" 
	Get binary data from file object with given endianess

	Parameters:
	    DTA_filepathname: file path and name of DTA file [str]
	    ReIm: is DTA file REAL or CPLX (1D or 2D)? [str]
	    
	Returns:
	    DTA_data: type based on dtype
	"""

	with open(DTA_filepathname, 'rb') as f:
	    DTA_data = np.frombuffer(f.read(), dtype='>d')
	    
	if ReIm == "CPLX":
		DTA_shape = len(DTA_data)/2
		DTA_data = np.ndarray(shape=(DTA_shape,2), dtype='>d', buffer=DTA_data)

	elif ReIm == "REAL":
		DTA_shape = len(DTA_data)
		DTA_data = np.ndarray(shape=(DTA_shape,1), dtype='>d', buffer=DTA_data)

	else:
	    raise TypeError, "Incorrect format <{}>. Expected REAL or CPLX.".format(ReIm)

	return DTA_data


def mk_data_table(DSC_DSC_param_dict, DTA_data):
	"""
	Takes in DSC parameters and DTA data.
	Builds numpy.ndarray for range of each dependent axis found in DSC file.
	Splits numpy.ndarray of DSC data into real and imag for complex datasets.
    Calculates X,Y,Z axes and tiles/repeats approapriately.
	Forms full data table as numpy.ndarray.

	Parameters:
	    DSC_DSC_param_dict: DSC parameter values [dict]
	    DTA_data: DTA dataset [numpy.ndarray]
	    
	Returns:
	    data_table = full dataset with axes [numpy.ndarray]
	"""

	# ============================================================
	# first make arrays for X,Y,Z axes datapoints
	Y_axis = None
	Z_axis = None
	dimension = 1

	# will have range of x vals by default
	X_start = DSC_DSC_param_dict["XMIN"]
	X_stop = DSC_DSC_param_dict["XWID"] + X_start
	X_pts = DSC_DSC_param_dict["XPTS"]
	X_axis = np.linspace(X_start, X_stop, X_pts).reshape((-1,1))

	if "YPTS" in DSC_DSC_param_dict:
		Y_start = DSC_DSC_param_dict["YMIN"]
		Y_stop = DSC_DSC_param_dict["YWID"] + Y_start
		Y_pts = DSC_DSC_param_dict["YPTS"]
		Y_axis = np.linspace(Y_start, Y_stop, Y_pts).reshape((-1,1))
		dimension = 2

		if "ZPTS" in DSC_DSC_param_dict:
			Z_start = DSC_DSC_param_dict["ZMIN"]
			Z_stop = DSC_DSC_param_dict["ZWID"] + Z_start
			Z_pts = DSC_DSC_param_dict["ZPTS"]
			Z_axis = np.linspace(Z_start, Z_stop, Z_pts).reshape((-1,1))
			dimension = 3

	# ============================================================
	# split off real and imag from DTA_data
	DTA_cplx = False
	DTA_imag = None

	if DSC_DSC_param_dict["IKKF"] == "CPLX":	# instead of looking it up each time
		DTA_cplx = True

	if DTA_cplx == True:
		DTA_real, DTA_imag = np.hsplit(DTA_data,2)

		if len(DTA_real) != len(DTA_imag):
			raise IndexError, "Real and Imag array length mismatch."
	else:
		DTA_real = DTA_data

	# ============================================================
	# create range arrays and append columns together data table
	index_array = np.arange(1, len(DTA_real)+1, 1).reshape((-1,1))

	# if DTA file is corrupted, then ValueError will be generated here
	# comes from shape mismatch between index_array and X/Y/Z axis/array
	if dimension == 3:
		X_ntiles = len(Y_axis)*len(Z_axis)
		X_array = np.tile(X_axis,(X_ntiles,1))

		Y_nrepeats = len(X_axis)
		Y_ntiles = len(Z_axis)
		Y_array = np.repeat(Y_axis,Y_nrepeats).reshape((-1,1))
		Y_array = Y_array.tile(Y_array,(Y_ntiles,1))

		Z_nrepeats = len(X_axis)*len(Y_axis)
		Z_array = np.repeat(Z_axis,Z_nrepeats).reshape((-1,1))

		data_table = np.append(index_array,X_array,axis=1)
		data_table = np.append(data_table,Y_array,axis=1)
		data_table = np.append(data_table,Z_array,axis=1)

	elif dimension == 2:
		X_ntiles = len(Y_axis)
		X_array = np.tile(X_axis,(X_ntiles,1))

		Y_nrepeats = len(X_axis)
		Y_array = np.repeat(Y_axis,Y_nrepeats).reshape((-1,1))

		data_table = np.append(index_array,X_array,axis=1)
		data_table = np.append(data_table,Y_array,axis=1)

	else:
		data_table = np.append(index_array,X_axis,axis=1)

	data_table = np.append(data_table,DTA_real,axis=1)

	if DTA_cplx == True:
		data_table = np.append(data_table,DTA_imag,axis=1)

	return data_table


def mk_data_file(savedir_ASCII, DSC_DSC_param_dict):

	header_str = ""
	header_lst = ["index"]

	X_col = "{} [{}]".format(DSC_DSC_param_dict["XNAM"], DSC_DSC_param_dict["XUNI"])
	header_lst.append(X_col)
	
	real_col = "{} [{}]".format(DSC_param_dict["IRNAM"], DSC_param_dict["IRUNI"])

	if DSC_param_dict["IKKF"] == "CPLX":
		imag_col = "{} [{}]".format(DSC_param_dict["IINAM"], DSC_param_dict["IIUNI"])

		if DSC_param_dict["ZTYP"] != "NODATA":
			Y_col = "{} [{}]".format(DSC_param_dict["YNAM"], DSC_param_dict["YUNI"])
			Z_col = "{} [{}]".format(DSC_param_dict["ZNAM"], DSC_param_dict["ZUNI"])
			header_lst.append(Y_col)
			header_lst.append(Z_col)
			header_lst.append(real_col)
			header_lst.append(imag_col)

		elif DSC_param_dict["YTYP"] != "NODATA":
			Y_col = "{} [{}]".format(DSC_param_dict["YNAM"], DSC_param_dict["YUNI"])
			header_lst.append(Y_col)
			header_lst.append(real_col)
			header_lst.append(imag_col)

		else:
			header_lst.append(real_col)
			header_lst.append(imag_col)

	else:
		if DSC_param_dict["ZTYP"] != "NODATA":
			Y_col = "{} [{}]".format(DSC_param_dict["YNAM"], DSC_param_dict["YUNI"])
			Z_col = "{} [{}]".format(DSC_param_dict["ZNAM"], DSC_param_dict["ZUNI"])
			header_lst.append(Y_col)
			header_lst.append(Z_col)
			header_lst.append(real_col)

		elif DSC_param_dict["YTYP"] != "NODATA":
			Y_col = "{} [{}]".format(DSC_param_dict["YNAM"], DSC_param_dict["YUNI"])
			header_lst.append(Y_col)
			header_lst.append(real_col)

		else:
			header_lst.append(real_col)

	for i in range(len(header_lst)-1):
		header_str += header_lst[i] + "\t"

	header_str += header_lst[len(header_lst)-1]
	header_str = header_str.replace("'","")

	np.savetxt(savedir_ASCII, data_table, header=header_str, delimiter="\t")

	return

def print2term(msg_type, msg_str=None):
    """ 
    Prints a header with msg_type and current timestamp to the terminal.
    Optionally takes in a msg_str for output.
    """

    line1 = "=" * 60
    line2 = "\n " + msg_type

    if msg_str is None:
        line3 = "\n " + ""
    else:
        line3 = "\n " + unicode(msg_str, encoding='UTF-8') + "\n"

    logmessage = line1 + line2 + line3 + "\n"

    print logmessage.encode('utf-8')

    return
# ========================================================================
#                     		MAIN PROGRAM SEQUENCE
# ========================================================================

# find all DTA and DSC files in directory structure within rootdir
DTA_matches = DTA_filepathnames(rootdir)
DSC_matches = DSC_filepathnames(rootdir)
if len(DTA_matches) > len(DSC_matches):
    raise IndexError, "Found more DTA files than DSC files"

# DTA_paths_and_names = file_paths_and_names(DTA_matches)

for i in range(len(DTA_matches)):

	# initialize variables to empty

	# in case more DSC than DTA files, assume DTA has corresponding DSC
	DTA_filepathname = DTA_matches[i]
	DSC_filepathname = DTA_matches[i][:-4] + ".DSC"

	# set save directory to be same as original data
	savedir_ASCII = DTA_matches[i][:-4] + ".txt"

	# load DSC file and make a dict of relvant DSC parameters (Re/Im, 1D/2D/3D)
	DSC_param_dict = load_DSC_vals(DSC_filepathname)

	# load DTA data into an numpy.ndarray of correct shape (Re only, or Re and Im)
	ReIm = DSC_param_dict["IKKF"]
	DTA_data = load_DTA_data(DTA_filepathname, ReIm)

	# generate tabulated data table as numpy.ndarray
	data_table = mk_data_table(DSC_param_dict, DTA_data)

	# generate column headers and save ASCII at savedir_ASCII
	mk_data_file(savedir_ASCII, DSC_param_dict)

	# some feedback to the user
	msg_type = "ASCII Conversion: Success"
	print2term(msg_type, msg_str=savedir_ASCII) 

elapsed_time = "execution time = " + str(time.time()-start_time), "seconds"
print2term(elapsed_time)
# ========================================================================
# ========================================================================