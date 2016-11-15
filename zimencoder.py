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

def create_page(page_path, page_meta):

    # Some verbose, usefull on large contents
    # to be aware that the program is still processing...
    title =  page_meta['title'] if 'title' in page_meta else page_meta['name']
    print u'Creating file: ' , title.encode('utf-8')

    fileOut = io.open(page_path + ".txt", 'w', encoding='utf-8')

    # Standard information at the start of any Zim file
    fileOut.write(u'Content-Type: text/x-zim-wiki\n')
    fileOut.write(u'Wiki-Format: zim 0.4\n')
    fileOut.write(u'Creation-Date: ' + page_meta['createdTime'] + u'\n')

    fileOut.write(u'\n====== ' + title + u' ======\n')
    fileOut.write(u'\n')

    return fileOut

def process_format(page, el, formatString):
    # for basic formatting tags (underline, bold, italic,...)
    # do the core job

    newLine = False

    # Open Wiki format
    page.pagefile.write(formatString)

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
    process_content(page, el, formatString)

    # Close Wiki format
    page.pagefile.write(formatString)

    # End of the trick for content finishing with a newline
    if newLine:
        page.pagefile.write(u'\n')

def process_content(page, elements, currentFormat):
    # "currentFormat" is a trick to close the Wiki format at end of each line
    # even if the format is applied to multi-lines
    # Nota: this trick would need to be be enhanced
    #       when multiple formats are nested

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
                page.pagefile.write(currentFormat)
                page.pagefile.write(u'\n')
                page.pagefile.write(currentFormat)

            
            elif el.name == 'h1':
                process_format(page, el, u'======')
            elif el.name == 'h2':
                process_format(page, el, u'=====')
            elif el.name == 'h3':
                process_format(page, el, u'====')
            elif el.name == 'h4':
                process_format(page, el, u'===')
            elif el.name == 'h5':
                process_format(page, el, u'==')

            # <u> tag stands for underline
            elif el.name == 'u':
                process_format(page, el, u'__')

            # <b> tag stands for bold
            elif el.name == 'b':
                process_format(page, el, u'**')

            # <i> tag stands fr italic
            elif el.name == 'i':
                process_format(page, el, u'//')

            # <s> tag stands for strike-through
            elif el.name == 's':
                process_format(page, el, u'~~')

            # cite cinverted to verbatim
            elif el.name == 'cite':
                process_format(page, el, u"''")

            # <span> tag can have different purposes according to arguments
            elif el.name == 'span':
                # Color "red" in NoteCase => I use "italic" in Zim
                attr = unicode(el.get('style'))
                if (attr == "color:#ff0000" or True):
                    process_format(page, el, u'//')
                # Other <span> contents are treated as plain text
                # You may add more cases according to your needs
                else:
                    print u"WARNING : unknown SPAN type", el.attrs
                    process_content(page, el, currentFormat)

            # <a> tag stands for links
            elif el.name == 'a':
                page.pagefile.write(u'[[')
                page.pagefile.write(el['href'])
                page.pagefile.write(u'|')
                process_content(page, el, currentFormat)
                page.pagefile.write(u']]')

            elif el.name == 'img':
                page.pagefile.write(u'{{')
                img_url = el.get('src')
                mime_type = el.get('data-src-type')
                img_file_name = unicode(uuid.uuid4()) + u'.png'
                page.images[img_file_name] = img_url
                page.pagefile.write(u'./' + img_file_name)
                    	# width="213" height="85" src="https://www.onenote.com/api/v1.0/me/notes/resources/0-3cf48f9de4474274b04d40880dc5bddc!1-46D6559BE479DE42!223/$value" 
                        # data-src-type="image/png"
                        # data-fullres-src="https://www.onenote.com/api/v1.0/me/notes/resources/0-3cf48f9de4474274b04d40880dc5bddc!1-46D6559BE479DE42!223/$value" 
                        # data-fullres-src-type="image/png" />
                page.pagefile.write(u'}}')


            elif el.name == 'td':
                page.pagefile.write(u'| ')
                process_content(page, el, currentFormat)
                page.pagefile.write(u' |')
            
            elif el.name in ['p', 'div', 'tr', 'table']: 
                process_content(page, el, currentFormat)
                page.pagefile.write(u'\n')

            elif el.name in ['ul', 'ol']: 
                process_content(page, el,  currentFormat + u'\t')

                # we should write out "currentFormat"" first before the astrisk
            elif el.name == 'li':
                # maintain indentation
                if currentFormat.find('\t') >= 0:
                    page.pagefile.write(currentFormat)    

                page.pagefile.write(u"* ")
                process_content(page, el, currentFormat)
                page.pagefile.write(u'\n')

            # In case program encounter a Tag which is not dealt with
            # according to your needs, you can then add specific bloc
            else:    
                print u'WARNING, unknown tag: ', el.name
                process_content(page, el, currentFormat)

        else:
            text = el.string
            # Delete the new line symbol at start of the line
            # This happens when there was a <br> just before
            # but <br> is already taken into account
            text = text.strip("\r\n\t")
            text = re.sub("^\n\r", '', text)
            page.pagefile.write(unicode(text))

def encode_page(page_path, page_meta, page_content=None):
    page = Page()
    page.images = {}
    page.pagefile = create_page(page_path, page_meta)
    if page_content:
        soup = BeautifulSoup(page_content, 'html.parser')
        body = soup.html.body
        process_content(page, body, u"")
    return page


