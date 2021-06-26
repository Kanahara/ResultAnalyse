import math
import joblib
import pandas as pd
import numpy as np

def result(dataframe, problem, instances, trial_num=100, parallel_key=None):
    results = joblib.Parallel(n_jobs=-1, verbose=10)(
        [joblib.delayed(_result_of_instance_)(dataframe[instance["name"]], problem, instance, trial_num, index) for index, instance in instances.iterrows()]
    )
    results.sort(key=lambda x: x[0])
    return parallel_key, pd.concat([r for index, r in results])


def _result_of_instance_(dataframe, problem, instance, trial_num=100, parallel_key=None):
    info = None
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

    if dataframe.empty:
        return parallel_key, pd.DataFrame([[
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
        dataframe = dataframe[0:trial_num]

        # 試行回数
        trial = len(dataframe)

        # 全試行ベストコスト
        best_cost = dataframe["最良解値"].max()

        # ベストコスト算出回数
        best_cost_count = (dataframe["最良解値"] == best_cost).sum()

        # 平均コスト
        cost_mean = dataframe["最良解値"].mean()

        # 全試行ワーストコスト
        worst_cost = dataframe["最良解値"].min()

        # ワーストコスト算出回数
        worst_cost_count = (dataframe["最良解値"] == worst_cost).sum()

        # 最大化問題,最小化問題切り替え
        if problem["type"] == "minimization":
            best_cost, worst_cost = worst_cost, best_cost
            best_cost_count, worst_cost_count = worst_cost_count, best_cost_count

        # ベストコスト算出CPU時間平均
        best_cost_cpu_time_mean = dataframe[(dataframe["最良解値"] == best_cost)]['最良解算出時間'].mean()

        # ベストコスト算出CPU時間標準偏差
        best_cost_cpu_time_std = dataframe[dataframe["最良解値"] == best_cost]["最良解算出時間"].std()
        if math.isnan(best_cost_cpu_time_std):
            best_cost_cpu_time_std = 0

        # 最了解値の標準偏差
        cost_std = dataframe["最良解値"].std()
        if math.isnan(cost_std):
            cost_std = 0

        # 最了解値算出CPU時間
        cost_cpu_time_mean = dataframe["探索時間"].mean()

        # コスト表示のパーセント化
        if problem["cost_style"] == "percent":
            best_cost = (best_cost - instance["BR"]) / instance["BR"]
            cost_mean = (cost_mean - instance["BR"]) / instance["BR"]
            worst_cost = (worst_cost - instance["BR"]) / instance["BR"]
            cost_std = ((dataframe["最良解値"] - instance["BR"]) / instance["BR"]).std()

        return parallel_key, pd.DataFrame([[
            instance["name"], instance["BR"], instance["n"], info,
            best_cost, "(", best_cost_count, "/", trial, ")",
            cost_mean, "(", cost_std, ")",
            worst_cost, "(", worst_cost_count, "/", trial, ")",
            best_cost_cpu_time_mean, "(", best_cost_cpu_time_std, ")",
            cost_cpu_time_mean
        ]],
            columns=en_columns
        )
