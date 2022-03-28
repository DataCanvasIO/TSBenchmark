class Report():
    def __init__(self):
        self.error_count = 0
        self.error_list = []
        self.success_count = 0

    def get_count_msg(self):
        count_msg = 'success count : {}, error count: {}  error list: \n {}'.format(self.success_count, self.error_count,
                                                                                  self.error_list)
        return count_msg
