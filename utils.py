import requests, calendar, time
from iso8601 import parse_date
from tinydb import TinyDB, Query
from worker import conn

def retrieve_current_price(endpoint):


    response = requests.get(url=endpoint)
    data = response.json()

    updatedTime = data['time']['updatedISO']
    currentPrice = data['bpi']["USD"]['rate_float']

    parsed = parse_date(updatedTime)
    timetuple = parsed.timetuple()

    parsedTime = calendar.timegm(timetuple)

    #conn.set(str(int(time.time())), {'updatedTime': int(parsedTime), 'QueryTime': int(time.time()), 'currentPrice': currentPrice} )
    
    db = TinyDB('bpi.db')
    BPI = Query()
    db.insert({'updatedTime': int(parsedTime), 'QueryTime': int(time.time()), 'currentPrice': currentPrice})

    return