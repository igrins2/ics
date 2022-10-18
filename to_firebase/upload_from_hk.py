import sys
import os
import time
import datetime
import pytz
import json

sys.path.append("..")
sys.path.append("../..")
sys.path.append("../../..")

import zmq
from ICSHub.icshub_client import MsgHubClient


telescope_list = ["HJST", "DCT", "GeminiSouth"]
# FieldNames = ['da','ti','va','t1','h1','t2','h2','t3','h3','t4','h4','t5','h5','t6','t7','t8']

# FieldNames = [('date', str), ('time', str),
#               ('pressure', float),
#               ('bench', float), ('bench_tc', float),
#               ('grating', float), ('grating_tc', float),
#               ('detH', float), ('detH_tc', float),
#               ('detK', float), ('detK_tc', float),
#               ('detS', float), ('detS_tc', float),
#               ('coldhead02', float), ('rack_computer', float),
#               ('rack_air', float), ('alert_status', str)]


from upload2fb_admin import get_firebase_from, get_db


def get_firebase():
    certificate_name = "hkp-db-45d38-firebase-adminsdk-3e1ho-1a900fb00f.json"
    databaseURL = "https://hkp-db-45d38.firebaseapp.com"

    firebase = get_firebase_from(certificate_name, databaseURL)

    return firebase


# def get_most_recent_hk_entry(db):
#     """
#     """
#     item = db.child("BasicHK").order_by_child("utc_upload").limit_to_last(1).get()
#     vs = list(item.val().values())

#     if vs:
#         return vs[0]
#     else:
#         return None

def push_hk_entry(db, entry):
    db.child("BasicHK").push(entry)


def start_upload_to_firebase(db, telescope_name):

    # last_entry = get_most_recent_hk_entry(db)

    HK_dict = (yield)

    while True:
        #result = firebase.get('/BasicHK', None)
        if HK_dict is None:
            msg = "Error"

        # elif last_entry and \
        #    (HK_dict["date"] == last_entry["date"]) and \
        #    (HK_dict["time"] == last_entry["time"]):

        #     msg = "Same"

        else:

            HK_dict["utc_upload"] = datetime.datetime.now(pytz.utc).isoformat()
            HK_dict["tel_name"] = telescope_name
            #firebase.put('/BasicHK', "upload", HK_dict)
            # fb.post('/BasicHK', HK_dict)

            if 1:
                push_hk_entry(db, HK_dict)
                # print("pushing", HK_dict)

            msg = HK_dict

        HK_dict = (yield msg)


def main(telescope_name):
    print ('================================================\n'
           'IGRINS House Keeping Status Updater for Firebase\n'
           '                                Ctrl + C to exit\n'
           '================================================\n')

    while True:

        identity = "ICS-UPLOAD2FB"

        msghub_client = MsgHubClient(context, identity,
                                     tag=b"hk-entries")
        # msghub_client.sub_socket.subscribe("hk-entries")

        firebase = get_firebase()
        db = get_db(firebase)

        fb = start_upload_to_firebase(db, telescope_name)
        next(fb)
        timestamp_prev = None

        try:
            while True:
                msg_ = msghub_client.wait_for_sub()

                timestamp_cur = datetime.datetime.now()
                if (msg_ and ((timestamp_prev is None) or
                             ((timestamp_cur - timestamp_prev).total_seconds() > 60))):
                    tag, msg = msg_.split(b'\0')
                    print("sending", msg)
                    hk_entries = json.loads(json.loads(msg)["msg"])
                    status = fb.send(hk_entries)
                else:
                    status = None

                if status is None:
                    print ("less than 60s from the last upload")
                elif status == "Error":
                    print ("Error uploading to fb")
                else:
                    timestamp_prev = timestamp_cur
                    if ("date" in status) and ("time" in status): 
                        print ("Uploaded", status["date"], status["time"])
                    else:
                        print ("Something wrong", status)

        except KeyboardInterrupt:
            print ("Quit.")
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        except:
            import traceback
            traceback.print_exc()
        finally:
            msghub_client.close_sockets()


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2 and sys.argv[1] in telescope_list:
        main(sys.argv[1])
    else:
        telescope_names = ", ".join(telescope_list)
        print ("The first argument must be a name of telescope [%s]" % \
            (telescope_names,))
