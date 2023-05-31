import pandas as pd

users = pd.read_csv("users.csv", index_col=0)
# print(users.loc[(users['user_id'] == 961544061), 'token_capacity'][0])
if users.loc[(users['user_id'] == 961544061), 'token_capacity'][0] > 0:
    print("kek")