import os


class file_util:
    @staticmethod
    def get_dir_path(dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return dir_path

    @staticmethod
    def get_filelist(dir, filelist):
        if os.path.isfile(dir):

            filelist.append(dir)

        elif os.path.isdir(dir):

            for s in os.listdir(dir):
                newDir = os.path.join(dir, s)

                file_util.get_filelist(newDir, filelist)

        return filelist


class dict_util:
    @staticmethod
    def sub_dict(somedict, somekeys, default=None):
        return dict([(k, somedict.get(k, default)) for k in somekeys])
