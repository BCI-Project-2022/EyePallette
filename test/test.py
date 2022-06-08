import datetime
import os
from time import sleep

#@app.route('/') : Front_end 쪽에서 호출 
def main():
    all_lines=[] # line 읽어 넣을 배열, 최종적으로 이중 배열이 된다. 
    d = datetime.datetime.now()
    year = str(d.year)
    month = '0'+str(d.month)
    day = '0'+str(d.day)
    noonOrnight = '오전' if d.hour<=12 else '오후'
    hour = str(d.hour) if d.hour<=12 else str(d.hour-12)
    minute = '0'+str(d.minute) if d.minute<=9 else str(d.minute) # 1~9분사이 폴더가 01, 02 분식으로 만들어짐 
    k = year + '-' + month + '-' + day + '_' + noonOrnight+' '+ hour + '_' + minute
    filePath=os.path.join('C:\MAVE_RawData', k, 'FP1_FFT.txt')
    with open(filePath, "r") as f:
        f.seek(0)
        while True:
            where = f.tell()
            line = f.readline().strip()
            if not line:
                sleep(0.1)
                delay_time += 0.1
                f.seek(where)
                if delay_time > 10.0:  # 10초 이상 지연되면 파일 출력이 끝난 것으로 간주
                    break
            else:
                delay_time = 0. # reset delay time
                temp = line.split('\t')
                all_lines.append((temp))

#@app.route('/mid_average') Front_end 쪽에서 60초 후 호출 

# 3841 : 코드짠 사람 컴퓨터의 엑셀 열이 3841 까지있었으며, 컴퓨터에 따라 더 늘어날 수 잇으나 13,19,23 hz등의 상대적으로 저주파 성분을 
#인덱싱 하기 때문에 길이는 상관없음.
def mid_request():
    sum_13hz=0.00000000000000000000000
    sum_19hz=0.00000000000000000000000
    sum_23hz=0.00000000000000000000000

    avg_13hz=0.00000000000000000000000
    avg_19hz=0.00000000000000000000000
    avg_23hz=0.00000000000000000000000


    for i in range(3841):
        if all_lines[0][i] == '13.00Hz':   #첫 행의 열의 인덱스를 구한다. 첫 행에는 hz 성분이 저장된다. 
            idx_13hz = i
        if all_lines[0][i] == '19.00Hz':
            idx_19hz = i
        if all_lines[0][i] == '23.00Hz':
            idx_23hz = i
            break
    # 27~40 라인이 중립평균을 구하는 라인 이므로 28~40 라인을 돌며 sum을 구하고 Average를 계산한다. 
    for i in range(27,40):
        sum_13hz += float(all_lines[i][idx_13hz])
        sum_19hz += float(all_lines[i][idx_19hz])
        sum_23hz += float(all_lines[i][idx_23hz])
    
    avg_13hz = sum_13hz / 14.0000000000000000000000
    avg_19hz = sum_19hz / 14.0000000000000000000000
    avg_23hz = sum_23hz / 14.0000000000000000000000
    # print(avg_13hz, avg_19hz, avg_23hz)

    return {"result" : {
        # '13hz 중립' : avg_13hz,
        # '19hz 중립' : avg_19hz,
        # '23hz 중립' : avg_23hz,
        '13hz idx' : idx_13hz, 
        '19hz idx' : idx_19hz, 
        '23hz idx' : idx_23hz, 
    }}

main()
