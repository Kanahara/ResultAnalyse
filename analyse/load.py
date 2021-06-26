import numpy as np
import pandas as pd
import math
import csv
import io
import joblib


def read_csv_with_try_except(key, file_path, dtype):
    names = tuple(dtype.keys())
    try:
        # print("--start--load--" + file_path)
        data = pd.read_csv(file_path, names=names, dtype=dtype)
        # print("--end----load--")
        return key, data
    except FileNotFoundError:
        print("--not----found--" + file_path)
        return key, pd.DataFrame(columns=dtype.keys())
    except Exception as e:
        print("--error---------" + file_path)
        print(e)
        return key, pd.DataFrame(columns=dtype.keys())


def groupby(key, dataframe, column_not_in_group, trial_num):
    columns = list(dataframe.columns)
    value_columns = []
    for column in column_not_in_group:
        if column in columns:
            columns.remove(column)
            value_columns.append(column)
    if columns == len(list(dataframe.columns)):
        return key, dataframe
    else:
        group_df = dataframe.groupby(columns, as_index=False).sum()
        group_df[value_columns] /= trial_num
        return key, group_df


def load_result(problem, instances, path, parallel_num, trial_num=100):
    result_list = joblib.Parallel(n_jobs=-1, verbose=10)(
        [joblib.delayed(load_result_instance)(problem, instances.iloc[instance_num], path, trial_num) for instance_num in range(len(instances))]
    )
    # シーケンシャル
    # result_list = [make_result(problem, instances.iloc[instance_num], path, trial_num) for instance_num in range(len(instances))]

    result = pd.DataFrame()
    if len(result_list) > 0:
        result = pd.concat(result_list)
    return parallel_num, result


def load_result_instance(problem, instance, path, trial_num):
    key, data = read_csv_with_try_except(key="", file_path=path + "/" + instance["name"] + ".csv",
                                         dtype={"最良解値": np.uint64, "最良解算出時間": np.float64, "探索時間": np.float64})

    return make_result_instance(data, problem, instance, path, trial_num)



def load_log(problem, instances, path, parallel_num):
    load_log_instance = None
    if problem["name"] == "mcp":
        load_log_instance = load_mcp_instance_log
    elif problem["name"] == "cpmp":
        load_log_instance = load_cpmp_log

    logs = joblib.Parallel(n_jobs=-1, verbose=0)(
        [joblib.delayed(load_log_instance)(instances.iloc[i], path) for i in range(len(instances))]
    )
    # シーケンシャル
    # logs = [load_mcp_instance_log(instances.iloc[i], data_lists[instances["name"][i]], path_list)  for i in range(len(instances))]

    all_log = {}
    for instance, log in logs:
        all_log[instance["name"]] = log

    return parallel_num, all_log


def load_mcp_instance_log(instance, path):
    log = dict()
    log["クリーク"] = load_result_clique(instance=instance, path=path)
    if len(log["クリーク"]) != 0:
        normal_logs = [
            dict(key="結果", type_id="",
                 dtype={"最良解値": np.uint64, "最良解算出時間": np.float64, "探索時間": np.float64}),
            dict(key="終了直前", type_id="_last_",
                 dtype={"排他的要素数": np.uint64, "クリークサイズ": np.uint64, "PAサイズ": np.uint64, "辺不足数": np.uint64})
        ]
        group_logs = [
            dict(key="終了直前カウント", type_id="_count_",
                 dtype={"カウントID": np.uint64, "回数": np.uint64}),

            dict(key="モードカウント", type_id="_mode_count_",
                 dtype={"カウントID": np.uint64, "割合": np.float64}),

            dict(key="探索頻度", type_id="_search_frequency_",
                 dtype={"頻度": np.float64, "割合": np.float64}),
            dict(key="クリーク頂点探索頻度", type_id="_clique_search_frequency_",
                 dtype={"頻度": np.float64, "割合": np.float64}),
            dict(key="クリークサイズ頻度", type_id="_clique_size_frequency_",
                 dtype={"クリークサイズ": np.uint64, "割合": np.float64}),
            dict(key="PAサイズ頻度", type_id="_pa_size_frequency_",
                 dtype={"PAサイズ": np.uint64, "割合": np.float64}),
            dict(key="辺不足数頻度", type_id="_missing_frequency_",
                 dtype={"辺不足数": np.uint64, "割合": np.float64}),
            dict(key="キック後排他的要素数頻度", type_id="_exclusive_size_frequency_after_kick_",
                 dtype={"排他的要素数": np.uint64, "割合": np.float64}),
            dict(key="リスタート後排他的要素数頻度", type_id="_exclusive_size_frequency_after_restart_",
                 dtype={"排他的要素数": np.uint64, "割合": np.float64}),

            dict(key="クリークサイズ時_PAサイズ", type_id="_pa_size_for_cc_size_",
                 dtype={"クリークサイズ": np.uint64, "PAサイズ": np.uint64, "割合": np.float64}),
            dict(key="クリークサイズ時_キック後排他的要素数", type_id="_exclusive_size_for_local_cc_size_after_kick_",
                 dtype={"クリークサイズ": np.uint64, "前回クリークサイズ": np.uint64, "排他的要素数": np.uint64, "辺不足数": np.uint64, "割合": np.float64}),
            dict(key="クリークサイズ時_リスタート後排他的要素数", type_id="_exclusive_size_for_local_cc_size_after_restart_",
                 dtype={"クリークサイズ": np.uint64, "前回クリークサイズ": np.uint64, "排他的要素数": np.uint64, "割合": np.float64})
        ]
        log_types = normal_logs + group_logs
        read_logs = joblib.Parallel(n_jobs=-1, verbose=0)(
            [joblib.delayed(read_csv_with_try_except)(key=log_type["key"], file_path=path + "/" + instance["name"] + log_type["type_id"] + ".csv", dtype=log_type["dtype"]) for log_type in log_types]
        )
        for key, read_log in read_logs:
            log[key] = read_log

        read_logs = joblib.Parallel(n_jobs=-1, verbose=0)(
            [joblib.delayed(groupby)(key=log_type["key"], dataframe=log[log_type["key"]], column_not_in_group=["割合", "回数"], trial_num=len(log["クリーク"])) for log_type in group_logs]
        )
        for key, read_log in read_logs:
            log[key] = read_log

        ########################################

        log["history"] = load_history(instance=instance, path=path)

        ########################################

        log["best_cost_result"] = load_mcp_best_cost_result(instance=instance, data_list=log["history"])

        ###############################################
        log["cost_result"] = load_mcp_cost_result(instance=instance, data_list=log["history"])

        ###############################################
        log["history_result"] = load_mcp_history_result(instance=instance, data_list=log["history"])
    return instance, log


def load_mcp_best_cost_result(instance, data_list):
    best_cost_result_list = []
    data_df = pd.concat([data[data["Cost"] == instance["BR"]] for data in data_list]).sort_values("ls").reset_index()

    for row_num in range(1, len(data_df) + 1):
        cost_result = data_df[:row_num]

        n = instance["n"]
        ls_max, ls_mean, ls_min = cost_result['ls'].max(), cost_result['ls'].mean(), cost_result['ls'].min()

        tmp = pd.DataFrame([[
            row_num, instance["BR"],
            cost_result['Time'].max(), cost_result['Time'].mean(), cost_result['Time'].min(),
            ls_max, ls_mean, ls_min,
            ls_max / n, ls_mean / n, ls_min / n,
        ]],
            columns=['num', 'Cost',
                     'Max_Time', 'Avg_Time', 'Min_Time',
                     'Max_ls', 'Avg_ls', 'Min_ls',
                     'Max_ls/n', 'Avg_ls/n', 'Min_ls/n',
                     ]
        )
        tmp.fillna(0, inplace=True)
        best_cost_result_list.append(tmp)
    if len(best_cost_result_list) == 0:
        return pd.DataFrame()
    else:
        return pd.concat(best_cost_result_list)


def load_history(instance, path):
    columns = {
        0: 'Cost',
        1: 'Time',
        2: 'ls',
        3: 'add',
        4: 'drop',
        5: 'm_add',
        6: 'kopt',
        7: 'kick',
        8: 'restart',
    }

    data_list = []
    file_path = ""
    try:
        file_path = path + "/" + instance["name"] + "_log_.csv"
        # print("--start--load--" + "/" + str(i) + "/" + str(len(instances)) + "-" + file_path)
        with open(file_path) as f:
            s = f.read()
            rows = csv.reader(io.StringIO(s))
            rows = [row[:len(row) - 1] for row in rows]

            for num in range(0, len(rows), len(columns)):
                df = pd.DataFrame(rows[num:num + len(columns)]).T
                df.rename(columns=columns, inplace=True)
                df["Cost"] = df["Cost"].astype('uint64')
                df['Time'] = df['Time'].astype('float64')
                df['ls'] = df['ls'].astype('uint64')
                df['add'] = df['add'].astype('uint64')
                df['drop'] = df['drop'].astype('uint64')
                df['m_add'] = df['m_add'].astype('uint64')
                df['kopt'] = df['kopt'].astype('uint64')
                df['kick'] = df['kick'].astype('uint64')
                df['restart'] = df['restart'].astype('uint64')
                data_list.append(df)

        # print("--end----load--")
    except FileNotFoundError:
        print("--not----found--" + file_path)
    except Exception as e:
        print("--error---------" + file_path)
        print(e)

    return data_list


def load_mcp_history_result(instance, data_list):
    instance_cost_result_list = []
    cost_set = []
    for data in data_list:
        cost_set.extend(data["Cost"].values)
    cost_set = np.unique(cost_set)
    cost_set = cost_set.astype('uint64')
    cost_set.sort()
    cost_set = cost_set[::-1]
    for i in range(1, len(cost_set) + 1, 1):
        data_df = pd.DataFrame()
        data_df_list = []
        for data in data_list:
            data['ls_diff'] = data['ls'].astype('uint64').diff().fillna(0)
            data['Time_diff'] = data['Time'].astype('float64').diff().fillna(0)
            if i <= len(data):
                data_df_list.append(pd.DataFrame(data.iloc[-i]).T)
        if len(data_df_list) > 0:
            data_df = pd.concat(data_df_list)

        if len(data_df) != 0:
            data_df['ls_diff'] = data_df['ls_diff'].astype('uint64')
            data_df['Time_diff'] = data_df['Time_diff'].astype('float64')

            n = instance["n"]
            ls_max, ls_mean, ls_min = data_df['ls'].max(), data_df['ls'].mean(), data_df['ls'].min()
            ls_diff_max, ls_diff_mean, ls_diff_min = data_df['ls_diff'].max(), data_df['ls_diff'].mean(), data_df['ls_diff'].min()
            add_max, add_mean, add_min = data_df['add'].max(), data_df['add'].mean(), data_df['add'].min()
            drop_max, drop_mean, drop_min = data_df['drop'].max(), data_df['drop'].mean(), data_df['drop'].min()
            m_add_max, m_add_mean, m_add_min = data_df['m_add'].max(), data_df['m_add'].mean(), data_df['m_add'].min()
            kopt_max, kopt_mean, kopt_min = data_df['kopt'].max(), data_df['kopt'].mean(), data_df['kopt'].min()
            kick_max, kick_mean, kick_min = data_df['kick'].max(), data_df['kick'].mean(), data_df['kick'].min()
            restart_max, restart_mean, restart_min = data_df['restart'].max(), data_df['restart'].mean(), data_df['restart'].min()

            add_div_kopt = data_df['add'] / data_df['kopt']
            add_div_kopt_max, add_div_kopt_mean, add_div_kopt_min = add_div_kopt.max(), add_div_kopt.mean(), add_div_kopt.min()

            drop_div_kopt = data_df['drop'] / data_df['kopt']
            drop_div_kopt_max, drop_div_kopt_mean, drop_div_kopt_min = drop_div_kopt.max(), drop_div_kopt.mean(), drop_div_kopt.min()

            kopt_div_ls = data_df['kopt'] / data_df['ls']
            kopt_div_ls_max, kopt_div_ls_mean, kopt_div_ls_min = kopt_div_ls.max(), kopt_div_ls.mean(), kopt_div_ls.min()

            tmp = pd.DataFrame([[
                len(data_df),
                data_df['Cost'].max(), data_df['Cost'].mean(), data_df['Cost'].min(),
                data_df['Time'].max(), data_df['Time'].mean(), data_df['Time'].min(),
                data_df['Time_diff'].max(), data_df['Time_diff'].mean(), data_df['Time_diff'].min(),
                ls_max, ls_mean, ls_min,
                ls_max / n, ls_mean / n, ls_min / n,
                ls_diff_max, ls_diff_mean, ls_diff_min,
                ls_diff_max / n, ls_diff_mean / n, ls_diff_min / n,
                add_max, add_mean, add_min,
                add_div_kopt_max, add_div_kopt_mean, add_div_kopt_min,
                drop_max, drop_mean, drop_min,
                drop_div_kopt_max, drop_div_kopt_mean,drop_div_kopt_min,
                m_add_max, m_add_mean, m_add_min,
                kopt_max, kopt_mean, kopt_min,
                kopt_div_ls_max, kopt_div_ls_mean, kopt_div_ls_min,
                kick_max, kick_mean, kick_min,
                restart_max, restart_mean, restart_min
            ]],
                columns=['trial',
                         'Max_Cost', 'Avg_Cost', 'Min_Cost',
                         'Max_Time', 'Avg_Time', 'Min_Time',
                         'Max_Time_diff', 'Avg_Time_diff', 'Min_Time_diff',
                         'Max_ls', 'Avg_ls', 'Min_ls',
                         'Max_ls/n', 'Avg_ls/n', 'Min_ls/n',
                         'Max_ls_diff', 'Avg_ls_diff', 'Min_ls_diff',
                         'Max_ls_diff/n', 'Avg_ls_diff/n', 'Min_ls_diff/n',
                         'Max_add', 'Avg_add', 'Min_add',
                         'Max_add/kopt', 'Avg_add/kopt', 'Min_add/kopt',
                         'Max_drop', 'Avg_drop', 'Min_drop',
                         'Max_drop/kopt', 'Avg_drop/kopt', 'Min_drop/kopt',
                         'Max_m_add', 'Avg_m_add', 'Min_m_add',
                         'Max_kopt', 'Avg_kopt', 'Min_kopt',
                         'Max_kopt/ls', 'Avg_kopt/ls', 'Min_kopt/ls',
                         'Max_kick', 'Avg_kick', 'Min_kick',
                         'Max_restart', 'Avg_restart', 'Min_restart'
                         ]
            )
            tmp.fillna(0, inplace=True)
            instance_cost_result_list.append(tmp)
    return pd.concat(instance_cost_result_list)


def load_mcp_cost_result(instance, data_list):
    instance_cost_result_list = []
    cost_set = []
    for data in data_list:
        cost_set.extend(data["Cost"].values)
    cost_set = np.unique(cost_set)
    cost_set = cost_set.astype('uint64')
    cost_set.sort()
    cost_set = cost_set[::-1]

    for cost in cost_set:
        data_df = pd.concat([data[data["Cost"] == cost] for data in data_list]).reset_index()
        n = instance["n"]
        ls_max, ls_mean, ls_min = data_df['ls'].max(), data_df['ls'].mean(), data_df['ls'].min()
        add_max, add_mean, add_min = data_df['add'].max(), data_df['add'].mean(), data_df['add'].min()
        drop_max, drop_mean, drop_min = data_df['drop'].max(), data_df['drop'].mean(), data_df['drop'].min()
        m_add_max, m_add_mean, m_add_min = data_df['m_add'].max(), data_df['m_add'].mean(), data_df['m_add'].min()
        kopt_max, kopt_mean, kopt_min = data_df['kopt'].max(), data_df['kopt'].mean(), data_df['kopt'].min()
        kick_max, kick_mean, kick_min = data_df['kick'].max(), data_df['kick'].mean(), data_df['kick'].min()
        restart_max, restart_mean, restart_min = data_df['restart'].max(), data_df['restart'].mean(), data_df['restart'].min()

        add_div_kopt = data_df['add'] / data_df['kopt']
        add_div_kopt_max, add_div_kopt_mean, add_div_kopt_min = add_div_kopt.max(), add_div_kopt.mean(), add_div_kopt.min()

        drop_div_kopt = data_df['drop'] / data_df['kopt']
        drop_div_kopt_max, drop_div_kopt_mean, drop_div_kopt_min = drop_div_kopt.max(), drop_div_kopt.mean(), drop_div_kopt.min()

        kopt_div_ls = data_df['kopt'] / data_df['ls']
        kopt_div_ls_max, kopt_div_ls_mean, kopt_div_ls_min = kopt_div_ls.max(), kopt_div_ls.mean(), kopt_div_ls.min()

        time_div_ls = data_df['Time'] / data_df['ls']
        time_div_ls_max, time_div_ls_mean, time_div_ls_min = time_div_ls.max(), time_div_ls.mean(), time_div_ls.min()

        tmp = pd.DataFrame([[
            len(data_df), cost.astype('uint64'),
            data_df['Time'].max(), data_df['Time'].mean(), data_df['Time'].min(),
            time_div_ls_max, time_div_ls_mean, time_div_ls_min,
            ls_max, ls_mean, ls_min,
            ls_max / n, ls_mean / n, ls_min / n,
            add_max, add_mean, add_min,
            add_div_kopt_max, add_div_kopt_mean, add_div_kopt_min,
            drop_max, drop_mean, drop_min,
            drop_div_kopt_max, drop_div_kopt_mean, drop_div_kopt_min,
            m_add_max, m_add_mean, m_add_min,
            kopt_max, kopt_mean, kopt_min,
            kopt_div_ls_max, kopt_div_ls_mean, kopt_div_ls_min,
            kick_max, kick_mean, kick_min,
            restart_max, restart_mean, restart_min
        ]],
            columns=['trial', 'Cost',
                     'Max_Time', 'Avg_Time', 'Min_Time',
                     'Max_Time/ls', 'Avg_Time/ls', 'Min_Time/ls',
                     'Max_ls', 'Avg_ls', 'Min_ls',
                     'Max_ls/n', 'Avg_ls/n', 'Min_ls/n',
                     'Max_add', 'Avg_add', 'Min_add',
                     'Max_add/kopt', 'Avg_add/kopt', 'Min_add/kopt',
                     'Max_drop', 'Avg_drop', 'Min_drop',
                     'Max_drop/kopt', 'Avg_drop/kopt', 'Min_drop/kopt',
                     'Max_m_add', 'Avg_m_add', 'Min_m_add',
                     'Max_kopt', 'Avg_kopt', 'Min_kopt',
                     'Max_kopt/ls', 'Avg_kopt/ls', 'Min_kopt/ls',
                     'Max_kick', 'Avg_kick', 'Min_kick',
                     'Max_restart', 'Avg_restart', 'Min_restart'
                     ]
        )

        tmp.fillna(0, inplace=True)
        instance_cost_result_list.append(tmp)

    return pd.concat(instance_cost_result_list)


def load_result_clique(instance, path):
    result_clique = []
    file_path = ""
    try:
        file_path = path + "/" + instance["name"] + "_result_clique_.csv"
        # print("--start--load--" + "/" + str(i) + "/" + str(len(instances)) + "-" + file_path)
        with open(file_path) as f:
            lines = csv.reader(f)
            for line in lines:
                tmp = []
                for element in line:
                    if type(element) is str:
                        if element != ' ':
                            tmp.append(int(element.replace(' ', '')))
                    else:
                        tmp.append(element)
                result_clique.append(tmp)
        # print("--end----load--")
    except FileNotFoundError:
        print("--not----found--" + file_path)
    except Exception as e:
        print("--error---------" + file_path)
        print(e)
    return result_clique


def load_cpmp_log(instances, path):
    columns = {
        0: 'Cost',
        1: 'population_best_cost',
        2: 'population_avg_cost',
        3: 'Time',
        4: 'ls',
        5: 'repair',
        6: 'start',
        7: 'selection',
        8: 'crossover',
        9: 'mutation',
        10: 'pmp_ls'}

    data_lists = load_log(instances, path, columns)
    for i in range(len(instances)):
        name = instances["name"][i]
        data_list = data_lists[name]
        for data_df in data_list:
            data_df["Cost"] = data_df["Cost"].astype('float64')
            data_df["population_best_cost"] = data_df["population_best_cost"].astype('float64')
            data_df["population_avg_cost"] = data_df["population_avg_cost"].astype('float64')
            data_df['Time'] = data_df['Time'].astype('float64')
            data_df['ls'] = data_df['ls'].astype('uint64')
            data_df['repair'] = data_df['repair'].astype('uint64')
            data_df['start'] = data_df['start'].astype('uint64')
            data_df['selection'] = data_df['selection'].astype('uint64')
            data_df['crossover'] = data_df['crossover'].astype('uint64')
            data_df['mutation'] = data_df['mutation'].astype('uint64')
            data_df['pmp_ls'] = data_df['pmp_ls'].astype('uint64')

    logs = joblib.Parallel(n_jobs=-1, verbose=10, timeout=None)(
        [joblib.delayed(load_cpmp_instance_log)(instances.iloc[i], data_lists[instances["name"][i]], path)
         for i in range(len(instances))]
    )
    # シーケンシャル
    # logs = [load_instance_log(data_lists[instances["name"][i]], max_count, instances["n"][i], instances["name"][i], path_list) for i in range(len(instances))]

    all_log = dict(
        cost_result={},
        history_result={},
    )
    for log in logs:
        for key in log.keys():
            all_log[key].update(log[key])

    return all_log


def load_cpmp_instance_log(instance, data_list, path):
    cost_result = {}
    history_result = {}
    if len(data_list) != 0:
        cost_set, cost_result[instance["name"]] = load_cpmp_cost_result(instance=instance, data_list=data_list)
        ###############################################
        history_result[instance["name"]] = load_cpmp_history_result(instance=instance, cost_set=cost_set, data_list=data_list)
    log = dict(
        cost_result=cost_result,
        history_result=history_result,
    )
    return log


def load_cpmp_history_result(instance, cost_set, data_list):
    instance_cost_result_list = []
    for i in range(1, len(cost_set) + 1, 1):
        data_df = pd.DataFrame()
        data_df_list = []
        for data in data_list:
            data['ls_diff'] = data['ls'].astype('uint64').diff().fillna(0)
            data['Time_diff'] = data['Time'].astype('float64').diff().fillna(0)
            if i <= len(data):
                data_df_list.append(pd.DataFrame(data.iloc[-i]).T)
        if len(data_df_list) > 0:
            data_df = pd.concat(data_df_list)

        if len(data_df) != 0:
            data_df['Time_diff'] = data_df['Time_diff'].astype('float64')
            data_df['ls_diff'] = data_df['ls_diff'].astype('uint64')
            tmp = pd.DataFrame([[
                len(data_df),
                data_df['Cost'].max(), data_df['Cost'].mean(), data_df['Cost'].min(),
                data_df['population_best_cost'].max(), data_df['population_best_cost'].mean(), data_df['population_best_cost'].min(),
                data_df['population_avg_cost'].max(), data_df['population_avg_cost'].mean(), data_df['population_avg_cost'].min(),
                data_df['Time'].max(), data_df['Time'].mean(), data_df['Time'].min(),
                data_df['Time_diff'].max(), data_df['Time_diff'].mean(), data_df['Time_diff'].min(),
                data_df['ls'].max(), data_df['ls'].mean(), data_df['ls'].min(),
                data_df['ls_diff'].max(), data_df['ls_diff'].mean(), data_df['ls_diff'].min(),
                data_df['repair'].max(), data_df['repair'].mean(), data_df['repair'].min(),
                data_df['start'].max(), data_df['start'].mean(), data_df['start'].min(),
                data_df['selection'].max(), data_df['selection'].mean(), data_df['selection'].min(),
                data_df['crossover'].max(), data_df['crossover'].mean(), data_df['crossover'].min(),
                data_df['mutation'].max(), data_df['mutation'].mean(), data_df['mutation'].min(),
                data_df['pmp_ls'].max(), data_df['pmp_ls'].mean(), data_df['pmp_ls'].min()
            ]],
                columns=['trial',
                         'Max_Cost', 'Avg_Cost', 'Min_Cost',
                         'Max_population_best_cost', 'Avg_population_best_cost', 'Min_population_best_cost',
                         'Max_population_avg_cost', 'Avg_population_avg_cost', 'Min_population_avg_cost',
                         'Max_Time', 'Avg_Time', 'Min_Time',
                         'Max_Time_diff', 'Avg_Time_diff', 'Min_Time_diff',
                         'Max_ls', 'Avg_ls', 'Min_ls',
                         'Max_ls_diff', 'Avg_ls_diff', 'Min_ls_diff',
                         'Max_repair', 'Avg_repair', 'Min_repair',
                         'Max_start', 'Avg_start', 'Min_start',
                         'Max_selection', 'Avg_selection', 'Min_selection',
                         'Max_crossover', 'Avg_crossover', 'Min_crossover',
                         'Max_mutation', 'Avg_mutation', 'Min_mutation',
                         'Max_pmp_ls', 'Avg_pmp_ls', 'Min_pmp_ls',
                         ]
            )
            tmp.fillna(0, inplace=True)
            instance_cost_result_list.append(tmp)
    return pd.concat(instance_cost_result_list)


def load_cpmp_cost_result(instance, data_list):
    instance_cost_result_list = []
    cost_set = []
    for data in data_list:
        cost_set.extend(data["Cost"].values)
    cost_set = np.unique(cost_set)
    cost_set = cost_set.astype('uint64')
    cost_set.sort()
    cost_set = cost_set[::-1]
    for cost in cost_set:
        data_df = pd.concat([data[data["Cost"] == cost] for data in data_list]).reset_index()

        tmp = pd.DataFrame([[
            len(data_df), cost.astype('uint64'),
            data_df['population_best_cost'].max(), data_df['population_best_cost'].mean(),
            data_df['population_best_cost'].min(),
            data_df['population_avg_cost'].max(), data_df['population_avg_cost'].mean(),
            data_df['population_avg_cost'].min(),
            data_df['Time'].max(), data_df['Time'].mean(), data_df['Time'].min(),
            data_df['ls'].max(), data_df['ls'].mean(), data_df['ls'].min(),
            data_df['repair'].max(), data_df['repair'].mean(), data_df['repair'].min(),
            data_df['start'].max(), data_df['start'].mean(), data_df['start'].min(),
            data_df['selection'].max(), data_df['selection'].mean(), data_df['selection'].min(),
            data_df['crossover'].max(), data_df['crossover'].mean(), data_df['crossover'].min(),
            data_df['mutation'].max(), data_df['mutation'].mean(), data_df['mutation'].min(),
            data_df['pmp_ls'].max(), data_df['pmp_ls'].mean(), data_df['pmp_ls'].min()
        ]],
            columns=['trial', 'Cost',
                     'Max_population_best_cost', 'Avg_population_best_cost', 'Min_population_best_cost',
                     'Max_population_avg_cost', 'Avg_population_avg_cost', 'Min_population_avg_cost',
                     'Max_Time', 'Avg_Time', 'Min_Time',
                     'Max_ls', 'Avg_ls', 'Min_ls',
                     'Max_repair', 'Avg_repair', 'Min_repair',
                     'Max_start', 'Avg_start', 'Min_start',
                     'Max_selection', 'Avg_selection', 'Min_selection',
                     'Max_crossover', 'Avg_crossover', 'Min_crossover',
                     'Max_mutation', 'Avg_mutation', 'Min_mutation',
                     'Max_pmp_ls', 'Avg_pmp_ls', 'Min_pmp_ls',
                     ]
        )

        tmp.fillna(0, inplace=True)
        instance_cost_result_list.append(tmp)

    return cost_set, pd.concat(instance_cost_result_list)
