# -*- coding: UTF-8 -*-

import time

class DeletablePage:
    def __init__(self, conn, local, remote, page_name):
        self._page_name = page_name.replace(" ", "_")
        self._wikiLocal = local
        self._wikiRemote = remote
        self._conn = conn
        self._setup()
        pass

    def _setup(self):

        from AntiDelete import AntiDelete

        # Initialize remote & local pages
        self._page_remote = self._wikiRemote.Pages[self._page_name]
        self._page_local = self._wikiLocal.Pages[self._page_name]

        # Check if we can pull this page at all
        if not self._page_remote.exists or self._page_remote.redirect or self._page_remote.namespace is not 0:
            # TODO: add filters here
            self.canBeSaved = False
        else:
            self.canBeSaved = True

        # Check if local page exists
        if self._page_local.exists:
            self.alreadyPulled = True
        else:
            self.alreadyPulled = False

        self._canBeChecked = False
        if self.alreadyPulled:
            self._db_record = self._conn.getOne(table="wikipedia_antidelete", where=("page_title=%s", [self._page_name]))
            if self._db_record:
                if self._db_record.status == 'pending':
                    if self._db_record.created_at < (time.time() - AntiDelete.pendingTime):
                        self._canBeChecked = True
            else:
                print "page seems to be corrupted or old-known, fixed"
                self.save_db()  # fix it to check on next run
                # No record though page is already pulled, this means either corrupted run or this page already
                # was nominated years ago


    def check_update(self):
        if self._canBeChecked and self.alreadyPulled:
            if self._page_remote.exists:
                # Looks like page survived deletion, restore
                print "page survived"
                self.survived()
            else:
                # Looks like page is not
                print "page was deleted, forget"
                self.forget()
        else:
            print "page can not be checked/updated"

    def survived(self):
        print "marking this page as survived.."
        self._page_local.save(text="{{Survived}}", summary="Robots detected that page is survived deletion")
        self.update_db('survived')

    def forget(self):
        print "forgetting this page.."
        self.update_db('completed')

    def save_local(self):
        if self.canBeSaved and not self.alreadyPulled:
            self._page_local.save(text=self._page_remote.text(), summary="Saved from Wikipedia deletion list")
            self.save_db()
            self.canBeSaved = False
            self.alreadyPulled = True
            print "page pulled locally"
        else:
            print "page can not be saved locally (either already pulled or wrong namespace)"

    def save_db(self, status='pending'):
        self._conn.insert("wikipedia_antidelete", {
            'page_title': self._page_name,
            'page_namespace': 0,
            'page_id_remote': self._page_remote.pageid,
            'page_id_local': self._page_local.pageid,
            'page_revision_remote': self._page_remote.revision,
            'page_revision_local': self._page_local.revision,
            'created_at': time.time(),
            'updated_at': time.time(),
            'status': status
        })
        self._conn.commit()

    def update_db(self, status):
        self._conn.update("wikipedia_antidelete", {
            'status': status
        }, where=("page_id_remote = %s", [self._page_remote.pageid]))
        self._conn.commit()
