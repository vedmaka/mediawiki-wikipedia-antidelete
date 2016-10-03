from deletedwiki import AntiDelete

print "Starting up anti-deletion script ..."

ad = AntiDelete('config.cfg')
print "Config loaded, db connection initiated."

print "Checking is there are changes in deletion script.."
# TODO: to be improved
#if ad.check_touched():
print "Deletion list changed.."
print "Starting already pulled pages update cycle.."
ad.update_pending()
print "All pulled pages updated."
print "Starting to fetch today's deletion pages list"
ad.fetch_deletion()
#else:
#    print "No changes detected."

print "All done, bye!"
