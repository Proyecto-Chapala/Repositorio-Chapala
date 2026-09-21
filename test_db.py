import psycopg2
try:
    psycopg2.connect(dbname='chapala_db', user='admin', password='admin6767', host='localhost', port='5432')
    print("SUCCESS")
except psycopg2.OperationalError as e:
    # Get the raw bytes if possible, or encode to latin1 and decode to utf8
    raw_msg = e.pgerror if e.pgerror else str(e)
    try:
        print("ERROR_DECODED:", raw_msg.encode('latin1').decode('utf8'))
    except:
        print("ERROR_RAW:", repr(raw_msg))
except Exception as e:
    print("OTHER_ERROR:", repr(e))

