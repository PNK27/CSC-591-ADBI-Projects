import csv
import pandas as pd
import operator
import math
import sys
import copy
import random

def check_budget(bid_amt,budget):
    if(budget < bid_amt):
        return False
    else:
        return True
#---------------------------------------Greedy-------------------------------------------
def greedy(queries,query_bid,budget_dict):
    rev = 0.0
    for query in queries:
        for l in query_bid[query]:
            inBudget = check_budget(l[1],budget_dict[l[0]])
            if(inBudget):
                budget_dict[l[0]] = budget_dict[l[0]] - l[1]
                rev+=l[1]
                break
            else:
                continue
    return rev
#---------------------------------------Balance------------------------------------------
def balance(queries,query_bid,budget_dict):
    rev = 0.0
    for query in queries:
        max_budget = 0.0
        max_bidder = -1
        for l in (query_bid[query]):
            inBudget = check_budget(l[1],budget_dict[l[0]])
            if(inBudget):
                if(budget_dict[l[0]] > max_budget):
                    max_budget = budget_dict[l[0]]
                    max_bidder = l[0]
                    
                elif(budget_dict[l[0]] == max_budget):    
                    if(max_bidder > l[0]):
                        max_bidder = l[0]
                            
            else:
                continue
        for j in query_bid[query]:
            if(j[0] == max_bidder):
                budget_dict[j[0]] = budget_dict[j[0]] - j[1]
                rev+=j[1]
                break
                
    return rev
#---------------------------------------MSVV---------------------------------------------
def psi(bid,full_budget,curr_budget):
    spent = full_budget - curr_budget
    frac = spent/full_budget
    
    psi = 1 - math.exp(frac - 1)
    return (psi*bid)

def msvv(queries,query_bid,clean_all_budgets,budget_dict):
    rev = 0.0
    for query in queries:
        max_scaled = 0.0
        max_bidder = -1
        for l in query_bid[query]:
            inBudget = check_budget(l[1],budget_dict[l[0]])
            if(inBudget):
                sb = psi(l[1],clean_all_budgets[l[0]],budget_dict[l[0]])
                if(sb > max_scaled):
                    max_scaled = sb 
                    max_bidder = l[0]
                   
            else:
                continue
        for j in query_bid[query]:
            if(j[0] == max_bidder):
                budget_dict[j[0]] -= j[1]
                rev+=j[1]
                break
    return rev  
#----------------------------main-----------------------------    
bidder_df = pd.read_csv(r"./bidder_dataset.csv")
optimal_rev  = bidder_df.sum(axis = 0)[3]

queries = []
with open(r'queries.txt', 'r') as f:
    queries = [line.strip() for line in f]
    
all_budgets = []
all_budgets = bidder_df['Budget'].tolist()
clean_all_budgets = [x for x in all_budgets if str(x) != 'nan']


subset = bidder_df[['Advertiser','Bid Value','Keyword']]
tuples = [x for x in subset.values]

query_bid = {}

for q in queries:
    temp = []
    for x in tuples:
        if(x[2] == q):
            temp.append([x[0],x[1]])
            query_bid[q] = temp

for x in query_bid:
    query_bid[x].sort(key = operator.itemgetter(1), reverse = True)

budget_dict={}
for x in range(0,len(clean_all_budgets)):
    budget_dict[x] = clean_all_budgets[x]

#----------------------Check type-------------------------
type = sys.argv[1]
if(sys.argv[1] == None):
    print("Argument not provided")
    sys.exit()
final_rev = 0.0
    
if(type == 'greedy'):
    Totrev = greedy(queries,copy.deepcopy(query_bid),copy.deepcopy(budget_dict))
    print(round(Totrev,2))
    for i in range(100):
        random.shuffle(queries)
        final_rev+=greedy(queries,copy.deepcopy(query_bid),copy.deepcopy(budget_dict))
    final_rev/=100
    
    comp_Ratio = final_rev/optimal_rev
    print(round(comp_Ratio,2))
    
elif(type == 'balance'):
    Totrev_balance = balance(queries,copy.deepcopy(query_bid),copy.deepcopy(budget_dict))
    print(round(Totrev_balance,2))
    for i in range(100):
        random.shuffle(queries)
        final_rev+=balance(queries,copy.deepcopy(query_bid),copy.deepcopy(budget_dict))  
    final_rev/=100
    
    comp_Ratio_balance = round(Totrev_balance,2)/optimal_rev
    print(round(comp_Ratio_balance,2))
    
elif(type == 'msvv'):
    Tot_rev = msvv(queries,copy.deepcopy(query_bid),copy.deepcopy(clean_all_budgets),copy.deepcopy(budget_dict))
    print(round(Tot_rev,2))
    for i in range(100):
        random.shuffle(queries)
        final_rev+=msvv(queries,copy.deepcopy(query_bid),copy.deepcopy(clean_all_budgets),copy.deepcopy(budget_dict))
    final_rev/=100
    
    comp_Ratio_msvv = round(Tot_rev,2)/optimal_rev
    print(round(comp_Ratio_msvv,2))

else:
    sys.exit()
    

    

    
    