# We are going to use a blocking scheduler
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
from rq import Queue
from worker import conn
from utils import retrieve_current_price

q = Queue(connection=conn)

endpoint = "https://api.coindesk.com/v1/bpi/currentprice/USD.json"

#To attach the needed metadata we use a decorator
#Coinbase publishes prices every minute (60 seconds)

@sched.scheduled_job('interval', minutes=1)
def retrieve_current_price_job():

     q.enqueue(retrieve_current_price, endpoint)

sched.start()