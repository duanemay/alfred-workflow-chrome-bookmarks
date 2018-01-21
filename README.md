# Chrome Bookmarks Alfred 3 Workflow

This alfred3 workflow can search your Chrome Bookmarks across multiple Chrome Profiles.

## Features

1. Shows matching Chrome Bookmarks.
2. Matches and Displays the Title of bookmark, URL, and Folder name.
3. Fast relevant results, indexes in the background
4. Add and remove your chrome profiles to control which accounts are shown in search results  
5. Displays the icon for the Chrome Profile that owns the bookmark. 

## How to Use

Type `bm` to see your bookmarks

Start typing a query and the bookmarks get filtered.
 
Type `bm-add` or `bm-remove` then select a listed profile to customize profiles that are searched.

**Note:** `bm-remove` will show the profiles that are currently being searched.
`bm-add` will show all available profiles

## Getting ChromeBookmarks

### From Packal

The workflow is available for download from Packal, here: http://www.packal.org/workflow/chromebookmarks

### From Github

If you clone the code from github, you will
need to install the dependencies

```bash
pip install --target=. Alfred-Workflow
pip install --target=. Whoosh
```

## Todo

1. ~~Search bookmarks.~~ *(available in v1.1)*
2. ~~add and remove profiles~~ *(available in v1.1)*
3. ~~Better relevance in search results~~ *(available in v1.2)*
4. ~~Move indexing to background~~ *(available in v1.2)*
5. Icon in results, show a small chrome icon in corner of the Profile icon
6. Ensure launch in correct profile in Chrome
