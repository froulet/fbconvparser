
#System imports
from bs4 import BeautifulSoup
import re
import sys
import csv
import urlparse
import time
import argparse
import ConfigParser

#Third-party imports
import mechanize


# Function use to strip html tags
def strip_html(data):
    #Extract the list from the first position of the array and convert it to string
    cleandata = to_text(data)
    #we strip the html tags from the string
    p = re.compile(r'<.*?>')
    return p.sub('', cleandata)

#Transform and concat all the data to string
def to_text(data):

    data = to_string(data)
    fullstring = ''
    for elem in data:
        if len(data) > 1:
            fullstring += str(elem) + " "
        else:
            fullstring += str(elem)
    return fullstring

#Transform int to string
def to_string(data):
    if isinstance( data, int ):
        return str(data)
    else:
        return data

#Logger function
def Logger(data):
    global args
    if args.log:
        log = data + get_date_hour()
        write_text_to_file("log", log)

def get_date_hour():
    return " - " + time.strftime("%d-%m-%Y") +"-"+ time.strftime("%H:%M:%S")

#We extract
def save_media(response):
    #We get the html source code
    soup = BeautifulSoup(html)
    cols = soup.findAll('div', attrs={"id" : 'messageGroup'})

    try:
        messages = soup.select("#messageGroup > div:nth-of-type(2) > div")
        print "\n"+str((len(messages))) + " messages on this page \n"


        for mess in reversed(messages):
            #We get the global var counter
            global counter

            textmess = mess.findAll("span")
            sender = mess.select("div:nth-of-type(1) >  a >  strong")
            date = mess.findAll("abbr")

            print strip_html(date)+"\n"

            # We put all the stripped data in a dic
            data = {"nb": strip_html(counter), "text": strip_html(textmess),
            "sender": strip_html(sender), "date":strip_html(date)}

            global args
            # To Refacto
            if args.format == 'txt':
                write_to_file(args.name, data)
            if args.format == 'csv':
                write_to_csv(args.name, data)


            #Increment and print it
            counter += 1
            #Logger("Total number of messages saved : " + str(counter))
            print "Total number of messages saved : " + str(counter)

        older = soup.find('div', attrs={"id" : 'see_older'}).find('a')
        #print cols[0].renderContents() # print content of first <td> element
        #all_text = ''.join(messages.findAll(text=True))
        #print all_text
        return older['href']

    except AttributeError:
        return None

def browse(url):
    print(url)
    Logger(url)
    html= get_page(url)

    while html is None:
        print "\n !!!! html is none, incrementing !!!! \n"
        Logger("html is none, incrementing")
        url=increment_start(url)
        html=get_page(url)

    return html

def get_page(url):
    #We try to open the page
    try:
        resp = browser.open(url)
        return resp.read()
    except mechanize.HTTPError, e:
        # handle http errors explicit by code
        if int(e.code) == 500:
            print "\n ///////////// ERROR 500 ///////////// \n"
            return None
        elif int(e.code) == 404:
            print "\n  \n"
            Logger(url+" : ///////////// ERROR 404 : PAGE NOT FOUND /////////////")
            raise Exception('This is the exception you expect to handle')
        else:
            raise e  # if http error code is not 500, reraise the exception
            return None

def send_message(url, message):
    try:
        #We try to open the page
        browser.open(url)
        #We select the second form
        browser.select_form(nr = 1)
        #we write in the textearea with 'name = "body"'
        browser['body'] = message
        browser.submit()
    except Exception as error:
        print("Message couldn't be sent ...")


def increment_start(url):
    parsed = urlparse.urlparse(url)
    start=urlparse.parse_qs(parsed.query)['start']
    start = int(start[0]) + 5
    return "https://mbasic.facebook.com/messages/read/?tid="+convid+"&start="+str(start)

def write_to_file(file, data):
    f = open(file+'.txt', 'a')
    f.write("\n")
    f.write(data['sender']+"\n")
    f.write(data['text']+"\n")
    f.write(data['date']+"\n")
    f.close()

def write_to_csv(file, data):
    with open(file+'.csv', 'a') as csvfile:
        fieldnames = ['nb','sender', 'text', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #writer.writeheader()
        writer.writerow({'nb': data['nb'], 'sender': data['sender'], 'text':data['text'], 'date':data['date']})

def write_text_to_file(file, text):
    f = open(file+'.txt', 'a')
    f.write("\n")
    f.write(text+"\n")
    f.close()

def fill_requirements():

    #Read the configuration file
    config = ConfigParser.ConfigParser()
    config.readfp(open('conf.cfg'))
    # print config.get('Ids', 'email')
    # print config.get('Ids', 'password')

    parser = argparse.ArgumentParser()
    parser.add_argument("--verbosity", help="increase output verbosity", default="1")

    #Email and passwords, default from conf.cfg, can be overwritten
    parser.add_argument("--email", help="Overwrite email adress", default=config.get('Ids', 'email'))
    parser.add_argument("--password", help="Overwrite password", default=config.get('Ids', 'password'))

    # !! Required !!
    parser.add_argument("--convid", help="Id of the conversation")
    parser.add_argument("--name", help="Name you want to give to the output file")

    parser.add_argument("--format", help="Choose default storing format (txt or csv)", default='txt')
    parser.add_argument("--log", help="change to true to log parsing", default=False)
    parser.add_argument("--start", help="Start from a certain page", default=0)

    global args
    args = parser.parse_args()
    args.name = args.name + get_date_hour()


#/////////////Main Logic/////////////
#Create the Browser Agent
browser = mechanize.Browser()
browser.set_handle_robots(False)
cookies = mechanize.CookieJar()
browser.set_cookiejar(cookies)
browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7')]
browser.set_handle_refresh(False)


fill_requirements()

global args

#Login
url = 'https://mbasic.facebook.com/login.php'
browser.open(url)
browser.select_form(nr = 0)       #This is login-password form -> nr = number = 0
browser.form['email'] = args.email
browser.form['pass'] = args.password
response = browser.submit()

#Initialization of the messages's counter
global counter
counter = 0

#send_message('https://m.facebook.com/messages/read/?tid='+args.convid, "Kek")
#exit()

try:
    if args.start != 0:
        html = browse('https://mbasic.facebook.com/messages/read/?tid='+args.convid+"&start="+args.start)
    else:
        html = browse('https://mbasic.facebook.com/messages/read/?tid='+args.convid)
except Exception as error:
    print("Page's conversation couldn't be reached.")
    exit()

see_older=save_media(html)

#sys.exit()

#While there is a 'see older' link in the page
while see_older:
    html = browse('https://mbasic.facebook.com'+see_older)
    see_older=save_media(html)

write_text_to_file(args.name, str(counter) + " messages ")

print ("///////////////////////////// END ! /////////////////////////////////")
