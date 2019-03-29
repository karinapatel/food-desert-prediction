db.healthy.find({"full_data.geo" : {       $exists : true,       $ne : null}}).count()
