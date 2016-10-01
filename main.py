import ConfigParser
import mwclient
import mwparserfromhell
import datetime

#Initialize config
config = ConfigParser.RawConfigParser()
config.read('config.cfg')

#Load config values
protocol = config.get('Local', 'protocol')
domain = config.get('Local', 'domain')
prefix = config.get('Local', 'prefix')
login = config.get('Local', 'login')
password = config.get('Local', 'password')

#Login to the site
wikiLocal = mwclient.Site( (protocol, domain), prefix )
wikiLocal.login(login, password)

#Wikipedia
wikiRemote = mwclient.Site( ('https', 'en.wikipedia.org'), '/w/' )
#wikiRemote.login(.., ..)

today = datetime.date.today().strftime('%Y_%B_%-d') #will not work on Windows
deletionList = wikiRemote.Pages['Wikipedia:Articles_for_deletion/Log/'+today]
text = deletionList.text()

wikicode = mwparserfromhell.parse(text)
templates = wikicode.filter_templates()
for template in templates:
    if template.name[:31] == "Wikipedia:Articles for deletion":
        print "."