import pandas as pd

users = pd.read_csv("text.csv", index_col=0)
users.loc[12232343] = [234]
# if users.loc[(users['user_id'] == 961544061), 'token_capacity'][0] > 0:
#     print("kek")

users.to_csv("text.csv")