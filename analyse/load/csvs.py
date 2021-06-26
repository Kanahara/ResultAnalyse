import load
import joblib


def csvs(csvs_info, dtype, parallel_key=None):
    csv_list = joblib.Parallel(n_jobs=-1, verbose=0)(
        [joblib.delayed(load.csv)(path, dtype, p_key) for path, p_key in csvs_info]
    )
    csv_dict = {}
    for key, csv in csv_list:
        csv_dict[key] = csv
    return parallel_key, csv_dict