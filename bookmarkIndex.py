#!/usr/bin/python
# encoding: utf-8

import codecs
import json
import sys
import time
from os.path import expanduser, isfile

from whoosh import index, qparser, query, fields
from whoosh.fields import NGRAMWORDS, STORED, NUMERIC, TEXT
from workflow import Workflow3


class BookmarkSchema(fields.SchemaClass):
    contentNgram = NGRAMWORDS(minsize=2, maxsize=4, stored=False, queryor=True)
    contentFull = TEXT(stored=False)
    urlSize = NUMERIC(signed=False, sortable=True, default=999)
    name = STORED()
    path = STORED()
    profile = STORED()
    url = STORED()
    icon = STORED()


class BookmarkIndex:

    def __init__(self, wf):
        self._wf = wf
        self._indexName = "bookmarks"
        self._cacheDir = wf.cachedir
        self._schema = BookmarkSchema()

    def get_bookmarks(self, profiles, writer):
        wf = self._wf
        for profile in profiles:
            profile_dir = expanduser("~/Library/Application Support/Google/Chrome/%s" % profile)
            icon_file = profile_dir + "/Google Profile Picture.png"
            if not isfile(icon_file):
                icon_file = "icon.png"

            bookmark_filename = profile_dir + "/Bookmarks"
            if isfile(bookmark_filename):
                wf.logger.info("Searching file: %s", bookmark_filename)
                bookmark_file = codecs.open(bookmark_filename, encoding='utf-8')
                bookmark_data = json.load(bookmark_file)
                roots = bookmark_data["roots"]

                for key in roots:
                    self.get_bookmark_tree(roots[key], writer, "", icon_file, profile)

        return

    def get_bookmark_tree(self, tree, writer, path, icon_filename, profile):
        if type(tree) is not dict:
            return
        for i, item in enumerate(tree["children"]):
            name = item['name']
            item_path = path + " : " + name if path != "" else name
            if "children" in item:
                self.get_bookmark_tree(item, writer, item_path, icon_filename, profile)
            else:
                url = item['url']
                content = name + "  " + path + "  " + url + "  " + profile
                writer.add_document(contentNgram=content,
                                    contentFull=content,
                                    name=name,
                                    url=url,
                                    path=path,
                                    profile=profile,
                                    icon=icon_filename,
                                    urlSize=len(url))

    def index_profiles(self, profiles):
        wf = self._wf
        wf.logger.info("Using cache dir: %s", self._cacheDir)

        wf.logger.info("Building the search index")
        the_index = index.create_in(self._cacheDir, schema=self._schema, indexname=self._indexName)
        writer = the_index.writer(limitmb=512)
        self.get_bookmarks(profiles, writer)
        writer.commit()
        wf.logger.info("Building the search index, DONE")
        wf.cache_data('freshIndex', True)

        return the_index

    def open_index(self):
        wf = self._wf
        wf.logger.info("Opening the search index in cache dir: %s", self._cacheDir)
        return index.open_dir(self._cacheDir, indexname=self._indexName)

    def get_index(self, profiles):
        index_exists = index.exists_in(self._cacheDir, indexname=self._indexName)
        if index_exists:
            ix = self.open_index()
        else:
            ix = self.index_profiles(profiles)

        return ix

    def parse_query(self, query_string):
        og = qparser.OrGroup.factory(0.9)
        parser = qparser.QueryParser("contentNgram", self._schema, group=og)
        #parser.remove_plugin_class(qparser.FieldsPlugin)
        #parser.add_plugin(qparser.FuzzyTermPlugin())
        return parser.parse(query_string)

    @staticmethod
    def all_query():
        return query.Every()

    def prefix_query(self, query_string):
        return query.Prefix("contentFull", query_string)


if __name__ == u"__main__":
    start = time.time()
    workflow = Workflow3()
    bi = BookmarkIndex(workflow)
    profilesToIndex = workflow.settings.setdefault("profiles", ["Default"])
    whoosh_index = bi.index_profiles(profilesToIndex)
    end = time.time()
    with whoosh_index.searcher() as searcher:
        numDocs = searcher.doc_count()
    time = end - start
    workflow.logger.info("Indexed %d documents, in %f seconds.", numDocs, time)

    sys.exit(0)
