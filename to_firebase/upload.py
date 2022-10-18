import sys
import os
import time
import datetime
import pytz

HKLogPath = "/IGRINS/TEST/Log/Web/tempweb.dat"
#HKLogPath = "/IGRINS/Log/Web/tempweb.dat"
# FieldNames = ['da','ti','va','t1','h1','t2','h2','t3','h3','t4','h4','t5','h5','t6','t7','t8']

FieldNames = [('date', str), ('time', str),
              ('pressure', float),
              ('bench', float), ('bench_tc', float),
              ('grating', float), ('grating_tc', float),
              ('detS', float), ('detS_tc', float),
              ('detK', float), ('detK_tc', float),
              ('camH', float),
              ('detH', float), ('detH_tc', float),
              ('benchcenter', float), ('coldhead01', float), 
              ('coldhead02', float), ('coldstop', float), 
              ('charcoalBox', float), ('camK', float), 
              ('shieldtop', float), ('air', float), 
              ('alert_status', str)]


def read_item_to_upload():
    HK_list = open(HKLogPath).read().split()
    # print(len(HK_list), len(FieldNames))

    if len(HK_list) != len(FieldNames):
        return None

    HK_dict = dict((k, t(v)) for (k, t), v in zip(FieldNames, HK_list))

    HK_dict["datetime"] = HK_dict["date"] + "T" + HK_dict["time"] + "+00:00"

    return HK_dict


import pyrebase


def get_firebase():
    config = {
        "apiKey": "AIzaSyCDUZO9ejB8LzKPtGB0_5xciByJvYI4IzY",
        "authDomain": "igrins2-hk.firebaseapp.com",
        "databaseURL": "https://igrins2-hk-default-rtdb.firebaseio.com",
        "storageBucket": "igrins2-hk.appspot.com",
        "serviceAccount": "igrins2-hk-firebase-adminsdk-qtt3q-073f6caf5b.json"
        }

    firebase = pyrebase.initialize_app(config)

    return firebase


def push_hk_entry(db, entry):
    db.child("BasicHK").push(entry)

def start_upload_to_firebase(db):

    while True:
        #result = firebase.get('/BasicHK', None)
        HK_dict = read_item_to_upload()
        if HK_dict is None:
            yield "Error" 

        else:

            HK_dict["utc_upload"] = datetime.datetime.now(pytz.utc).isoformat()
            #HK_dict["tel_name"] = telescope_name
            #firebase.put('/BasicHK', "upload", HK_dict)
            # fb.post('/BasicHK', HK_dict)

            if 1:
                push_hk_entry(db, HK_dict)

                last_entry = HK_dict

            yield HK_dict


def main():
    print('================================================\n'
           'IGRINS House Keeping Status Updater for Firebase\n'
           '                                Ctrl + C to exit\n'
           '================================================\n')


    while True:
        firebase = get_firebase()
        db = firebase.database()

        fb = start_upload_to_firebase(db)

        try:
            while True:
                sleep_time = 20 #60
                r = next(fb)
                if r == "Same":
                    print("Skipping, same as the last entry.")
                elif r == "Error":
                    print("Error reading the file, retrying in 10s.")
                    sleep_time = 10
                else:
                    print("Uploaded", r["date"], r["time"])

                time.sleep(sleep_time)

        except KeyboardInterrupt:
            print("Quit.")
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
    
