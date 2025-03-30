import pandas as pd
import glob
import pickle

if __name__ == "__main__":
    all_dfs = []

    elo_result_files = glob.glob("elo_results_*.pkl")
    elo_result_files.sort(key=lambda x: int(x[12:-4]))

    leaderboard_table_files = glob.glob("leaderboard_table_*.csv")
    leaderboard_table_files.sort(key=lambda x: int(x[18:-4]))
    latest_model_info = pd.read_csv(leaderboard_table_files[-1])[["key","Model","License","Organization"]]
    hard_coded_info = pd.read_csv("key_to_model.csv")

    model_info = pd.concat([latest_model_info, hard_coded_info], ignore_index=True)
    
    for elo_result_file in elo_result_files:
        date = elo_result_file[-12:-4]
        print(date)
        
        with open(elo_result_file, "rb") as fin:
            elo_results = pickle.load(fin)
        if "text" in elo_results:
            elo_results_text = elo_results["text"]
            elo_results_vision = elo_results["vision"]
        else:
            elo_results_text = elo_results
            elo_results_vision = None

        #first two elo results files are formatted differently
        if "elo_rating_online" in elo_results:
            elo_df = pd.DataFrame(elo_results["elo_rating_online"].items(), columns=["key","rating"])
        else:
            elo_df = elo_results_text["full"]["leaderboard_table_df"]
            elo_df = elo_df.reset_index(names=['key'])

        #model_table_df = pd.read_csv(leaderboard_table_file)

        # print(model_table_df)

        output_df = pd.merge(elo_df, model_info, on='key', how='left')[["key","Model","rating","License","Organization"]]
        output_df["date"] = date

        all_dfs.append(output_df)
        
    alltime_results = pd.concat(all_dfs, ignore_index=True)
    alltime_results.to_csv("/tmp/alltime.csv", ignore_index=True)

    
