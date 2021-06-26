import pandas as pd
import numpy as np
from algorithm import Algorithm
from utility import load_algorithm_results, make_algorithm_workbook


def main():
    problems = pd.read_csv("./setting/problem.csv")
    problem = problems[problems["name"] == "tsp"].iloc[0]
    instances = pd.read_csv("./setting/instance/" + problem["name"] + "/" + problem["name"] + ".csv")
    # instances = pd.read_csv("setting/instance/random/random.csv")
    algorithms = []
    # algorithms.append(Algorithm(name="alg1", path="/mnt/share/algorithm/" + problem["name"], parameter=""))

    print("----Start-Load-Result----")
    load_algorithm_results(algorithms, instances, dtype={"最良解値": np.float64, "最良解算出時間": np.float64, "探索時間": np.float64})
    # load_algorithm_results(algorithms, instances, dtype={"最良解値": np.float64, "探索時間": np.float64, "最良解算出時間": np.float64})
    print("----End--Load-Result----")

    print("----Start-Make--Workbook---")
    make_algorithm_workbook(algorithms, instances, problem)
    print("----End---Make--Workbook---")




if __name__ == '__main__':
    main()