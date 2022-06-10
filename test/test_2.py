import datetime
import os
from time import sleep

cnt = 13

def main():
    d = datetime.datetime.now()
    d_m = d.minute
    d_s = d.second
    d_m_first = d_m*60 + d_s
    global cnt
    req_0_cnt = cnt
    print(d_m_first)
    while(True):
        d_2 = datetime.datetime.now()
        d_m_now = d_2.minute*60 + d_2.second
        req_0_cnt +=1
        if(d_m_now - d_m_first > 5):
            break

    print(d_m_now)
    print(req_0_cnt)

main()






