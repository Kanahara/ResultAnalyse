import joblib


def __make_result__(filename, path_dict, workspace_path):
    output_filepath = workspace_path + "/result/" + filename
    try:
        with open(output_filepath, mode="w") as outfile:
            read_data = joblib.Parallel(n_jobs=-1, verbose=10)(
                [joblib.delayed(__read_result__)(dirname + "/" + filename) for dirname in path_dict[filename]]
            )
            outfile.write("".join(read_data))
    except Exception as e:
        print("--error---------" + output_filepath)
        print(e)


def __read_result__(filepath):
    try:
        with open(filepath) as infile:
            return infile.read()
    except Exception as e:
        print("--error---------" + filepath)
        print(e)
        return ""