import os
import pickle


class Config:
    def __init__(self):
        self.file = r'data/configs.pkl'
        self.production_dir = '/'
        self.loss_dir = '/'
        self.target_dir = '/'
        self.tst = "test"

    def read(self):
        try:
            with open(self.file, 'rb') as f:
                self.production_dir, self.loss_dir, self.target_dir = pickle.load(f)
        except:
            print('no configuration file found')

    def write(self):
        with open(self.file, 'wb') as f:
            pickle.dump([self.production_dir, self.loss_dir, self.target_dir], f)

    def set_production_dir(self, text):
        self.production_dir = self.get_directory(text)
        print(self.production_dir)

    def set_loss_dir(self, text):
        self.loss_dir = self.get_directory(text)
        print(self.loss_dir)

    def set_target_dir(self, text):
        self.target_dir = text
        print(self.target_dir)

    @staticmethod
    def get_directory(text):
        paths = text.split('\n')
        if not os.path.exists(paths[0]):
            return '/'
        return os.path.split(paths[0])[0]
