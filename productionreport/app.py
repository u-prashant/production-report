from config import Config
from gui import GUI


def main():
    config = Config()
    config.read()
    GUI(config)


if __name__ == '__main__':
    main()
