from json import loads
from urllib2 import Request, urlopen, URLError, HTTPError
from datetime import date, timedelta
import ConfigParser
import markup
from markup import oneliner as nest

config = ConfigParser.ConfigParser()
config.read('config.ini')

page = markup.page()
page.init(css=config.get('output', 'styles'),title=config.get('output', 'title'))

ndbaseurl = config.get('nzbdrone info', 'baseurl')
apikey = config.get('nzbdrone info', 'apikey')
today = str(date.today())
tomorrow = str(date.today()+timedelta(days=1))

def writeout(file,result):
    f = open(file,'w')
    f.write(result)
    f.close()

def validateconfig():
    if config.get('nzbdrone info', 'baseurl'):
        pass
    else:
        print "Please specify a url for NZBDrone in config.ini"
        page.div("Please specify a url for NZBDrone in config.ini",class_="show")
        writeout(config.get('output', 'filename') + '.html',str(page))
    if config.get('nzbdrone info', 'apikey'):
        pass
    else:
        print "Please specify an API key in config.ini"
        page.div("Please specify an API key in config.ini",class_="show")
        writeout(config.get('output', 'filename') + '.html',str(page))
        
validateconfig()
droneurl = "%s/api/calendar?start=%s&end=%s" % (ndbaseurl, today, tomorrow)

def createPage(droneurl):
    req = Request(droneurl, headers={"X-Api-Key" : apikey})
    try:
        response = urlopen(req)
    except HTTPError as e:
        return 'HTTPError: ', e.code
        page.div('HTTPError:' + str(e.code),class_="show")
        writeout(config.get('output', 'filename') + '.html',str(page))  
    except URLError as e:
        page.div('URLError: ' + str(e.reason),class_="show")
        writeout(config.get('output', 'filename') + '.html',str(page))  
    else:
        try:
            data = loads(response.read())
        except ValueError as e:
            page.div('ValueError: ' + str(e),class_="show")
            writeout(config.get('output', 'filename') + '.html',str(page))  
        else:
            if len(data) == 0:
                page.div("Uh oh! Doesn't look like you have any shows today! :(\nAdd more " + nest.a("here!",href=ndbaseurl),class_="show")
                writeout(config.get('output', 'filename') + '.html',str(page))            
            else:
                page.div(config.get('output', 'head'),id="head")
                for x in range(len(data)):
                    title = data[x]['title'].encode('utf-8')
                    series = data[x]['series']['title'].encode('utf-8')
                    airtime = data[x]['series']['airTime'].encode('utf-8')
                    overview = data[x]['overview'].encode('utf-8')
                    banner = data[x]['series']['images'][0]['url'].encode('utf-8')
                    if overview:
                        page.div(nest.img(src=banner,class_="roundimg") + nest.div(series + ": " + title, class_="title") + nest.div(airtime, class_="airtime") + nest.div(overview, class_="overview"), class_="show")
                    else:
                        page.div(nest.img(src=banner,class_="roundimg") + nest.div(series + ": " + title, class_="title") + nest.div(airtime, class_="airtime"), class_="show")
                writeout(config.get('output', 'filename') + '.html',str(page))       
          
createPage(droneurl)