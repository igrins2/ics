import firebase_admin
import firebase_admin.db
from firebase_admin import credentials
import logging
# import time


def get_firebase_from(certificate_name, databaseURL):
    # Fetch the service account key JSON file contents
    cred = credentials.Certificate(certificate_name)

    app_name = '[DEFAULT]'
    if app_name in firebase_admin._apps:
        app = firebase_admin._apps["[DEFAULT]"]
        firebase_admin.delete_app(app)

    # Initialize the app with a service account, granting admin privileges
    firebase = firebase_admin.initialize_app(cred, {
        "databaseURL": databaseURL,
    })

    return firebase


def get_firebase_default():
    firebase = get_firebase_from("igrins-status-0513e0175271.json",
                                 "https://igrins-status.firebaseio.com")

    return firebase


def get_db(firebase_app):
    db = firebase_admin.db.reference(app=firebase_app)
    return db


class FailSafeUploader(object):
    def __init__(self, msg_queue, quit_event, get_firebase):
        """
        msg_queue : accept {"_task"=upload|quit, "_key"=fb_key}
        """

        self.get_firebase = get_firebase
        self.msg_queue = msg_queue
        self.quit_event = quit_event

        logging.warn("fb initialized")

    def push(self, db, parent, entry, key=None):
        if key is None:
            db.child(parent).push(entry)
        else:
            db.child(parent).child(key.replace(".", ":")).set(entry)

    def upload(self, default_parent, max_retry_count=5):
        last_msg = None
        do_loop_count = max_retry_count
        while do_loop_count > 0:
            if self.quit_event.is_set():
                break

            logging.warn("fb starting loop")
            firebase_app = self.get_firebase()
            db = get_db(firebase_app)

            try:
                while True:
                    if last_msg is not None:
                        msg = last_msg
                    else:
                        msg = self.msg_queue.get()

                    last_msg = msg.copy()

                    if self.quit_event.is_set() or (msg["_task"] == "quit"):
                        do_loop_count = 0
                        break
                    elif msg["_task"] == "upload":
                        msg.pop("_task")
                        parent = msg.pop("_parent", default_parent)
                        key = msg.pop("_key", None)
                        msg["timestamp"] = {".sv": "timestamp"}
                        logging.warn("fb uploading: {}".format(msg))
                        self.push(db, parent, msg, key=key)
                        logging.warn("fb uploaded")

                    last_msg = None

            except:
                import traceback
                traceback.print_exc()
                do_loop_count -= 1
            else:
                do_loop_count = max_retry_count

        # time.sleep(60)

        logging.warn("fb out of loop")


def test():
    from threading import Thread
    from queue import Queue

    print("starting")
    queue = Queue()
    uploader = FailSafeUploader(queue)
    t = Thread(target=uploader.upload)

    t.start()

    import time
    print("sleeping")
    time.sleep(5)

    queue.put(dict(_task="quit"))
    print("quit")
    t.join()
    print("joined")


# test()
def test_upload():
    uploader = FailSafeUploader(None, None, get_firebase_default)
    firebase_app = uploader.get_firebase()
    db = get_db(firebase_app)
    uploader.push(db, "UPLOAD_TEST", dict(my="test3"))


if __name__ == "__main__":
    test_upload()
