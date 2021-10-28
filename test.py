import pandas as pd
from mylib import *

#df = pd.read_csv('./sample.csv').to_dict('records')



def switch_file(file_name):
    global datas
    datas = pd.read_csv(file_name).to_dict('records')

def test3():
    print(len(datas))


if __name__=='__main__':
    file_name1 = './sample.csv'
    file_name2 = './sample2.csv'

    switch_file(file_name1)
    test3()
    switch_file(file_name2)
    test3()




