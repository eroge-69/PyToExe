import sys
import codecs
import os
from pathlib import Path
from atlassian import Confluence
import requests
import shutil
import re
import urllib

def ini_Config(CONFLUENCE_BASE_URL, USER, PASSWORD, ACCESS_TOKEN):
    if (ACCESS_TOKEN == ''):
        confluence = Confluence(url = CONFLUENCE_BASE_URL, username = USER, password = PASSWORD)
        return confluence
    else:
        confluence = Confluence(url = CONFLUENCE_BASE_URL, token = ACCESS_TOKEN)
        return confluence

def sanitize_For_Filename(original_string):
    sanitized_file_name = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()
    return sanitized_file_name

# WORK WITH SPACE
spaces = None
spacelist = None

def get_All_In4 (confluence):
    global spaces
    global spacelist
    try:
        spaces = confluence.get_all_spaces(start=0, limit=500, expand=None)
        spacelist = spaces['results']
        print("Spaces:")
        for space in spacelist:
            print("   Key: " + space['key'] + ' | ' + "Name: " + space['name'])
            _all_pages = []
            start = 0
            limit = 100
            while True:
                values = confluence.get_all_pages_from_space(space=space['key'], start = start, limit = limit, expand=None, content_type='page')
                _all_pages = _all_pages + values
                if len(values) == 0:
                    print("Page not found, check permissions")
                    break
                if len(values) < limit:
                    break
                start += limit
            for value in _all_pages:                                                           
                print("\t Page ID: " + value['id'] + " | Title: " + value['title'])
    except:
        print("Error. Can not found any Space or Page")

# WORK WITH SPACE

def get_All_Spaces (confluence):
    global spaces
    global spacelist
    spaces = confluence.get_all_spaces(start=0, limit=500, expand=None)
    spacelist = spaces['results']

def print_All_Spaces (confluence):
    global spaces
    global spacelist
    spaces = confluence.get_all_spaces(start=0, limit=500, expand=None)
    spacelist = spaces['results']
    print("Spaces:")
    for space in spacelist:
        print("   Key: " + space['key'] + ' | ' + "Name: " + space['name'])
    #Count the Spaces from results.
    print('Total Spaces:', len(spacelist))

def get_Spaces_In4 (confluence, spaceKey):
    try:
        _all_pages = []
        start = 0
        limit = 100
        while True:
            values = confluence.get_all_pages_from_space(space=spaceKey, start = start, limit = limit, expand=None, content_type='page')
            _all_pages = _all_pages + values
            if len(values) == 0:
                print("Page not found, check permissions")
                break
            if len(values) < limit:
                break
            start += limit
        for value in _all_pages:                                                           
            print("\t Page ID: " + value['id'] + " | Title: " + value['title'])
    except:
        print("Error. Can not found Space")

def get_Space_With_Key (spaceKey):
    for space in spacelist:
        skey = space['key']
        if spaceKey == skey:
            return space['name']

def get_Space_With_Name (spaceName):
    for space in spacelist:
        sName = space['name']
        if spaceName == sName:
            return space['key']

# WORK WITH PAGE
def export_Pages_To_PDF (confluence, spaceKey):
    _all_pages = []
    start = 0
    limit = 100
    while True:
        values = confluence.get_all_pages_from_space(space=spaceKey, start = start, limit = limit, expand=None, content_type='page')
        _all_pages = _all_pages + values
        if len(values) == 0:
            print("Page not found, check permissions")
            break
        if len(values) < limit:
            break
        start += limit
    try:
        # Create directory for the current space with the space name and download the files in to that dir.
        dirName = sanitize_For_Filename(str(get_Space_With_Key(spaceKey)))
        try:
            os.makedirs(dirName)    
            print("=== Created directory for space:" , dirName)
            os.chdir(dirName)
        except FileExistsError:
            print("=== Directory '" , dirName ,  "' already exists")
            os.chdir(dirName)
        # Download files from list
        for value in _all_pages:                                                           
            #print("\t Page ID: " + value['id'] + " | Title: " + value['title'])
            page = confluence.get_page_by_id(page_id=value['id'])
            pageId = value['id']  
            # A function to create pdf from byte-stream responce
            def save_file(content):
                file_pdf = open(sanitize_For_Filename(value['title']) + '.pdf', 'wb')
                file_pdf.write(content)
                file_pdf.close()
                print("\t Downloaded: " + value['title'])
            # Get your confluence page as byte-stream
            response = confluence.get_page_as_pdf(page_id=value['id'])
            save_file(content=response) 
                    
        # Exit from current folder and go back to home dir
        path_parent = os.path.dirname(os.getcwd())
        os.chdir(path_parent)
    except:
        print("Error")

def list_Attachment_Of_Page (confluence, spaceKey, pageID):
    _all_pages = []
    start = 0
    limit = 100
    # Page is not specific.
    if pageID == "":
        print("SPACE: " + get_Space_With_Key(spaceKey))
        while True:
            values = confluence.get_all_pages_from_space(space=spaceKey, start = start, limit = limit, expand=None, content_type='page')
            _all_pages = _all_pages + values
            if len(values) == 0:
                print("Page not found, check permissions")
                break
            if len(values) < limit:
                break
            start += limit
        for value in _all_pages:
            print("\t Attachment in page '" + value['title'] + "':")
            attachments_container = confluence.get_attachments_from_content(page_id=value['id'], start=0, limit=500)
            attachments = attachments_container['results']
            for attachment in attachments:
                fname = attachment['title']
                print("\t \t" + fname)
    else:
        while True:
            values = confluence.get_all_pages_from_space(space=spaceKey, start = start, limit = limit, expand=None, content_type='page')
            _all_pages = _all_pages + values
            if len(values) == 0:
                print("Page not found, check permissions")
                break
            if len(values) < limit:
                break
            start += limit
        for value in _all_pages:
            if pageID == value['id']:
                print("\t Attachment in page '" + value['title'] + "':")
                attachments_container = confluence.get_attachments_from_content(page_id=pageID, start=0, limit=500)
                attachments = attachments_container['results']
                for attachment in attachments:
                    fname = attachment['title']
                    print("\t \t" + fname)
            else:
                continue

def export_Attachment_Of_Page (confluence, spaceKey, pageID):
    _all_pages = []
    start = 0
    limit = 100
    # Page is not specific.
    if pageID == "":
        print("Working SPACE: " + get_Space_With_Key(spaceKey))
        while True:
            values = confluence.get_all_pages_from_space(space=spaceKey, start = start, limit = limit, expand=None, content_type='page')
            _all_pages = _all_pages + values
            if len(values) == 0:
                print("Page not found, check permissions")
                break
            if len(values) < limit:
                break
            start += limit
        dirName = sanitize_For_Filename(str(get_Space_With_Key(spaceKey)))
        try:
            os.makedirs(dirName)
            print("=== Created directory for space:" , dirName)
            os.chdir(dirName)
        except FileExistsError:
            print("=== Directory '" , dirName ,  "' already exists")
            os.chdir(dirName)
        for value in _all_pages:
            dirName = sanitize_For_Filename(str(value['title']))
            try:
                os.makedirs(dirName)    
                os.chdir(dirName)
            except FileExistsError:
                os.chdir(dirName)
            print("\t Attachment in page '" + value['title'] + "':")
            attachments_container = confluence.get_attachments_from_content(page_id=value['id'], start=0, limit=500)
            attachments = attachments_container['results']
            for attachment in attachments:
                fname = attachment['title']
                print("\t \t" + fname)
                download_link = confluence.url + attachment['_links']['download']
                r = confluence.session.get(download_link)
                if r.status_code == 200:
                    with open(fname, "wb") as f:
                        for bits in r.iter_content():
                            f.write(bits)
            os.chdir('..')
        path_parent = os.path.dirname(os.getcwd())
        os.chdir(path_parent)
    else:
        while True:
            values = confluence.get_all_pages_from_space(space=spaceKey, start = start, limit = limit, expand=None, content_type='page')
            _all_pages = _all_pages + values
            if len(values) == 0:
                print("Page not found, check permissions")
                break
            if len(values) < limit:
                break
            start += limit
        dirName = sanitize_For_Filename(str(get_Space_With_Key(spaceKey)))
        #try:
        #    os.makedirs(dirName)
        #    print("=== Created directory for space:" , dirName)
        #    os.chdir(dirName)
        #except FileExistsError:
        #    print("=== Directory '" , dirName ,  "' already exists")
        #    os.chdir(dirName)
        for value in _all_pages:
            if pageID == value['id']:
                try:
                    os.makedirs(dirName)
                    print("=== Created directory for space:" , dirName)
                    os.chdir(dirName)
                except FileExistsError:
                    print("=== Directory '" , dirName ,  "' already exists")
                    os.chdir(dirName)

                dirName = sanitize_For_Filename(str(value['title']))
                try:
                    os.makedirs(dirName)    
                    os.chdir(dirName)
                except FileExistsError:
                    os.chdir(dirName)
                print("\t Attachment in page '" + value['title'] + "':")
                attachments_container = confluence.get_attachments_from_content(page_id=pageID, start=0, limit=500)
                attachments = attachments_container['results']
                for attachment in attachments:
                    fname = attachment['title']
                    print("\t \t" + fname)
                    download_link = confluence.url + attachment['_links']['download']
                    r = confluence.session.get(download_link)
                    if r.status_code == 200:
                        with open(fname, "wb") as f:
                            for bits in r.iter_content():
                                f.write(bits)
            else:
                continue

# ******************************************************************************************************** #

def main():
    # Check CommandLine
    if len(sys.argv) <= 7:
        print("Info: Export Atlassian Confluence's data")
        print("Usage: python ExportConfluence.py -U [Value] [-P|-A] [Value] -L [Confluence_URL] [OPTIONS] [Value]")
        print("     -U    \t UserName")
        print("     -P    \t Password")
        print("     -A    \t AccessToken")
        print("     -L    \t Confluence URL. Format 'https://confluence.dot.com'")
        print("     -Ls   \t List all Pages and Spaces infomation in Confluence")
        print("     -Sp   \t List all Spaces infomation in Confluence. Value accepted {All, SpaceKey}, default is 'All'")
        print("     -Pdf  \t Export Pages of all Space or an specific Spaces into PDF files. Value accepted {All, SpaceKey}")
        print("     -Lsa  \t List all Attachment. Value accepted {All, SpaceKey, PageID}")
        print("           \t       All: List Attachment on all Pages in all Space")
        print("           \t  SpaceKey: List Attachment on all Pages in specific Space")
        print("           \t    PageID: List Attachment in specific Page")
        print("     -Atm  \t Export Attachment. Value accepted {All, SpaceKey, PageID}")
        print("           \t       All: Export Attachment on all Pages in all Space")
        print("           \t  SpaceKey: Export Attachment on all Pages in specific Space")
        print("           \t    PageID: Export Attachment in specific Page")
        return sys.exit(1)
    exportFolder = "CON_DMP"
    user = sys.argv[2]
    loginType = sys.argv[3]
    auth = sys.argv[4]
    url = sys.argv[6]
    options = sys.argv[7]
    if (loginType == '-P'):
        confluence = ini_Config(url,user,auth,'')
    else:
        confluence = ini_Config(url,user,'',auth)
    try:
        if options == "-Ls":
            get_All_In4(confluence)
            return
        if options == "-Sp":
            if sys.argv[8] == "All":
                get_All_In4(confluence)
                return
            else:
                get_Spaces_In4(confluence, sys.argv[8])
                return
        if options == "-Pdf":
            try:
                os.makedirs(exportFolder)
                os.chdir(exportFolder)
            except FileExistsError:
                print("Directory '" + exportFolder +  "' already exists.")
                os.chdir(exportFolder)
            if sys.argv[8] == "All":
                print_All_Spaces(confluence)
                for space in spacelist:
                    try:
                        export_Pages_To_PDF(confluence, space['key'])
                    except:
                        print("Cant access space: " + space['name'])
                print("Export to PDF finished")
                return
            else:
                try:
                    get_All_Spaces(confluence)
                    export_Pages_To_PDF(confluence, sys.argv[8])
                except:
                    print("Cant access space: " + str(get_Space_With_Key(sys.argv[8])))
                print("Export to PDF finished")
                return
        if options == "-Atm":
            get_All_Spaces(confluence)
            try:
                os.makedirs(exportFolder)
                os.chdir(exportFolder)
            except FileExistsError:
                print("Directory '" + exportFolder +  "' already exists")
                os.chdir(exportFolder)
            if sys.argv[8] == "All":
                for space in spacelist:
                    try:
                        export_Attachment_Of_Page(confluence, space['key'], "")
                    except:
                        print("Cant access Space: " + space['name'])
                return
            elif get_Space_With_Key(sys.argv[8]) is not None:
                try:
                    export_Attachment_Of_Page(confluence, str(sys.argv[8]), "")
                except:
                    print("Cant access SpaceKey: " + str(sys.argv[8]))
                return
            else:
                for space in spacelist:
                    try:
                        export_Attachment_Of_Page(confluence, space['key'], sys.argv[8])
                    except:
                        print("Cant access PageID: " + sys.argv[8])
                return
        if options == "-Lsa":
            get_All_Spaces(confluence) 
            if sys.argv[8] == "All":
                for space in spacelist:
                    try:
                        list_Attachment_Of_Page(confluence, space['key'], "")
                    except:
                        print("Cant access Space: " + space['name'])
                return
            elif get_Space_With_Key(sys.argv[8]) is not None:
                try:
                    list_Attachment_Of_Page(confluence, str(sys.argv[8]), "")
                except:
                    print("Cant access SpaceKey: " + str(sys.argv[8]))
                return
            else:
                for space in spacelist:
                    try:
                        list_Attachment_Of_Page(confluence, space['key'], sys.argv[8])
                    except:
                        print("Cant access PageID: " + sys.argv[8])
                return
    except:
        print("Error")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        error_print('ERROR: Keyboard Interrupt.')
        sys.exit(1)