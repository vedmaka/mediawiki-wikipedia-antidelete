# -*- coding: UTF-8 -*-

# This filter strips out all broken links and templates away from source page

import mwparserfromhell


def filter_text(text):
    parsed = mwparserfromhell.parse(text)

    # Remove all templates since we had no templates
    for template in parsed.filter_templates():
        parsed.remove(template)

    # Remove all links (because they all are broken)
    for link in parsed.filter_wikilinks():
        print "Found link %s" % link.title
        parsed.replace(link, link.title)
    return unicode(parsed)
