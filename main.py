from deletedwiki import AntiDelete

print "Starting up anti-deletion script ..."

ad = AntiDelete('config.cfg')
print "Config loaded, db connection initiated."

print "Starting already pulled pages update cycle.."
ad.update_pending()
print "All pulled pages updated."

print "Starting to fetch today's deletion pages list"
ad.fetch_deletion()

print "All done, bye!"
