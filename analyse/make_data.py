import numpy as np
import pandas as pd
import math
import csv
import io
import joblib



def make_result_by_history(problem, instances, algorithm, parallel_num, ls_num, trial_num=100):
    data = None
    result_list = joblib.Parallel(n_jobs=-1, verbose=10)(
        [joblib.delayed(make_result_instance_by_history)(problem, instances.iloc[instance_num], algorithm, ls_num, trial_num) for instance_num in range(len(instances))]
    )
    # シーケンシャル
    # result_list = [make_result(data, problem, instances.iloc[instance_num], path, trial_num) for instance_num in range(len(instances))]

    result = pd.DataFrame()
    if len(result_list) > 0:
        result = pd.concat(result_list)
    return parallel_num, result


def make_result_instance_by_history(problem, instance, algorithm, ls_num, trial_num):
    log = algorithm.log()[instance["name"]]
    data = pd.DataFrame(columns=['最良解値', '最良解算出時間', "探索時間"])
    if "history" in log.keys():
        histories = log["history"]
        # data = pd.concat([history[history["ls"] <= ls_num * instance["n"]][["Cost", "Time", "Time"]].tail(1) for history in histories])
        data = pd.concat([history[history["ls"] <= ls_num][["Cost", "Time", "Time"]].tail(1) for history in histories])
        data.columns = ['最良解値', '最良解算出時間', "探索時間"]
    return make_result_instance(data, problem, instance, "history-" + algorithm.name(), trial_num)


def make_result_instance(data, problem, instance, path, trial_num):
    info = 0
    info_name = ""
    if problem["name"] == "mcp":
        # 辺密度ロー
        info = instance["r"]
        info_name = "ρ"
    elif problem["name"] == "mwcp":
        # 辺密度ロー
        info = instance["r"]
        info_name = "ρ"
    elif problem["name"] == "gcp":
        # 辺密度ロー
        info = instance["r"]
        info_name = "ρ"
    elif problem["name"] == "cpmp":
        # 解説施設数ピー
        info = instance["p"]
        info_name = "p"
    en_columns = ["name", "BR", "n", info_name,
                  "Best", "", "#B", "", "", "",
                  "Avg", "", "s.dev", "",
                  "Worst", "", "#W", "", "", "",
                  "Time(s)", "", "s.dev", "",
                  "SearchCPUTimeAvg(s)",
                  ]

    if data.empty:
        print(path + "/" + instance["name"] + ".csv")
        return pd.DataFrame([[
            instance["name"], instance["BR"], instance["n"], info,
            np.nan, "(", np.nan, "/", np.nan, ")",
            np.nan, "(", np.nan, ")",
            np.nan, "(", np.nan, "/", np.nan, ")",
            np.nan, "(", np.nan, ")",
            np.nan
        ]],
            columns=en_columns
        )

    else:
        # 試行回数分抽出
        data = data[0:trial_num]

        # 試行回数
        trial = len(data)

        # 全試行ベストコスト
        best_cost = data["最良解値"].max()

        # ベストコスト算出回数
        best_cost_count = (data["最良解値"] == best_cost).sum()

        # 平均コスト
        cost_mean = data["最良解値"].mean()

        # 全試行ワーストコスト
        worst_cost = data["最良解値"].min()

        # ワーストコスト算出回数
        worst_cost_count = (data["最良解値"] == worst_cost).sum()

        # 最大化問題,最小化問題切り替え
        if problem["type"] == "Minimization":
            best_cost, worst_cost = worst_cost, best_cost
            best_cost_count, worst_cost_count = worst_cost_count, best_cost_count

        # ベストコスト算出CPU時間平均
        best_cost_cpu_time_mean = data[(data["最良解値"] == best_cost)]['最良解算出時間'].mean()

        # ベストコスト算出CPU時間標準偏差
        best_cost_cpu_time_std = data[data["最良解値"] == best_cost]["最良解算出時間"].std()
        if math.isnan(best_cost_cpu_time_std):
            best_cost_cpu_time_std = 0

        # 最了解値の標準偏差
        cost_std = data["最良解値"].std()
        if math.isnan(cost_std):
            cost_std = 0

        # 最了解値算出CPU時間
        cost_cpu_time_mean = data["探索時間"].mean()

        # コスト表示のパーセント化
        if problem["cost_per"]:
            best_cost = (best_cost - instance["BR"]) / instance["BR"]
            cost_mean = (cost_mean - instance["BR"]) / instance["BR"]
            worst_cost = (worst_cost - instance["BR"]) / instance["BR"]
            cost_std = ((data["最良解値"] - instance["BR"]) / instance["BR"]).std()

        return pd.DataFrame([[
            instance["name"], instance["BR"], instance["n"], info,
            best_cost, "(", best_cost_count, "/", trial, ")",
            cost_mean, "(", cost_std, ")",
            worst_cost, "(", worst_cost_count, "/", trial, ")",
            best_cost_cpu_time_mean, "(", best_cost_cpu_time_std, ")",
            cost_cpu_time_mean
        ]],
            columns=en_columns
        )
