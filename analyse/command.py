import utility

# 実行ファイルのコピーコマンド
def copy_exe_file_command(algorithm, server_workspace_path):
    command = "rm -r " + server_workspace_path + "/" + algorithm.name() + "; "
    command += "mkdir -p " + server_workspace_path + "/" + algorithm.name() + "; "
    command += "cp " + algorithm.file_path() + " " + server_workspace_path + "/" + algorithm.name() + "/; "
    return command

# 実行コマンドリスト作成
def make_exec_commands(command_function, problem, instances, algorithm, server_workspace_path, seed):
    commands = []
    for index, instance in instances.iterrows():
        if instance["easy"]:
            commands.append(
                command_function(problem=problem, instance=instance, algorithm=algorithm,
                                 server_workspace_path=server_workspace_path, seed=seed,
                                 trial_num=algorithm.parameter()["trial_num"])
            )
        else:
            for t in range(algorithm.parameter()["trial_num"]):
                commands.append(
                    command_function(problem=problem, instance=instance, algorithm=algorithm,
                                     server_workspace_path=server_workspace_path, seed=seed + t, trial_num=1)
                )
    return commands

# def makeExecCommandTest(problem, instance, algorithm, server_workspace_path, seed, trial_num):
#     command = ""
#     exe_path = server_workspace_path + "/" + algorithm.name()
#     save_path = exe_path + "/tmp/" + randomString(16) + "/"
#     config_path = "/mnt/share/data/config/" + problem["name"] + ".cfg"
#     instance_path = problem["instances_dir_path"] + "/" + instance["name"] + problem["extension"]
#     command = "bash -c \""
#     command += "mkdir " + exe_path + "/tmp ; "
#     command += "mkdir " + save_path + " ; "
#     command += exe_path + "/" + algorithm.file() + \
#                " " + instance_path + \
#                " " + save_path + \
#                " " + str(instance["BR"] - 1) + " ; "
#     command += "cp -r " + save_path + " " + algorithm.workspace_path() + "/tmp/ ; "
#     command += "\""
#     return command

# 実行コマンド作成

def make_exec_command(problem, instance, algorithm, server_workspace_path, seed, trial_num):
    exe_path = server_workspace_path + "/" + algorithm.name()
    save_path = exe_path + "/tmp/" + utility.random_string(16) + "/"
    config_path = "/mnt/share/data/config/" + problem["name"] + ".cfg"
    instance_path = problem["instances_dir_path"] + "/" + instance["name"] + problem["extension"]

    repeat_times = "0"
    if type(algorithm.parameter()["repeat_times"]) is int:
        repeat_times = str(algorithm.parameter()["repeat_times"])
    elif "n" in algorithm.parameter()["repeat_times"]:
        repeat_times = str(instance["n"] * int(algorithm.parameter()["repeat_times"].replace("n", "")))

    run_time = "0"
    if type(algorithm.parameter()["run_time"]) is int:
        run_time = str(algorithm.parameter()["run_time"])
    elif "n" in algorithm.parameter()["run_time"]:
        run_time = str(instance["n"] * int(algorithm.parameter()["run_time"].replace("n", "")))

    command = "bash -c \""
    command += "mkdir " + exe_path + "/tmp ; "
    command += "mkdir " + save_path + " ; "
    command += exe_path + "/" + algorithm.file() + \
               " -f " + instance_path + \
               " -b " + str(instance["BR"]) + \
               " -seed " + str(seed) + \
               " -t " + str(trial_num) + \
               " -r " + repeat_times + \
               " -s " + run_time + \
               " -p " + str(algorithm.parameter()["pop_size"]) + \
               " -type " + instance["type"] + \
               " -results_dir_path " + save_path + \
               " -log_dir_path " + save_path + \
               " -config_path " + config_path + " ; "
    command += "cp -r " + save_path + " " + algorithm.workspace_path() + "/tmp/ ; "
    command += "\""
    return command