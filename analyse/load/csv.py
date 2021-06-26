import pandas as pd


def csv(file_path, dtype, parallel_key=None):
    names = tuple(dtype.keys())
    try:
        # print("--start--load--" + file_path)
        data = pd.read_csv(file_path, names=names, dtype=dtype)
        # print("--end----load--")
        return parallel_key, data
    except FileNotFoundError:
        print("--not----found--" + file_path)
        return parallel_key, pd.DataFrame(columns=dtype.keys())
    except Exception as e:
        print("--error---------" + file_path)
        print(e)
        return parallel_key, pd.DataFrame(columns=dtype.keys())
