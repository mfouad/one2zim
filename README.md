# one2zim
Converts OneNote notebooks hosted in OneDrive or Office365 to ZimWiki format

## Features

Below is a list of completed and planned featues. feel free to send a pull request with any features or fixes. 

### OneDrive and Office365
- [x] Login to personal OneDrive and download all notebooks including shared notebooks
- [ ] Login to Office365 work account and download all notebooks

### Images and simple content
- [x] Import notebooks, sections and pages
- [ ] Import section groups (currently all sections are imported but section group heirarchy is not maintained)
- [x] Import images
- [x] Maintain simple formatting (Bold, Italics, Underline, Highlight)
- [ ] Maintain text color (not supported by zim)
- [ ] Maintain indentation and lists
- [ ] Import numbered lists (all lists are imported as bullet lists)

### Advanced formatting
- [x] Import task lists (ToDo tags), and maintain the (ToDo/Done) status
- [x] Import simple tables, if each row contains only a single line
- [ ] Handle tables with complicated formatting and inline lists
- [ ] Import drawings
- [ ] Import voice and other embedded objects
- [ ] Import attached files

### HTML format
- [x] Beside zim format, Import original note in HTML format
- [ ] Fix images in original notes HTML to point to the downloaded images folder


## How to run

The code requires Python 2.7+ to run

```
export LIVE_CLIENT_ID='OFFICE_APP_ID'
export LIVE_CLIENT_SECRET='OFFICE_APP_TOKEN'

python server.py
```

A browser window will open and ask you to login to your Microsoft Account and to gain acces to read your notes.
once you approve access, it will download your notes to a folder called *Notebooks*.
