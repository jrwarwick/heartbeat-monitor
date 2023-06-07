import os
from bottle import route, request, response, run, template, debug
import json
import time
import datetime
import sqlite3
import requests
from threading import Thread, Event


## Monitor Thread
shutdown_event = Event()
service_period_event = Event()
DB_FILEPATH = "/db/heartbeat_monitor.db"
MONITORING_PERIOD_LENGTH =  60 * 5  #probably should be 120 or greater. Seconds.
COOLOFF_PERIOD =            60*60   #seconds
SIGNAL_URI_BASE =               os.environ['SIGNAL_URI_BASE']
NOTIFICATION_MESSAGE_PREFIX =   os.environ['NOTIFICATION_MESSAGE_PREFIX']
DEFAULT_NTFY_CHANNEL_NAME =     os.environ['DEFAULT_NTFY_CHANNEL_NAME']
ADAPTIVE_CARDS_WEBHOOK_URI =    os.environ['ADAPTIVE_CARDS_WEBHOOK_URI'] # pretty much MS Teams channel web hook.


def monitor():
    """
    The monitor function will constitute a separate execution thread
    responsible for periodically reading the registry and heartbeat
    records and issuing any and all outgoing notifications for overdue
    heartbeat signal records. 
    The monitor thread will not directly open the sqlite DB. 
    Instead, it will act a little bit like a client to the RESTful
    service offered by the other, bottle-based thread.
    Activity plan:
        http GET list of overdue heartbeats
        for each:
          evaluate severity and notification target/method
          evaluate cool off periods and blackouts
          if appropriate, then: issue alert
          inc/dec appropriately (blackout cycles or whatnot)
    """
    ###DEBUG###import pdb; pdb.set_trace()
    print("[monitor]: execution thread started.")
    print("           default/fallback ntfy channel configured for outgoing notifications: " + DEFAULT_NTFY_CHANNEL_NAME )
    for i in range(1000):
        #instead of time.sleep(120), look to this thread wait technique:
        service_period_event.wait(timeout=MONITORING_PERIOD_LENGTH) 
        if shutdown_event.is_set():
            break
        else:
            nowness = datetime.datetime.now()
            if not i % 10:
                print("[monitor]: iteration "+str(i)+".  ("+str(nowness)+")")
                #any kind of checkpoint here? a monitor watcher?
            rep_htreq = requests.get( SIGNAL_URI_BASE+"api/report")
            if rep_htreq.status_code == 200:
                ##print(rep_htreq.text)
                alerts = json.loads(rep_htreq.text)
                print(str(len(alerts['heartbeats'])))
                for j in range(len(alerts['heartbeats'])):
                    #TODO: determine if this is a ntfy channel or an email address, then branch accordingly
                    #print(" prep for alert: " + str(alerts['heartbeats'][j]['name']))
                    ##Super Simple:
                    ##msg = NOTIFICATION_MESSAGE_PREFIX + alerts['heartbeats'][j]['name']
                    ##alert_htreq = requests.post("https://ntfy.sh/" + DEFAULT_NTFY_CHANNEL_NAME, data=msg.encode(encoding='utf-8'))
                    #Slightly Fancier
                    msg = "Examine job/task " + alerts['heartbeats'][j]['name'] + " as it is overdue for a heartbeat signal!"
                    if alerts['heartbeats'][j]['last_alert_date']:
                        #2023-06-06 14:30:53
                        ready_date = datetime.datetime.srtptime(alerts['heartbeats'][j]['last_alert_date'],"%Y-%m-%d %H:%M:%S") + datetime.timedelta(0,COOLOFF_PERIOD)
                    else:
                        ready_date = nowness - datetime.timedelta(0,COOLOFF_PERIOD)
                    print("thresh hold date: " + str(ready_date) + " vs. " + str(nowness))
                    if nowness < ready_date:
                        print("Cooling off on this one...")
                    else:
                        #TODO: detection and branching and fallback based on notification addresses
                        # differing notifciation strategies probably need some dedicated functions too
                        if alerts['heartbeats'][j]['alert_address_primary'].startswith("http://"):
                                print(" alert_address_primary appears to be an HTTP URL (webhook?)")
                        elif alerts['heartbeats'][j]['alert_address_primary'].startswith("tel:"):
                                print(" alert_address_primary appears to be a TELephone number (sms?)")
                        elif alerts['heartbeats'][j]['alert_address_primary'].index("@") > 3:
                                print(" alert_address_primary appears to be an EMAIL ADDRESS")
                        else:
                                print(" alert_address_primary appears to be a simple string, so maybe a ntfy channel name?")
                        alert_htreq = requests.post("https://ntfy.sh/" + DEFAULT_NTFY_CHANNEL_NAME,
                                data=msg.encode(encoding='utf-8'),
                                headers={
                                        "Title": NOTIFICATION_MESSAGE_PREFIX ,
                                        "Priority": "High",
                                        "Tags": "warning"
                                })
                        if alert_htreq.status_code == 429:
                            #blackout, temporary double cooloff, but also fallback/escalate?
                            print("WARNING: too many requests to external service!")
                        print("\t outgoing http: "+str(alert_htreq.status_code) + "\t" + msg)
                        arec_htreq = requests.put( SIGNAL_URI_BASE+"api/alert/"+str(alerts['heartbeats'][j]['id']))
                        print("\t self http: "+str(arec_htreq.status_code) + "\t" + msg)
            else:
                print(str(rep_htreq.status_code))
                print(rep_htreq)
    print("[monitor]: execution thread shutting down on shutdown event signal.") # or expired...

monitor_thread = Thread(target=monitor)
monitor_thread.start()


## Web (Main) Thread
# Views - Management Web App
@route("/")
def homepage():
    genid = str(time.time_ns())
    return template('registration',msg="REGISTRATION URI: "+ SIGNAL_URI_BASE+"api/heartbeat/"+ genid )

# API - RESTful
#TODO: /api/ for OpenAPI stuff, and mimetypes
#TODO: edits/updates and deletes?
#TODO: some reasonable aliases and flexibility mods?
@route("/api/registry", method='POST')
def register():
    genid = str(time.time_ns())
    postdata = request.body.read()
    print(postdata)
    if postdata:
        if postdata[0] == '{':
            #then its json...
            params = json.loads(postdata)
            #TODO: for /api/export to be useful, we probably need to determine right here if postdata is a normal single registration
            # or if it is a whole-export/backup registry and act accordingly.
        else:
            params_name = request.params.get('name')
            params_period = request.params.get('period')
            params_notification_address = request.params.get('notification_address')
    if params_name and params_period:
        print(','.join((params_name,params_period,params_notification_address)) + "\n\t" + ','.join(request.params))
        db = sqlite3.connect(DB_FILEPATH)
        cursor = db.cursor() 
        #cursor.execute("INSERT into registry (name,period) VALUES('Test_"+genid+"',120)")
        cursor.execute("INSERT into registry (name,period,ALERT_ADDRESS_PRIMARY) VALUES(?,?,?)",(params_name,params_period,params_notification_address))
        client_message = "Registration successful, ID# " + str(cursor.lastrowid)
        #cursor.execute("SELECT * from registry")
        #rows = cursor.fetchall()
        #print(rows)
        db.commit()
        db.close()
    else:
        client_message = "Insufficient parameter data supplied! Try again?"
    return template('registration',msg=client_message+"<br/>  REGISTRATION ID "+genid)

@route("/api/registry", method='GET')
@route("/api/export", method='GET')
def registry_report():
    db = sqlite3.connect(DB_FILEPATH)
    cursor = db.cursor() 
    cursor.execute("SELECT * from registry")
    #row = await cursor.fetchone()
    rows = cursor.fetchall()
    if rows:
        #print(rows[0])
        x = rows.count
        datadict = [dict((cursor.description[i][0].lower(), value) for i, value in enumerate(row)) for row in rows]
    db.close()
    response.content_type = 'application/json; charset=UTF8' 
    return json.dumps({"monitor_registration": datadict})

@route("/api/flatline", method='GET')
@route("/api/report", method='GET')
def overdue_report():
    db = sqlite3.connect(DB_FILEPATH)
    cursor = db.cursor() 
    offset = str(6)+" minutes"
    cursor.execute("SELECT * from registry where datetime(coalesce(last_signal_date,datetime('now','-10000 minutes')),'6 minutes') < datetime('now')")
    #cursor.execute("SELECT * from registry where datetime(coalesce(last_signal_date,datetime('now','-10000 minutes')),?) < datetime('now')",offset)
    #cursor.execute("SELECT * from registry where coalesce(last_signal_date,datetime('now','-10 minutes')) < datetime('now')")
    #row = await cursor.fetchone()
    rows = cursor.fetchall()
    if rows:
        datadict = [dict((cursor.description[i][0].lower(), value) for i, value in enumerate(row)) for row in rows]
        x = rows.count
    db.close()
    #return json.dumps({"heartbeats": "ONE" + str(rows)})
    response.content_type = 'application/json; charset=UTF8' 
    return json.dumps({"heartbeats": datadict})

@route("/api/heartbeat/<identity>")
def record_signal(identity):
    """
    We are making a deliberate choice here. This is a down-in-the-trenches
    get-your-hands-dirty tool. So sometimes prim and proper refusal to do
    what is obvious intent is not appropriate.  Thus: any hit to this URI, 
    regardless of verb, should result in intended heartbeat recording.
    """
    if identity:
        print("\tincoming heartbeat, id by url")
    else:
        identity = request.params.get("identity")
        if identity:
            print("\tincoming heartbeat, id by params")
    print("\t\tidentity:  "+identity)
    if (identity.isnumeric()):
        print("\t\twhich is by numeric ID (not alias)")
    else:
        print("?")
        #TODO: is it too much to scan for CSV list-of-ID numbers?
    #TODO resolve name to ID
    db = sqlite3.connect(DB_FILEPATH)
    cursor = db.cursor() 
    cursor.execute("SELECT * from registry where id = ?",(identity,))
    ht_response = dict({'response': "ACK", 'id': identity, 'altid': "?"})
    rows = cursor.fetchall()
    if rows:
        #print(rows[0])
        datadict = [dict((cursor.description[i][0].lower(), value) for i, value in enumerate(row)) for row in rows]
        print ( datadict )
        ht_response['altid'] = datadict[0]['name']
        cursor.execute("UPDATE registry set last_signal_date = datetime('now') where ID = ?",(identity,))
        db.commit()
    else:
        response.status = 404
        ht_response['response']="NACK"
    db.close()
    response.content_type = 'application/json; charset=UTF8' 
    #return json.dumps({"response": "ACK", "id": identity, "altid": altid})
    return json.dumps(ht_response)

@route("/api/alert/<identity>", method='PUT')
def record_alert(identity):
    """
    Specifically: we need to record the fact that we *successfully* issued an alert.
    This is all part of flood-control (while keeping responsiveness highish)
    """
    if identity:
        print("\tincoming heartbeat, id by url")
    else:
        identity = request.params.get("identity")
        if identity:
            print("\tincoming heartbeat, id by params")
    print("\t\tidentity:  "+identity)
    if (identity.isnumeric()):
        print("\t\twhich is by numeric ID (not alias)")
    else:
        print("?")
        #TODO: is it too much to scan for CSV list-of-ID numbers?
    #TODO resolve name to ID
    db = sqlite3.connect(DB_FILEPATH)
    cursor = db.cursor() 
    cursor.execute("SELECT * from registry where id = ?",(identity,))
    ht_response = dict({'response': "ACK", 'id': identity, 'altid': "?"})
    rows = cursor.fetchall()
    if rows:
        #print(rows[0])
        datadict = [dict((cursor.description[i][0].lower(), value) for i, value in enumerate(row)) for row in rows]
        print ( datadict )
        ht_response['altid'] = datadict[0]['name']
        cursor.execute("UPDATE registry set last_alert_date = datetime('now') where ID = ?",(identity,))
        db.commit()
    else:
        response.status = 404
        ht_response['response']="NACK"
    db.close()
    response.content_type = 'application/json; charset=UTF8' 
    #return json.dumps({"response": "ACK", "id": identity, "altid": altid})
    return json.dumps(ht_response)

@route("/api/service_status", method='GET')
def service_status():
    db = sqlite3.connect(DB_FILEPATH)
    cursor = db.cursor() 
    cursor.execute("SELECT * from registry where name = 'heartbeat_monitor'")
    #row = await cursor.fetchone()
    rows = cursor.fetchall()
    if rows:
        ##datadict = [dict((cursor.description[i][0].lower(), value) for i, value in enumerate(row)) for row in rows]
        print(rows[0])
        x = rows.count
    else:
        response.status = 503
        x = 0
    db.close()
    teams_webhook_actioncard_post("SVC STATUS: " + str(x))
    response.content_type = 'application/json; charset=UTF8' 
    return json.dumps({'response':"ACK", 'service_status': str(x)})

def teams_webhook_actioncard_post(message):
    hook_uri=ADAPTIVE_CARDS_WEBHOOK_URI 
    #super simple
    card_payload = """
        {
            "@context": "https://schema.org/extensions",
            "@type": "MessageCard",
            "themeColor": "0072C6",
            "title": "Heartbeat Monitor Report",
            "text": "This is a simple text card, but you can add images, buttons, whatever! ;) """ + message + """ "  
        }
    """
    report_htreq = requests.post(hook_uri, data=card_payload.encode(encoding='utf-8'))
    print("\tMS Teams outgoing http: "+str(report_htreq.status_code) + "\t?" )


print("Consumption URI: " + SIGNAL_URI_BASE)
debug(True)
run(host="0.0.0.0",port=5000)

shutdown_event.set()
service_period_event.set()
print("Main-thread bottle run exited.")