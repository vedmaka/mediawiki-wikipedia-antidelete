# -*- coding: UTF-8 -*-

import ConfigParser
import mwclient
import mwparserfromhell
import datetime
import time
import random

from simplemysql import SimpleMysql
from DeletablePage import DeletablePage


class AntiDelete:

    pendingTime = 60 * 60 * 24 * 7

    def __init__(self, config_file):
        self._config_file = config_file
        self._load_config()
        pass

    def _load_config(self):
        config = ConfigParser.RawConfigParser()
        config.read(self._config_file)

        # Load config values
        protocol = config.get('Local', 'protocol')
        domain = config.get('Local', 'domain')
        prefix = config.get('Local', 'prefix')
        login = config.get('Local', 'login')
        password = config.get('Local', 'password')

        # Load database settings
        db_host = config.get('Database', 'host')
        db_database = config.get('Database', 'database')
        db_login = config.get('Database', 'login')
        db_password = config.get('Database', 'password')
        db_table = 'wikipedia_antidelete'

        # Setup
        self._wikiLocal = mwclient.Site((protocol, domain), prefix)
        self._wikiLocal.login(login, password)

        self._wikiRemote = mwclient.Site(('https', 'en.wikipedia.org'), '/w/')

        self._db = SimpleMysql(host=db_host, db=db_database, user=db_login, passwd=db_password)

    def update_pending(self):
        # TODO: this method should check pending pages in database and update/remove them if needed
        self.store_stat(0, '', 'check_pending')
        pending = self._db.getAll("wikipedia_antidelete",
                                  where=(
                                      "status = %s and created_at < %s",
                                      ['pending', (time.time() - self.pendingTime)]
                                  ))
        if pending:
            print "Found %s pending pages" % len(pending)
            for page in pending:
                print "\t %s" % page.page_title.encode('utf-8')
                dpage = DeletablePage(self._db, self._wikiLocal, self._wikiRemote, page.page_title)
                dpage.check_update()
                time.sleep(random.randint(5, 10))

    def fetch_deletion(self):
        # TODO: this method should fetch actual (today's) deletion list and import (if needed) pages from it
        today_string = datetime.date.today().strftime('%Y_%B_') + '{d.day}'.format(d=datetime.date.today())
        deletionList = self._wikiRemote.Pages['Wikipedia:Articles_for_deletion/Log/' + today_string]
        # Store statistics
        self.store_stat(deletionList.touched, '', 'fetch')
        text = deletionList.text()
        wikicode = mwparserfromhell.parse(text)
        templates = wikicode.filter_templates()
        for template in templates:
            if template.name[:31] == "Wikipedia:Articles for deletion":
                pageName = template.name[32:]
                if "(2nd nomination)" in pageName:
                    pageName = pageName.replace(" (2nd nomination)", "")
                print "%s" % pageName.encode('utf-8')
                dpage = DeletablePage(self._db, self._wikiLocal, self._wikiRemote, pageName)
                dpage.save_local()
                time.sleep(random.randint(5, 10))

    def check_touched(self):
        # TODO: this method is experimental, should be tested carefully
        today_string = datetime.date.today().strftime('%Y_%B_') + '{d.day}'.format(d=datetime.date.today())
        deletionList = self._wikiRemote.Pages['Wikipedia:Articles_for_deletion/Log/' + today_string]
        # Fetch last record
        record = self._db.getOne("wikipedia_antidelete_log",
                                 fields="*",
                                 order=["created_at", "DESC"],
                                 where=("FROM_UNIXTIME(created_at, '%%Y-%%M-%%d')=%s AND status='fetch')", [datetime.date.today().strftime('%Y-%B-%d')])
                                 )
        if record:
            last_touched = record.touched
            if deletionList.touched != last_touched:
                # Indicate that deletion list has *not* changed since our last query
                self.store_stat(0, 'not_changed', 'check_touch')
                return False
        # Indicates either an error or deletion list *has* changed since our last query
        self.store_stat(0, 'changed', 'check_touch')
        return True

    def store_stat(self, touched, status, flag):
        self._db.insert("wikipedia_antidelete_log", {
            'touched': 0 if touched == 0 else time.mktime(touched),
            'status': status,
            'flag': flag,
            'created_at': time.time()
        })
        self._db.commit()
