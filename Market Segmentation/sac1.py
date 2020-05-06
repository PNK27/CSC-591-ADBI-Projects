import sys
import pandas as pd
from igraph import *
import numpy as np
from scipy import spatial
import os

#-----------------Goodness measure: Cosine Similarity----------------------
def similarity(v1,v2,g):
    ver1 = list(g.vs[v1].attributes().values())
    ver2 = list(g.vs[v2].attributes().values())
    sim = 1-spatial.distance.cosine(ver1,ver2)
    return sim
#-----------------Algorithm 1st phase--------------------------------------
#Helps obtain initial communities with high modularity gains
def p1(g,cos_sim,init_communities):
    for i in range(num_attr):
        for j in range(num_attr):
            cos_sim[i][j] = similarity(i,j,g)
    num_comm = cluster(init_communities)
    iter = 0
    
    while(num_comm > 0 and iter < 15):
        iter+=1
        num_comm = cluster(init_communities) 
#------------------Algorithm 2nd phase-------------------------------------
def p2(g,init_communities,sim_vertices,cos_sim):
    count = 0
    global num_attr 
    for comm in init_communities:
        for v in comm:
            sim_vertices[v] = count
        count+=1
    g.contract_vertices(sim_vertices, combine_attrs = "mean")
    g.simplify(multiple = True, loops = True)

    
    num_attr = count
    init_communities = [[v] for v in range(num_attr)]

    g.es["weight"] = [0 for edge in range(len(g.es))]
    for edge in edges:
        partition1 = sim_vertices[edge[0]]
        partition2 = sim_vertices[edge[1]]
        
        if(partition1 != partition2):
            id = g.get_eid(partition1,partition2)
            g.es["weight"][id] += 1 
    #recalculating similarity        
    for i in range(num_attr):
        for j in range(num_attr):
            cos_sim[i][j] = similarity(i,j,g)    
        
    p1(g,cos_sim,init_communities)
#--------------------------Modularity--------------------------------------
def composite_modularity(ver,community):
    q_newman = 0.0
    q_attr = 0.0
    link_str = 0
    degree = 0
    
    num_edges = len(g.es)
    community = list(set(community))
    #finding q_newman
    for c in community:
        if (g.are_connected(ver,c)):
            idx = g.get_eid(ver,c)
            link_str += g.es["weight"][idx]
    q_newman =  (link_str - sum(g.degree(community)) * g.degree(ver) / (2.0 * num_edges))/(2.0 * num_edges)
    
    #finding q_attr
    for c in community:
        q_attr = q_attr + cos_sim[c][ver]
    q_attr = (q_attr/len(community)/len(community))

    modularity_gain = alpha * q_newman + (1 - alpha) * q_attr
    return modularity_gain
#--------------------------Cluster formation-------------------------------
def cluster(init_communities):
    ctr = 0
    for att in range(num_attr):
        mod_gain = 0
        v_community = []
        
        for community in init_communities:
            if att in community:
                v_community = community
                break
                
        max_gain = -1
        max_comm = []
        
        #remove community if gain is lesser 
        for community in init_communities:
            mod_gain = composite_modularity(att,community)
            if mod_gain > 0:
                if(mod_gain > max_gain):
                    max_gain = mod_gain
                    max_comm = community
        #add community to cluster with highest gain        
        if set(max_comm) != set(v_community):
            if max_gain > 0:
                v_community.remove(att)
            max_comm.append(att)
            ctr=ctr+1
            
            if(len(v_community) == 0):
                init_communities.remove([])
                
    return ctr         
#---------------------------Data Processing--------------------------------
attributes_df = pd.read_csv("./data/fb_caltech_small_attrlist.csv")
f = open("./data/fb_caltech_small_edgelist.txt","r")
edgelist = f.read().split("\n")

alpha = float(sys.argv[1])

edges = []
for edge in edgelist:
	x = edge.split(' ')
	if x[0] != '' and x[1] != '':
		edges.append((int(x[0]),int(x[1])))

        
#print("Edges:",edges)
num_attr = len(attributes_df)

g = Graph()
g.add_vertices(num_attr)
g.add_edges(edges)
g.es['weight'] = [1 for x in range(len(edges))]

for col in attributes_df.keys():
	g.vs[col] = attributes_df[col]

#print("G is:",g)
global cos_sim
cos_sim = np.zeros((num_attr,num_attr))

for i in range(num_attr):
        for j in range(num_attr):
            cos_sim[i][j] = similarity(i,j,g)


#each vertex is initially single one in the entire community
init_communities = [[x] for x in range(num_attr)]
sim_vertices = [0 for x in range(num_attr)]

#phase 1 is for initial groups               
p1(g,cos_sim,init_communities)

#phase 2 is for regrouping
p2(g,init_communities,sim_vertices,cos_sim)

f2 = open("./communities.txt", "w")
for community in init_communities:
    for i in range(len(community)):
        if i != 0:
            f2.write(",")
        f2.write(str(community[i]))
    f2.write("\n")
f2.close()

if(alpha == 0):
    os.rename("communities.txt", "communities_0.txt")
if(alpha == 0.5):
    os.rename("communities.txt", "communities_5.txt")
if(alpha == 1):
    os.rename("communities.txt", "communities_1.txt")
    