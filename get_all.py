import json
import urllib2


print 'loading'
#json_data=open('TUI_DS_S3PreviewPaths.json').read()
json_data=open('family-life.json').read()

data = json.loads(json_data)

total = len(data)

duplicates = []
for i, image_url in enumerate(data):
    print(str(i) + " of " + str(total) + " - " + image_url)
    url = 'https://m3fgod2lea.execute-api.eu-central-1.amazonaws.com/prod/query-one?url='+image_url+'&threshold=85'
    image_dup = len(json.loads(urllib2.urlopen(url).read())['suspects'])
    print "  > " + str(image_dup) + " > " + str(len(duplicates)) + " of " + str(i+1)
    if image_dup > 0:
        duplicates.append(image_dup)



print "TOTAL - " + str(len(duplicates)) + " duplicates out of " + str(total)