import io
import os
import zimencoder
import re

class OneNote:
    def __init__(self, api):
        self.api = api

    def fetch(self, url):
        res = self.api.get(url)
        res_json = res.json()
        if 'value' in res_json:
            return res_json["value"]
        else: 
            print res.text
            return None

    def fetch_html(self, url):
        res = self.api.get(url)
        return res.text

    def fetch_binary(self, url):
        res = self.api.get(url)
        return res.content
        

    def mkdir(self, path):
        try: 
            os.mkdir(path)
        except OSError:
            pass

    # creates a file and a dir with the name of the object
    def create(self, parent_path, name):
        clean_name = "_".join(re.findall("[a-zA-Z]+", name))
        path = os.path.join(parent_path, clean_name)
        self.mkdir(path)
        
        return (path, clean_name)

    def get_notebooks(self):
        home_path = os.path.abspath("Notebooks")
        self.mkdir(home_path)
        zimencoder.encode_notebook(home_path, "ImportedFromOneNote")

        notebooks = self.fetch('https://www.onenote.com/api/v1.0/me/notes/notebooks')
        for notebook in notebooks:
            print(notebook["name"], notebook["lastModifiedTime"])
            (notebook_path, notebook_name) = self.create(home_path, notebook["name"])
            zimencoder.encode_notebook(notebook_path, notebook_name)
            zimencoder.encode_page(notebook_path, notebook_name, notebook['createdTime'], u"")

            sections = self.fetch(notebook["sectionsUrl"])
            if sections is None:
                continue
            for section in sections:
                print(section["name"], section["lastModifiedTime"])

                (section_path, section_name) = self.create(notebook_path, section["name"])
                zimencoder.encode_page(section_path, section_name, section['createdTime'], u"")
                
                pages = self.fetch(section["pagesUrl"])
                for page in pages:
                    print(page["title"], page["id"], page["contentUrl"])
                    
                    (page_path, page_name)  = self.create(section_path, page["title"])
                    content = self.fetch_html(page["contentUrl"])
                    with io.open(page_path + ".html", 'w', encoding='utf-8') as fpage:
                        fpage.write(unicode(content))

                    page_info = zimencoder.encode_page(page_path, page_name, page['createdTime'], content)
                    # if it has images, make a dir for the page
                    if len(page_info.images) > 0:
                        self.mkdir(page_path)
                    for image_name, image_url in page_info.images.iteritems():
                        print(image_name, image_url)
                        image_path = os.path.join(page_path, image_name)
                        image_content = self.fetch_binary(image_url)
                        with io.open(image_path, 'wb') as fimage:
                            fimage.write(image_content)


    def import_all(self):       
        self.get_notebooks()

        