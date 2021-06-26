import pandas as pd
import numpy as np
import plotly.graph_objects as go
from algorithm import Algorithm
from utility import load_algorithm_results


if __name__ == '__main__':
    problems = pd.read_csv("./setting/problem.csv")
    problem = problems[problems["name"] == "gcp"].iloc[0]
    instances = pd.read_csv("setting/instance/random/random.csv")
    sizes = np.arange(100, 1000, 100).tolist() + np.arange(1000, 5000, 1000).tolist() + np.arange(5000, 20001, 5000).tolist()
    densities = np.arange(5, 100, 5) / 100
    instances = pd.merge_asof(instances.sort_values("r"), pd.DataFrame({"density": densities}), left_on='r', right_on='density', direction='nearest')
    algorithms = []
    # algorithms.append(Algorithm(name="rlf_int16_if", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(Algorithm(name="rlf_int32", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(Algorithm(name="rlf_A_B_int16_if", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(Algorithm(name="rlf_A_B_int32", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    algorithms.append(Algorithm(name="rlf_original", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    algorithms.append(Algorithm(name="rlf_A", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    algorithms.append(Algorithm(name="rlf_B", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    algorithms.append(Algorithm(name="rlf_C", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    algorithms.append(Algorithm(name="rlf_AB", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    algorithms.append(Algorithm(name="rlf_AC", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    algorithms.append(Algorithm(name="rlf_BC", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    algorithms.append(Algorithm(name="rlf_ABC", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    algorithms.append(Algorithm(name="rlf_2ABC", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(Algorithm(name="rlf_A_", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(Algorithm(name="rlf_B_", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(Algorithm(name="rlf_C_", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(Algorithm(name="rlf_AB_", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(Algorithm(name="rlf_AC_", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(Algorithm(name="rlf_BC_", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(Algorithm(name="rlf_ABC_", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(Algorithm(name="rlf_2ABC_", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(
    #     Algorithm(name="Tabucol-LMIN_0-LMAX_9-ARATE_6_norm", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(
    #     Algorithm(name="Tabucol-LMIN_0-LMAX_9-ARATE_6", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(
    #     Algorithm(name="Tabucol-LMIN_0-LMAX_9-ARATE_6_A", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(
    #     Algorithm(name="Tabucol-LMIN_0-LMAX_9-ARATE_6_B", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(
    #     Algorithm(name="Tabucol-LMIN_0-LMAX_9-ARATE_6_C", path="/mnt/share/algorithm/" + problem["name"], parameter=""))

    # algorithms.append(Algorithm(name="rlf_4ABC_", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(Algorithm(name="rlf_6ABC_", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(Algorithm(name="rlf_6ABC_test", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    # algorithms.append(Algorithm(name="rlf_8ABC_", path="/mnt/share/algorithm/" + problem["name"], parameter=""))
    print("----Start-Load-Result----")
    load_algorithm_results(algorithms, instances, dtype={"最良解値": np.float64, "最良解算出時間": np.float64, "探索時間": np.float64})
    print("----End--Load-Result----")


    df_dict = {}
    for algorithm in algorithms:
        df = pd.DataFrame()
        result = algorithm.result()
        for size in sizes:
            for density in densities:
                times = [result[instance["name"]]["探索時間"].mean() for index, instance in instances[(instances["n"] == size) & (instances["density"] == density)].iterrows()]
                df = df.append({"size": size, "density": density, "time": np.mean(times)}, ignore_index=True)
        df_dict[algorithm.name()] = df

    fig = go.Figure()
    for name in df_dict.keys():
        df = df_dict[name]
        for size in sizes:
            size_df = df[df["size"] == size]
            fig.add_trace(
                go.Scatter(name=name, x=size_df["density"], y=size_df["time"])
            )


    steps = []
    for index, size in enumerate(sizes):
        step = dict(
            method="update",
            label=str(size),
            args=[{"visible": [False] * len(fig.data)},
                  {"title": "RLF: size=" + str(size)},
                  ],  # layout attribute
        )
        for al in range(len(df_dict.keys())):
            step["args"][0]["visible"][index + len(sizes) * (al)] = True
        steps.append(step)
        # print(step)
    sliders = [dict(
        active=0,
        currentvalue={"prefix": "Size: "},
        pad={"t": 100},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders
    )

    fig.write_html("./output/size.html")
