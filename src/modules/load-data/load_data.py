import pandas as pd

class DataProcess:
    def load_data(self, file_path):
        df = pd.read_csv(file_path)
        return df
    
if __name__ == "__main__":
    df = DataProcess().load_data("data/course_raw.csv")
    print(df.head())
