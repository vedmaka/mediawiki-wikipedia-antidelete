import ConfigParser
import mwclient
import mwparserfromhell
import datetime
import time
from simplemysql import SimpleMysql

# Initialize config

config = ConfigParser.RawConfigParser()
config.read('config.cfg')

# Load config values
protocol = config.get('Local', 'protocol')
domain = config.get('Local', 'domain')
prefix = config.get('Local', 'prefix')
login = config.get('Local', 'login')
password = config.get('Local', 'password')

use_db = config.get('Database', 'use_db')
if use_db:
    db_host = config.get('Database', 'host')
    db_database = config.get('Database', 'database')
    db_login = config.get('Database', 'login')
    db_password = config.get('Database', 'password')
    db_table = 'wikipedia_antidelete'
    conn = SimpleMysql(host=db_host, db=db_database, user=db_login, passwd=db_password)


# Login to the site
wikiLocal = mwclient.Site( (protocol, domain), prefix )
wikiLocal.login(login, password)

# Wikipedia
wikiRemote = mwclient.Site( ('https', 'en.wikipedia.org'), '/w/')
# wikiRemote.login(.., ..)

today = datetime.date.today().strftime('%Y_%B_') + '{d.day}'.format(d=datetime.date.today())
print "Today is %s" % today

deletionList = wikiRemote.Pages['Wikipedia:Articles_for_deletion/Log/'+today]
text = deletionList.text()

wikicode = mwparserfromhell.parse(text)
templates = wikicode.filter_templates()

pagesToSave = []

for template in templates:
    if template.name[:31] == "Wikipedia:Articles for deletion":
        pageName = template.name[32:]
        if "(2nd nomination)" in pageName:
            pageName = pageName.replace(" (2nd nomination)", "")
        pagesToSave.append(pageName)

if len(pagesToSave):
    print "Found %s pages to save:" % len(pagesToSave)
    for page in pagesToSave:
        print "\t - %s" % page.encode('utf-8')
        localPage = wikiLocal.Pages[page]
        if localPage.exists:
            print "\t\t [!] Already exists, skipped."
        else:
            remotePage = wikiRemote.Pages[page]
            if remotePage.exists:
                if remotePage.namespace == 0:
                    if not remotePage.redirect:
                        # TODO: add page content filters here
                        localPage.save(text=remotePage.text(), summary="Saved from deletion list on Wikipedia")
                        time.sleep(5)
                        print "\t\t [*] Imported."
                    else:
                        print "\t\t [-] Redirect, skipped."
                else:
                    print "\t\t [-] Unknown namespace, skipped."
            else:
                print "\t\t [!] Source page does not exists, skipped."
        time.sleep(5)
else:
    print "Nothing to do."
