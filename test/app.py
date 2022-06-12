from flask import Flask
from flask_cors import CORS
import datetime
import os
from time import sleep

app = Flask(__name__)
CORS(app, resources={r'*': {'origins': '*'}})

idx_map = [] # Fp1_fft.txt의 첫 라인을 저장하는 리스트이다. 파이썬 내장함수 .index를 통해 관심영역(13,19,22hz)을 찾고, 아래 변수들에 저장한다. 

idx_13hz = 0 # 13hz 의 인덱스를 얻어올 변수
medium_arr_13hz = [] # 13hz대역의 amplitude를 읽어올 리스트이며, 관심대역에서 오차범위 0.4~0.6hz가 +-된 amplitude까지 들어간다(열 +-2)

idx_19hz = 0 # 19hz 의 인덱스를 얻어올 변수
medium_arr_19hz = [] #  19hz대역의 amplitude를 읽어올 리스트이며, 관심대역에서 오차범위 0.4~0.6hz가 +-된 amplitude까지 들어간다(열 +-2)

idx_22hz = 0 # 22hz 의 인덱스를 얻어올 변수
medium_arr_22hz = [] #  22hz대역의 amplitude를 읽어올 리스트이며, 관심대역에서 오차범위 0.4~0.6hz가 +-된 amplitude까지 들어간다(열 +-2)
time_stamp = [] 
# 일반적인 줄이 읽히는 시점이라면 0을 추가
# 중립평균 요청을 하면 -1 추가
# 첫번째 영역 요청을 하면 1추가,
# 두번째 영역 요청을 하면 2추가
# 세번째 영역 요청을 하면 3추가
# 이러한 구별자로 어느라인부터 어느라인까지 읽을 지 정한다. 

m_avg_13hz = 0.00000000000000000000000 #13hz의 중립평균 초기화
m_avg_19hz = 0.00000000000000000000000 #19hz의 중립평균 초기화
m_avg_22hz = 0.00000000000000000000000 #22hz의 중립평균 초기화

# flag 값 들 : req_1, 2, 3 에서 리턴되어 값이 지정되며 red인지, green인지, blue 인지 알려주는 지정자이다. 
flag_1=''  
flag_2='' 
flag_3='' 

@app.route('/')
def main():
    global idx_13hz
    global idx_19hz
    global idx_22hz

    # MAVE 녹화 시작 -> app.py와 동시에 실시간 라이브로 한줄씩 추가
    d = datetime.datetime.now()
    year = str(d.year)
    month = '0' + str(d.month)
    day = str(d.day)
    noonOrnight = '오전' if d.hour <= 12 else '오후'
    hour = str(d.hour) if d.hour <= 12 else str(d.hour - 12)
    minute = '0' + str(d.minute) if d.minute <= 9 else str(d.minute)  # 1~9분사이 폴더가 01, 02 분식으로 만들어짐
    k = year + '-' + month + '-' + day + '_' + noonOrnight + ' ' + hour + '_' + minute
    

    filePath = os.path.join('C:\MAVE_RawData', k, 'FP1_FFT.txt')
    with open(filePath, "r") as f:
        f.seek(0)
        while True:
            where = f.tell()
            line = f.readline().strip()
            if not line:
                sleep(0.1)
                delay_time += 0.1
                f.seek(where)
                if delay_time > 10.0: # 라인추가가 10초이상 되지 않으면 함수를 종료한다. while(True)문을 나가면 함수는 끝까지 실행된 후 종료된다. 
                    break
            else:
                delay_time = 0.  # 라인이 읽힐 경우 delay time은 리셋된다. 
                # sleep(1)
                temp = line.split('\t')
                if len(idx_map) == 0: # 첫 라인일시, idx_map에 라인을 저장. 
                    idx_map.append(temp[1:]) # temp[0]에는 시간이 저장되므로, temp[1]부터 읽어 append 한다. 
                    idx_13hz = idx_map[0].index('13.00Hz')
                    idx_19hz = idx_map[0].index('19.00Hz')
                    idx_22hz = idx_map[0].index('22.00Hz')
                    print('idx_13hz',idx_13hz, 'idx_19hz', idx_19hz, 'idx_22hz',idx_22hz)
                else : # 두번째 줄 이후부터는, all_lines가 아닌 각각의 중립평균을 위한 이차원 배열에 저장된다. &저장 시점부터 엑셀과 동일한 자료형으로 저장
                    idx_temp = temp[1:] #time columne 삭제 
                    medium_arr_13hz.append([float(idx_temp[idx_13hz-2]),float(idx_temp[idx_13hz-1]), float(idx_temp[idx_13hz]), float(idx_temp[idx_13hz+1]), float(idx_temp[idx_13hz+2])])
                    medium_arr_19hz.append([float(idx_temp[idx_19hz-2]),float(idx_temp[idx_19hz-1]), float(idx_temp[idx_19hz]), float(idx_temp[idx_19hz+1]), float(idx_temp[idx_19hz+2])])
                    medium_arr_22hz.append([float(idx_temp[idx_22hz-2]),float(idx_temp[idx_22hz-1]), float(idx_temp[idx_22hz]), float(idx_temp[idx_22hz+1]), float(idx_temp[idx_22hz+2])])
                    time_stamp.append(0) #한줄 추가될 때마다 배열에 0을 추가한다. 이는 어떤 라인을 읽어야 할 지에 대한 안내변수가 된다. 
                    
# 40초에 호출되어 40~60초, 20초간 중립 평균을 구하는 라우팅 함수
@app.route('/mid_average')
def mid_request_0():
    print('중립평균 요청 옴')
    time_stamp.append(-1) #요청이 들어오면 time_stamp 리스트에 -1을 추가.
    start = time_stamp.index(-1) #추가하는 동시에 time_stamp에서 -1의 index를 추가(Start가 인덱스인 라인부터 읽기 시작한다. )
    print('start', start, type(start))
    sleep(20) # 20초간 sleep하고, 그 동안 main 함수는 돌아가며 라인이 추가되고 있다. 
    end = len(medium_arr_13hz)-1 # medium_arr_1hz의 len은 현재까지 읽힌 라인수와 같다. 

    # 13hz,19hz,22hz대역을 모두 더해 저장할 변수이다. 나눠서 avg_13hz, avg_19hz, avg_22hz에 저장된다. 
    sum_13hz = 0.0000000000000
    sum_19hz = 0.0000000000000
    sum_22hz = 0.0000000000000
    
    # start부터 end-1 라인까지 읽고, 열인덱스+-2 까지 더한다. y가 행, x가 열을 뜻한다. 
    for y in range(start, end): #세로로 쌓이는 한줄에 대한 루프 기준점
        for x in range(0,5): 
            sum_13hz += medium_arr_13hz[y][x]
            sum_19hz += medium_arr_19hz[y][x]
            sum_22hz += medium_arr_22hz[y][x]
    

    #temp는 더한 컴포넌트의 수이며, float로 형변환 해서 나눠준다. 
    temp = float((end-start) * 5)
    #전역변수 m_avg_13hz 를 수정해주어야 하므로 global 변수로 선언해준다. 
    global m_avg_13hz 
    m_avg_13hz = sum_13hz / (temp)
    global m_avg_19hz
    m_avg_19hz = sum_19hz / (temp)
    global m_avg_22hz
    m_avg_22hz = sum_22hz / (temp)


    return {"result": {
        '13Hz 중립평균': m_avg_13hz, 
        '19Hz 중립평균': m_avg_19hz,
        '22Hz 중립평균' : m_avg_22hz,
    }}

@app.route('/first')
def mid_request_1():
    print('첫번째 요청이 왔습니다.')
    time_stamp.append(1) #요청이 들어오면 time_stamp 리스트에 1을 추가
    start = time_stamp.index(1) #추가하는 동시에 time_stamp에서 1의 index를 추가
    print('첫번째 요청 start', start)
    sleep(30) # 30초간 sleep한다. 
    end = len(medium_arr_13hz)-1
    print('첫번째 요청 end', end)
    # return할 값이 flag_1만 있으므로 flag_1만 전역변수로 선언해준다. 
    global flag_1
    sum_13hz = 0.00000000000000000000000
    sum_19hz = 0.00000000000000000000000
    sum_22hz = 0.00000000000000000000000

    # 지역 변수
    avg_13hz = 0.00000000000000000000000
    avg_19hz = 0.00000000000000000000000
    avg_22hz = 0.00000000000000000000000

    red_flag = 0.000000000000000000000000
    blue_flag = 0.000000000000000000000000
    green_flag = 0.000000000000000000000000

    #start~end 라인을 읽어 더한다. 

    for y in range(start, end): 
        for x in range(0,5): 
            sum_13hz += medium_arr_13hz[y][x]
            sum_19hz += medium_arr_19hz[y][x]
            sum_22hz += medium_arr_22hz[y][x]


    #더한 개수로 나눠준다. 
    temp = float((end-start) * 5)
    avg_13hz = sum_13hz / temp
    avg_19hz = sum_19hz / temp
    avg_22hz = sum_22hz / temp

    # 측정된 라인에서 대역별 중립평균의 차를 구하여 flag라는 변수에 저장, 이 셋 중에 가장 큰 값을 가진 변수의 이름을 리턴한다. 
    red_flag = avg_13hz - m_avg_13hz
    green_flag = avg_19hz - m_avg_19hz
    blue_flag = avg_22hz - m_avg_22hz


    # red, blue, green flag 중 가장 큰 flag를 찾아 flag_1이라는 전역변수에 저장한다. 
    if((red_flag >= blue_flag) and (red_flag >= green_flag)):
        flag_1='1-Red'
    elif((blue_flag >= red_flag) and (blue_flag >= green_flag)):
        flag_1='1-Blue'
    elif((green_flag >= red_flag) and (green_flag >= blue_flag)):
        flag_1='1-Green'
    else:
        flag_1='1-Error'

    return {"result": {
        'flag_1': flag_1
    }}

@app.route('/second')
def mid_request_2():
    time_stamp.append(2) #요청이 들어오면 time_stamp 리스트에 1을 추가
    start = time_stamp.index(2) #추가하는 동시에 time_stamp에서 1의 index를 추가
    print('두번째 요청 start', start)
    sleep(30) # 30초간 sleep
    end = len(medium_arr_13hz)-1
    print('두번째 요청 end', end)
    
    global flag_2

    sum_13hz = 0.00000000000000000000000
    sum_19hz = 0.00000000000000000000000
    sum_22hz = 0.00000000000000000000000

    avg_13hz = 0.00000000000000000000000
    avg_19hz = 0.00000000000000000000000
    avg_22hz = 0.00000000000000000000000

    red_flag = 0.000000000000000000000000
    green_flag = 0.000000000000000000000000
    blue_flag = 0.000000000000000000000000


    #start~end 라인을 읽어 더한다. 
    for y in range(start, end):
        for x in range(0,5): 
            sum_13hz += medium_arr_13hz[y][x]
            sum_19hz += medium_arr_19hz[y][x]
            sum_22hz += medium_arr_22hz[y][x]


    # 더한 개수로 나눠 평균을 구해준다. 
    temp = float((end-start)*5) 
    print('두번째 나눗셈 분모', temp)
    avg_13hz = sum_13hz / temp
    avg_19hz = sum_19hz / temp
    avg_22hz = sum_22hz / temp

    # 각 색깔별 평균과 중립평균의 차이를 구한다. 
    red_flag = avg_13hz - m_avg_13hz
    green_flag = avg_19hz - m_avg_19hz
    blue_flag = avg_22hz - m_avg_22hz
    
    # red, blue, green flag 중 가장 큰 flag를 찾아 flag_2이라는 전역변수에 저장한다. 
    if((red_flag >= blue_flag) and (red_flag >= green_flag)):
        flag_2 = flag_1 + '-' + 'Red'
    elif((blue_flag >= red_flag) and (blue_flag >= green_flag)):
        flag_2 = flag_1 + '-' + 'Blue'
    elif((green_flag >= red_flag) and (green_flag >= blue_flag)):
        flag_2 = flag_1 + '-' + 'Green'
    else:
        flag_2 = flag_1 + '-' + 'Error'


    return {"result": {
        'flag_2': flag_2
    }}

@app.route('/third')
def mid_request_3():
    time_stamp.append(3) #요청이 들어오면 time_stamp 리스트에 3을 추가
    start = time_stamp.index(3) #추가하는 동시에 time_stamp에서 3의 index를 추가
    print('세번째 요청 start', start)
    sleep(30) # 30초간 sleep
    end = len(medium_arr_13hz)-1
    print('세번째 요청 end', end)

    
    global flag_3

    sum_13hz = 0.00000000000000000000000
    sum_19hz = 0.00000000000000000000000
    sum_22hz = 0.00000000000000000000000

    avg_13hz = 0.00000000000000000000000
    avg_19hz = 0.00000000000000000000000
    avg_22hz = 0.00000000000000000000000

    red_flag = 0.000000000000000000000000
    blue_flag = 0.000000000000000000000000
    green_flag = 0.000000000000000000000000

    # start~end 라인을 더한다. 
    for y in range(start, end): 
        for x in range(0,5): 
            sum_13hz += medium_arr_13hz[y][x]
            sum_19hz += medium_arr_19hz[y][x]
            sum_22hz += medium_arr_22hz[y][x]

    # 더한 개수로 나눈다. 
    temp = float((end-start)*5)
    print('세번째 나눗셈 분모', temp)
    avg_13hz = sum_13hz / temp
    avg_19hz = sum_19hz / temp
    avg_22hz = sum_22hz / temp

    # 평균과 중립평균의 차를 구한다. 

    red_flag = avg_13hz - m_avg_13hz
    green_flag = avg_19hz - m_avg_19hz
    blue_flag = avg_22hz - m_avg_22hz

    # red, blue, green flag 중 가장 큰 flag를 찾아 flag_3이라는 전역변수에 저장한다. 
    if((red_flag >= blue_flag) and (red_flag >= green_flag)):
        flag_3 = flag_2 + '-' + 'Red'
    elif((blue_flag >= red_flag) and (blue_flag >= green_flag)):
        flag_3 = flag_2 + '-' + 'Blue'
    elif((green_flag >= red_flag) and (green_flag >= blue_flag)):
        flag_3 = flag_2 + '-' + 'Green'
    else:
        flag_3 = flag_2 +'-' +'Error'

    return {"result": {
        'flag_3': flag_3
    }}

if __name__ == '__main__':
    app.run(debug=True)
