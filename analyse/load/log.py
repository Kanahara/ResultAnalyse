import joblib


def log(problem, instances, path, parallel_num):
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