import matplotlib.pyplot as plt
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')


import random
import itertools

# 텍스트 데이터를 리스트로 만들기
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

# 초기 염색체 생성
def initial_chrome(): 
    lst = []
    for _ in range(len(data_list)):
        lst.append(list(range(0,len(final_data))))

    chromo = list(itertools.chain.from_iterable(lst)) # 대용량 데이터 고려 itertools 사용
    random.shuffle(chromo)
    return chromo



# 적합도 평가
def fitness(chrom):
    
    job_sequence = [0] * len(final_data) # 작업 순서: 작업 개수만큼 리스트 생성
    mc_finish_time = [0] * len(final_data) # 기계별 종료 시간
    job_finish_time = [0] * len(final_data) # 작업별 종료 시간
    
    for i in chrom:
        step = job_sequence[i]
        mc_num, prc_time = final_data[i][step]  # 값 가져오기
        mc_num, prc_time = int(mc_num), int(prc_time)

        start_time = max(mc_finish_time[mc_num],job_finish_time[i])
        end_time = start_time + prc_time    

        mc_finish_time[mc_num] = end_time
        job_finish_time[i] = end_time

        job_sequence[i] += 1

    make_span = max(mc_finish_time) # 각 기계중 최댓값
    return [make_span,chrom]



# 선택 (룰렛휠)
def selection(population): # 인자: [[(makespan,염색체)],[],[]]

    candi_makespan = [] # makespan 후보
    candi_chrom = [] # 그에 해당하는 염색체 후보

    for i in range(len(population)): # 받은 makespan 리스트 생성
        candi_makespan.append(population[i][0])

    for i in range(len(population)): # 받은 염색체 리스트
        candi_chrom.append(population[i][1])

    

    for i in range(len(candi_makespan)):
        candi_makespan[i] = 1/candi_makespan[i]
    s = sum(candi_makespan)

    for i in range(len(candi_makespan)):
        candi_makespan[i] = candi_makespan[i]/s
    # 룰렛휠 
    rk = 0
    rk_lst = []
    for i in candi_makespan:
        rk += i
        rk_lst.append(rk)
    
    prob = random.random()
    a = 0
    for i in range(len(rk_lst)):
        if prob <= rk_lst[i]:
            a = i
            break

    prob2 = random.random()
    b = 0
    for i in range(len(rk_lst)):
        if prob2 <= rk_lst[i]:
            b = i
            break

    first_par = candi_chrom[a]
    seccond_par= candi_chrom[b]
    
    return [first_par,seccond_par]


# 교차- 돌연변이 필요한 이유가 교차했을때 염색체가 부모=자손 인 경우땜시?
def cross(chromo):
    
    p1 = chromo[0].copy()
    p2 = chromo[1].copy()

    p1c = p1.copy()
    p2c = p2.copy()
    fixed_num = random.sample(range(len(final_data)), 2) # 고정할 작업 번호

    child1 = []
    child2 = []
    
    #자손 1
    remaining1 = [] # p2염색체에서 고정할 작업 순차적으로 저장

    for i in range(len(p1)): # p1에서 고정할 작업이 있으면 작업번호롤 -1로 치환
        if p1c[i] in fixed_num:
            p1c[i] = -1

    for i in range(len(p2)): # p2에서 고정할 작업있는거 따로 빼줌(순차적으로 빼짐)
        if p2c[i] in fixed_num:
            remaining1.append(p2[i])

    idx = 0
    for i in range(len(p1)): # p1에서 -1인 값에 고정할 작업 순차적으로 넣어줌
        if p1c[i] == -1:
            p1c[i] = remaining1[idx]
            idx += 1
    child1 = p1c
    
    # 자손2
    remaining2 = [] 

    for i in range(len(p2)): 
        if p2c[i] in fixed_num:
            p2c[i] = -1

    for i in range(len(p1)): 
        if p1c[i] in fixed_num:
            remaining2.append(p1c[i])

    idx1 = 0
    for i in range(len(p2)): 
        if p2c[i] == -1:
            p2c[i] = remaining2[idx1]
            idx1 += 1
    child2 = p2c

    return [child1,child2]

# 돌연변이
def mutaion(child):
    mutaion_rate = 0.1

    if random.random() <= mutaion_rate:
        index = random.sample(range(len(final_data)**2),2)
        idx1 = index[0]
        idx2 = index[1]
        
        #변이
        child[idx1], child[idx2] = child[idx2], child[idx1]

    return child

# 시작--------------------------------------
se = 0
seq = []
while se < 50:
    pop_size = 100
    population = []
    convergen = []   
    for _ in range(pop_size):   # 초기 집단 생성
            population.append(initial_chrome())
    avg = []

    generation = 0
    while True: # -----외부 루프------
        fit_lst = []
        selec_lst = []
        child_lst = []
        new_gene = []
        new_gene.clear()
        avg.clear()

        # 적합도 연산
        for i in range(pop_size):
            fit_lst.append(fitness(population[i]))

        # 세대별 최적값 저장
        current_makespan = []
        current_chrom = []
        for i in range(len(fit_lst)):
            current_makespan.append((fit_lst[i])[0])
            current_chrom.append(fit_lst[i][1])

        current_best = min(current_makespan)
        

        # 엘리트 확보
        indx = current_makespan.index(current_best)
        each_gen_best = current_chrom[indx].copy()
        
        #-----------내부루프 100회-------
        while True:
                # 선택 연산
            selec_lst = selection(fit_lst) 
            
                # 교차 연산
            child_lst.append(cross(selec_lst))

                # 돌연변이 연산
            for i in range(len(child_lst)): 
                for j in range(len(child_lst[0])):
                    new_gene.append(mutaion(child_lst[i][j]))

            selec_lst.clear()
            child_lst.clear()
            if len(new_gene) == pop_size:
                break
        fit_lst.clear() 
        population = new_gene
        generation += 1

        population[0] = each_gen_best
        #-------------내부루프 종료--------------
        for i in population:
            avg.append(fitness(i)[0])

        each_avg = sum(avg) / len(avg)
        convergen.append(each_avg)

        if generation == 1000:
            population[0] = each_gen_best
            break
    #------------------외부루프 종료

    # 결과 출력
    optimized_makespan = []
    optimized_chrom = []

    for i in range(len(population)):
        optimized_makespan.append(fitness(population[i])[0])
        optimized_chrom.append(fitness(population[i])[1])

    best_makespan = min(optimized_makespan)
    best_idx = optimized_makespan.index(best_makespan)
    best_chrom = optimized_chrom[best_idx]

    seq.append(best_makespan)
    optimized_chrom.clear()
    optimized_makespan.clear()

    se += 1
    if se == 50:
        break

    # print(f'Make Span:{best_makespan}','\n')
    # print(f'작업 순서:{best_chrom}')

    # plt.plot(convergen,color = 'royalblue')
    # plt.title(f'make span:{best_makespan}')
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

# for i in best_chrom:
    
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
