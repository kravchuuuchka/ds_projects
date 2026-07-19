class Research:
    def file_reader(self) -> str:
        return open("../../datasets/data.csv").read()


if __name__ == '__main__':
    print(Research().file_reader())