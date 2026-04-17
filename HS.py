import matplotlib.pyplot as plt
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
import random



data_list = []
with open("ft10.txt",'r') as data:
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

# make span 계산
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

def ini_var():
    variable = [] # 작업 집합
    hm_size = 100
    for _ in range(hm_size):
        variable.append(initial_arr())
    return variable
IA = 0
IAA = []
while IA < 50:
    variable = ini_var() # 초기 변수 집단 생성

    var_size = 100
    hmcr = random.uniform(0.7,0.8) # 메모리에서 참조할 확률
    par = random.uniform(0.2,0.5) # 피치 미세조정할 확률

    for _ in range(var_size):
        variable.append(initial_arr())

    harmony_num = random.randint(30,100) # 하모니 메모리 개수 지정

    hm = [] # 하모니 메모리
    hm_fit = [] # hm의 make span 집합
    cnvg = []

    h_idx = random.sample(range(0,len(variable)),harmony_num) # 초기집단에서에서 해 인덱스 랜덤선택
    for i in range(harmony_num): # 하모니 메모리 생성
        hm.append(variable[h_idx[i]])


    avg_lst = []
    outter_i = 0
    while True:
        inner_i = 0
        hm_fit.clear()
        avg_lst.clear()
        for arg in hm:  # 하모니 메모리의 make span 계산
            hm_fit.append(fitness(arg)[0])

        worst = max(hm_fit)  # 하모니 메모리에서 최악의 make span
        best = min(hm_fit) # 최고띠
        worst_idx = hm_fit.index(worst)
        worst_harmony = hm[worst_idx] # hm에서 최악의 해

        best_idx = hm_fit.index(best)
        best_har = hm[best_idx] # hm에서 제일 좋은 해
        while True:
            b = random.random() # 피치 조정 확률
                
            new_memory = []
            record_job = [0] * len(final_data) # 몇번째 작업 선택햇는지 기록하는 리스트

            for i in range(len(variable[0])):
                a = random.random() # 메모리 참조 여부

                if a <= hmcr: # '메모리 참조 할때'

                    job_arg = random.choice(hm) # 메모리에서 참조된 해
                    chosen = job_arg[i] # 선택된 작업번호
                        
                else: # '메모리 참조 안할때'
                    chosen = random.randint(0,len(final_data)-1) # 작업번호 랜덤 추출
                
                while record_job[chosen]>=len(final_data):
                    chosen = random.randint(0,len(final_data)-1)
                
                new_memory.append(chosen)
                record_job[chosen] += 1
            
            if b <= par: # 피치 조정 여부 결정
                for _ in range(10): # 조정
                    cros_idx = random.sample(range(0,len(new_memory)),2)
                    job1 = new_memory[cros_idx[0]]
                    job2 = new_memory[cros_idx[1]]

                    new_memory[cros_idx[0]] = job2
                    new_memory[cros_idx[1]] = job1

                    new_memory = new_memory
            value = fitness(new_memory)[0]

            if value < worst: # 해 더 좋은경우 교체
                hm[worst_idx] = new_memory

            # 가장 좋은 해 유지
            mini = min(hm_fit)
            midx = hm_fit.index(mini)
            val = hm[midx]
            hm[0] = val
            
            inner_i += 1
            if inner_i == 100:
                break

        # for i in hm:
        #     avg_lst.append(fitness(i)[0])
        # cnvg.append(sum(avg_lst)/len(avg_lst)) # 루프별 적합도  

        mini = min(hm_fit)
        midx = hm_fit.index(mini)
        val = hm[midx]
        hm[0] = val
        outter_i += 1
        if outter_i == 1000:
            break
    final_makespan = []
    optimzed_makespan = []


    for i in hm:
        final_makespan.append(fitness(i)[0])

    op = min(final_makespan)
    f_idx = final_makespan.index(op)
    f_value = hm[f_idx]
    IA += 1
    IAA.append(op)
    if IA == 50:
        break
plt.plot(IAA)
plt.title(f"최적갑: {min(IAA)}")
plt.show()
# plt.plot(cnvg)
# plt.xlabel('반복수',fontsize = 20)
# plt.ylabel('make span',fontsize = 20)
# plt.title(f"최종 make span: {op}")
# plt.show()


# 작업 색상 리스트
#colors = ["#F85858", '#66B2FF', '#99FF99', "#F0A65D", "#9971C5", "#1AEDF4"]
# 기존 6개 + 추가 4개 (총 10개 작업용)
# colors = [
#     "#F85858", "#66B2FF", "#767876", "#F0A65D", "#9971C5", "#1AEDF4", # 기존
#     "#FFD700", "#FF69B4", "#32CD32", "#8B4513"                      # 추가 (Gold, HotPink, LimeGreen, SaddleBrown)
# ]

# job_sequence = [0] *len(final_data) # 작업 순서
# mc_finish_time = [0] * len(final_data) # 기계별 종료 시간
# job_finish_time = [0] * len(final_data) # 작업별 종료 시간

# for i in f_value:
    
#     step = job_sequence[i]

#     mc_num , prc_time = final_data[i][step]
#     mc_num , prc_time = int(mc_num),int(prc_time)

#     start_time = max(mc_finish_time[mc_num],job_finish_time[i])
#     end_time = start_time + prc_time 
    
#     mc_finish_time[mc_num] = end_time
#     job_finish_time[i] = end_time

#     job_sequence[i] += 1
    
#     plt.barh(mc_num, prc_time, left=start_time, edgecolor='black', color=colors[i])
#     plt.text(start_time + prc_time/2, mc_num, f'Job {i}', va='center', ha='center')

# mc = max(mc_finish_time)
# plt.yticks(range(len(final_data)),fontsize=15)
# plt.title(f'간트 차트 (make span:{mc})',fontsize = 20)
# plt.xlabel('시간',fontsize = 20)
# plt.ylabel('기계번호',fontsize = 20)
# plt.show()
# print(f"최종 make span: {op}\n최종 해: {f_value}")