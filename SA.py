import matplotlib.pyplot as plt
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
import random
import math

# 텍스트 데이터를 리스트로 만들기
data_list = []
with open("ft06.txt",'r') as data:
    for i in data:
        data_list.append(i.split())

job_num = len(data_list[0]) 

# (기계번호 ,해당 기계에서 작업시간)을  묶기
final_data = []
for i in range(len(data_list)):
    job_list = []
    for j in range(0,job_num,2):
        job_list.append([data_list[i][j],data_list[i][j+1]])

    final_data.append(job_list) 

# 초기 작업 배열 생성
def initial_arr(): 
    lst = []
    for _ in range(len(data_list)):
        lst.append(list(range(0,len(final_data))))

    job_arr = []
    for i in range(len(lst)):
        for j in range(len(lst)):
            job_arr.append(lst[i][j])
    random.shuffle(job_arr)
    return job_arr

def fitness(arr):
    
    job_sequence = [0] * len(final_data) # 작업 순서: 작업 개수만큼 리스트 생성
    mc_finish_time = [0] * len(final_data) # 기계별 종료 시간
    job_finish_time = [0] * len(final_data) # 작업별 종료 시간
    
    for i in arr:
        step = job_sequence[i]
        mc_num, prc_time = final_data[i][step]  # 값 가져오기
        mc_num, prc_time = int(mc_num), int(prc_time)

        start_time = max(mc_finish_time[mc_num],job_finish_time[i])
        end_time = start_time + prc_time    

        mc_finish_time[mc_num] = end_time
        job_finish_time[i] = end_time

        job_sequence[i] += 1

    make_span = max(mc_finish_time) # 각 기계중 최댓값
    return [make_span,arr]

# 역전 방식
def reversal(pop):
    p = pop.copy()
    num = random.randint(len(p)/4,len(p)/2)  # 배열길이/4 ~ 배열길이/2 중 랜덤값 선택
    idx = random.sample(range(0,len(p)),num) # 역전할 작업 인덱스 랜덤 추출
    job = []
    for i in range(len(idx)):
        job.append(p[idx[i]])

    job = job[::-1]
    for i in range(len(idx)):
        p[idx[i]] = job[i]
    new = fitness(p)
    new_arr = new[1]
    return new_arr


# 스왑 방식
def swap(pop):
    p = pop.copy()
    idx = random.sample(range(0,len(p)),2)
    first = p[idx[0]]
    second = p[idx[1]]
    p[idx[0]] = second  # 단순 인덱스 끼리 교환시 값 달라지므로 미리 저장한 값으로 대체
    p[idx[1]] = first

    return p
    
#-----외부 루프------------------
T = 1000
so_cool = 0.99 # 냉각률
pop = initial_arr() # 초기 배열 선언
out_iter = 0
cnvrg = [] # 온도별 make span 리스트 
cnvrg.clear()
while True:
    in_iter = 0
    make_span = fitness(pop)[0]
    
    #--------------내부 루프------------
    while True:
        existing_arr = pop.copy() # 기존 배열 저장

        if T > 500: # 온도 높을시 역전 방식
            pop = reversal(pop)
        else: # 온도 낮을시 스왑 방식
            pop = swap(pop)

        new = fitness(pop)
        value = new[0] # make span
        job_arr = new[1] # 작업 배열

        # 해 수용 여부 결정
        if value < make_span:
            make_span = value
            pop = job_arr
            
        else:
            a = random.random()
            p = math.exp(-(value-make_span)/T)
            if a <= p:
                pop = job_arr
            else:
                pop = existing_arr
        in_iter += 1
        if in_iter == 100:
            break
    # ------------내부 루프 종료-------------------
    cnvrg.append(fitness(pop)[0])
    T = T * so_cool
    out_iter += 1
    if out_iter == 1000:
        break

plt.plot(cnvrg,color = 'royalblue')
plt.xlabel('반복수',fontsize = 20)
plt.ylabel('make span',fontsize = 20)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.title(f"수렴값: {make_span}")
plt.show()
print(make_span,'\n',pop)



# 기존 6개 + 추가 4개 (총 10개 작업용)
colors = [
    "#F85858", "#66B2FF", "#767876", "#F0A65D", "#9971C5", "#1AEDF4", # 기존
    "#FFD700", "#FF69B4", "#32CD32", "#8B4513"                      # 추가 (Gold, HotPink, LimeGreen, SaddleBrown)
]

job_sequence = [0] *len(final_data) # 작업 순서
mc_finish_time = [0] * len(final_data) # 기계별 종료 시간
job_finish_time = [0] * len(final_data) # 작업별 종료 시간

for i in pop:
    
    step = job_sequence[i]

    mc_num , prc_time = final_data[i][step]
    mc_num , prc_time = int(mc_num),int(prc_time)

    start_time = max(mc_finish_time[mc_num],job_finish_time[i])
    end_time = start_time + prc_time 
    
    mc_finish_time[mc_num] = end_time
    job_finish_time[i] = end_time

    job_sequence[i] += 1
    
    plt.barh(mc_num, prc_time, left=start_time, edgecolor='black', color=colors[i])
    plt.text(start_time + prc_time/2, mc_num, f'Job {i}', va='center', ha='center')

mc = max(mc_finish_time)
plt.yticks(range(len(final_data)),fontsize=20)
plt.xticks(fontsize=20)
plt.title(f'간트 차트 (make span:{mc})',fontsize = 20)
plt.xlabel('시간',fontsize = 20)
plt.ylabel('기계번호',fontsize = 20)

plt.show()
print(f"\n 수렴 리스트:{cnvrg}")

