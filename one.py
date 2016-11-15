import io
import os
import zimencoder

class OneNote:
    def __init__(self, api):
        self.api = api

    def fetch(self, url):
        res = self.api.get(url)
        res = res.json()
        return res["value"]

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

    def get_notebooks(self):
        home_path = os.path.abspath("Notebooks")
        zimencoder.encode_notebook(home_path, "ImportedFromOneNote")
        self.mkdir(home_path)

        notebooks = self.fetch('https://www.onenote.com/api/v1.0/me/notes/notebooks')
        for notebook in notebooks:
            print(notebook["name"], notebook["lastModifiedTime"])
            
            notebook_path = os.path.join(home_path, notebook["name"])
            self.mkdir(notebook_path)
            zimencoder.encode_notebook(notebook_path, notebook["name"])

            sections = self.fetch(notebook["sectionsUrl"])
            for section in sections:
                print(section["name"], section["lastModifiedTime"])
                section_path = os.path.join(notebook_path, section["name"])
                self.mkdir(section_path)
                zimencoder.encode_page(section_path, section, u"")
                pages = self.fetch(section["pagesUrl"])
                for page in pages:
                    print(page["title"], page["id"], page["contentUrl"])
                    page_path = os.path.join(section_path, page["title"])
                    content = self.fetch_html(page["contentUrl"])
                    with io.open(page_path + ".html", 'w', encoding='utf-8') as fpage:
                        fpage.write(unicode(content))

                    page_info = zimencoder.encode_page(page_path, page, content)
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

        