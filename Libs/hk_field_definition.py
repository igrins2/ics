import os
import warnings

def get_hk_log_path():
    # webpath = cfg.get('HK','hk-web-location')
    #webpath = "/IGRINS/TEST/Log/Web"
    webpath = "/IGRINS/Log/Web"
    return os.path.join(webpath, "tempweb.dat")


HKLogPath = get_hk_log_path()


# FieldNames = ['da','ti','va','t1','h1','t2','h2','t3','h3','t4','h4','t5','h5','t6','t7','t8']

#change 20210107 by hilee
HkFieldNames = [('pressure', float),
                ('bench', float), ('bench_tc', float),
                ('grating', float), ('grating_tc', float),
                ('detS', float), ('detS_tc', float),
                ('detK', float), ('detK_tc', float),
                ('camH', float),
                ('detH', float), ('detH_tc', float),
                ('benchcen', float),
                ('coldhead01', float), 
                ('coldhead02', float), 
                ('coldstop', float), 
                ('charcoalbox', float),
                ('camK', float),
                ('shieldstop', float),
                ('air', float)]   


def read_item_to_upload():
    hk_entries_ = open(HKLogPath).read().split()

    log_date, log_time = hk_entries_[:2]
    hk_entries = hk_entries_[2:]
    HK_dict = hk_entries_to_dict(log_date, log_time, hk_entries)

    return HK_dict


def hk_entries_to_dict(log_date, log_time, hk_entries):
    
    #add 20210107 by hilee
    hk_entries = hk_entries[:-1]

    if len(hk_entries) != len(HkFieldNames):
        warnings.warn("hk_entries has %d length, while %d is expected" %
                      (len(hk_entries), len(HkFieldNames)))
        return None

    HK_dict = dict((k, t(v)) for (k, t), v in zip(HkFieldNames, hk_entries))

    HK_dict["date"] = log_date
    HK_dict["time"] = log_time
    HK_dict["datetime"] = log_date + "T" + log_time + "+00:00"

    return HK_dict
