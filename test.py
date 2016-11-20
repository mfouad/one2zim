import zimencoder
import io


content = None
path = './test/TestOneNote.html' 
with io.open(path, 'r', encoding='utf-8') as f:
    content = f.read()
page = zimencoder.encode_page(path, "test", "now", content)
print page.__dict__
