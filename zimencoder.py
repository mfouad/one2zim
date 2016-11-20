#!/usr/bin/python

############### Contributer Notice
# Modified by Mohammad Fouad based on jigho's notecase2zim.py.
# Original notice follows below...
############### Original Notice
# Simple script to convert NoteCase Document to a Zim notebook folder
#
# NoteCase reference: 
#    http://notecase.sourceforge.net/  (Free version, discontinued)
#    http://www.virtual-sky.com/   (Pro version)
#
# Based on BeautifulSoup (you need to install it before running notecase2zim): 
#    http://www.crummy.com/software/BeautifulSoup/
#
# Adapted to my use of NoteCase and Zim => other may want to adapt it
# For instance:
#   Color "red" in NoteCase => I use "italic" in Zim
#   Background Color "grey" in NoteCase => Title 3 in Zim
#
# Usage :
# -------
# 1. Save NoteCase document to .ncd format (plain text, no compression)
# 2. This script assumes the name is "notecase.ncd". This can be changed below
# 3. Run: python notecase2zim.py
# 4. Get a Folder named "notecase.zim" with the main file "notebook.zim" inside
#
# v1.1
# Jigho 2011
# Contact: https://launchpad.net/~jigho
#

import os
import sys
import re
import io
import uuid
#sys.path.append('./BeautifulSoup')

from bs4 import BeautifulSoup

class Page(object):
    pass

def encode_notebook(path, name):
    # You may change the name and endofline mode here
    fpath = os.path.join(path, name) + '.zim'
    fileZim = open(fpath, 'w')
    fileZim.write('[Notebook]\nname=' + name + '\nversion=0.4\nendofline=dos')
    fileZim.close()

def create_page(page_path, page_name, page_create_date):

    # Some verbose, usefull on large contents
    # to be aware that the program is still processing...
    title =  page_name
    print u'Creating file: ' , title.encode('utf-8')

    fileOut = io.open(page_path + ".txt", 'w', encoding='utf-8')

    # Standard information at the start of any Zim file
    fileOut.write(u'Content-Type: text/x-zim-wiki\n')
    fileOut.write(u'Wiki-Format: zim 0.4\n')
    fileOut.write(u'Creation-Date: ' + page_create_date + u'\n')

    fileOut.write(u'\n====== ' + title + u' ======\n')
    fileOut.write(u'\n')

    return fileOut

def format(page, el, left_tag, right_tag=None):
    # for basic formatting tags (underline, bold, italic,...)
    # do the core job

    if right_tag is None:
        right_tag = left_tag

    newLine = False

    # Open Wiki format
    page.pagefile.write(left_tag)

    # Another trick in case of formatted content ends with a newline
    # I then prefer to close the formatting tag and then write the
    # new line without formatting
    if (len(el.contents) > 1):
        if (el.contents[-2].__class__.__name__ == 'Tag'):
            if (el.contents[-2].name == 'br'):
                el.contents[-2].extract()
                el.contents[-1].extract()
                newLine = True

    # Process content (recursively !)
    format_children(page, el, u'')

    # Close Wiki format
    page.pagefile.write(right_tag)

    # End of the trick for content finishing with a newline
    if newLine:
        page.pagefile.write(u'\n')

def format_children(page, elements, left_tag, right_tag=None):
    # "currentFormat" is a trick to close the Wiki format at end of each line
    # even if the format is applied to multi-lines
    # Nota: this trick would need to be be enhanced
    #       when multiple formats are nested

    if right_tag is None:
        right_tag = left_tag

    for el in elements:
        if (el.__class__.__name__ == 'Tag'):

            attr = unicode(el.get('data-tag'))
            if attr.find("to-do:completed") >= 0:
                page.pagefile.write(u"[*] ")
            elif attr.find("to-do") >= 0:
                page.pagefile.write(u"[ ] ")

            # <br> tag stands for new line
            # use the "currentFormat" trick to properly close format tag
            # and then reopen it on the the new line
            if el.name == 'br':
                page.pagefile.write(right_tag)
                page.pagefile.write(u'\n')
                page.pagefile.write(left_tag)

            
            elif el.name == 'h1':
                format(page, el, u'====== ', u' ======\n')
            elif el.name == 'h2':
                format(page, el, u'===== ', u' =====\n')
            elif el.name == 'h3':
                format(page, el, u'==== ', u' ====\n')
            elif el.name == 'h4':
                format(page, el, u'=== ' , u' ===\n')
            elif el.name == 'h5':
                format(page, el, u'== ', u' ==\n')

            # <u> tag stands for underline
            elif el.name == 'u':
                format(page, el, u'__')

            # <b> tag stands for bold
            elif el.name == 'b':
                format(page, el, u'**')

            # <i> tag stands fr italic
            elif el.name == 'i':
                format(page, el, u'//')

            # <s> tag stands for strike-through
            elif el.name == 's':
                format(page, el, u'~~')

            # cite cinverted to verbatim
            elif el.name == 'cite':
                format(page, el, u"''")

            # <span> tag can have different purposes according to arguments
            elif el.name == 'span':
                attr = unicode(el.get('style'))
                if (attr == "color:#ff0000" or attr == "font-style:italic"):
                    format(page, el, u'//')
                elif attr == "font-weight:bold":
                    format(page, el, u'**')
                elif attr == "text-decoration:underline":
                    format(page, el, u'__')
                elif attr == "text-decoration:line-through":
                    format(page, el, u'~~')
                elif attr.find("background-color") >= 0:
                    format(page, el, u'**')
                # Other <span> contents are treated as plain text
                # You may add more cases according to your needs
                else:
                    print u"WARNING : unknown SPAN type", el.attrs
                    format(page, el, left_tag, right_tag)

            # <a> tag stands for links
            elif el.name == 'a':
                page.pagefile.write(u'[[')
                page.pagefile.write(el['href'])
                page.pagefile.write(u'| ')
                format(page, el, u"")
                page.pagefile.write(u' ]]')

            elif el.name == 'img':
                page.pagefile.write(u'{{')
                img_url = el.get('src')
                mime_type = el.get('data-src-type')
                img_file_name = unicode(uuid.uuid4()) + u'.png'
                page.images[img_file_name] = img_url
                page.pagefile.write(u'./' + img_file_name)
                    	# width="213" height="85" src="https://www.onenote.com/api/v1.0/me/notes/resources/GUIDs/$value" 
                        # data-src-type="image/png"
                        # data-fullres-src="https://www.onenote.com/api/v1.0/me/notes/resources/GUID/$value" 
                        # data-fullres-src-type="image/png" />
                page.pagefile.write(u'}}')

            elif el.name == 'td':
                format(page, el, u'| ', u'')

            elif el.name == 'tr': 
                format(page, el, u'', u' |\n')

            elif el.name in ['p', 'div', 'table']: 
                format(page, el, left_tag, right_tag + u'\n')

            elif el.name in ['ul', 'ol']: 
                format_children(page, el,  left_tag + u'\t', u'')

            elif el.name == 'li':
                # maintain indentation    
                page.pagefile.write(left_tag + u'* ')            
                format_children(page, el, left_tag,  right_tag)
                page.pagefile.write(right_tag + u'\n')

            # In case program encounter a Tag which is not dealt with
            # according to your needs, you can then add specific bloc
            else:    
                print u'WARNING, unknown tag: ', el.name
                format(page, el, left_tag, right_tag)

        else:
            text = el.string
            # Delete the new line symbol at start of the line
            # This happens when there was a <br> just before
            # but <br> is already taken into account
            text = text.strip("\r\n\t")
            text = re.sub("^\n\r", '', text)
            page.pagefile.write(unicode(text))

def encode_page(page_path, page_name, page_create_date, page_content=None):
    page = Page()
    page.images = {}
    page.pagefile = create_page(page_path, page_name, page_create_date)
    if page_content:
        soup = BeautifulSoup(page_content, 'html.parser')
        body = soup.html.body
        format_children(page, body, u"")
    return page


