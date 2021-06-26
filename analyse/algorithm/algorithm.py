import glob
import os
import shutil
import joblib

from algorithm.__utility__ import __make_result__


class Algorithm:
    def __init__(self, name, path, parameter):
        self.__name = name
        self.__path = path
        self.__parameter = parameter
        self.__extension = ".out"
        self.__result = None
        self.__result_dataframe = None
        self.__log = None

    def name(self):
        return self.__name

    def path(self):
        return self.__path

    def file(self):
        return self.name() + self.__extension

    def file_path(self):
        return self.workspace_path() + "/" + self.file()

    def workspace_path(self):
        return self.path() + "/" + self.name()

    def result_path(self):
        return self.path() + "/" + self.name() + "/result"

    def log_path(self):
        return self.path() + "/" + self.name() + "/log"

    def pickle_path(self):
        return self.path() + "/" + self.name() + "/pickle"

    def pickle_file_path(self):
        return self.pickle_path() + "/" + self.name() + ".pickle"

    def parameter(self):
        return self.__parameter

    def set_result(self, result):
        self.__result = result

    def result(self):
        return self.__result

    def set_result_dataframe(self, dataframe):
        self.__result_dataframe = dataframe

    def result_dataframe(self):
        return self.__result_dataframe

    def set_log(self, log):
        self.__log = log

    def log(self):
        return self.__log

    def exists_pickle(self):
        return os.path.exists(self.pickle_file_path())

    # 結果ディレクトリ 一時ファイルディレクトリを作成
    def make_directory(self):
        os.makedirs(self.workspace_path(), exist_ok=True)
        os.chmod(self.workspace_path(), 0o777)
        os.makedirs(self.workspace_path() + "/result", exist_ok=True)
        os.chmod(self.workspace_path() + "/result", 0o777)
        os.makedirs(self.workspace_path() + "/tmp", exist_ok=True)
        os.chmod(self.workspace_path() + "/tmp", 0o777)
        os.makedirs(self.workspace_path() + "/pickle", exist_ok=True)
        os.chmod(self.workspace_path() + "/pickle", 0o777)
        try:
            shutil.move(self.path() + "/" + self.file(), self.workspace_path())
        except Exception as e:
            print(e)

    # 一時ファイルから結果ファイルを作成
    def make_result(self):
        path_dict = {}
        path_list = glob.glob(self.workspace_path() + "/tmp/**", recursive=True)
        for path in path_list:
            if os.path.isfile(path):
                dirname, filename = os.path.split(path)
                if filename not in path_dict.keys():
                    path_dict[filename] = []
                path_dict[filename].append(dirname)
        joblib.Parallel(n_jobs=-1, verbose=10)(
            [joblib.delayed(__make_result__)(filename, path_dict, self.workspace_path()) for filename in path_dict.keys()]
        )

