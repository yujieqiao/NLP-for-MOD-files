import json
with open("modeldb-metadata.json") as peach:
    data_lib = json.load(peach)

#find the associated models for a specific "object_id"
def count_within_item(item, look_for):
    if item['object_id']==look_for:
        return 1
    else:
        return 0


def count_within_list(list_of_items, look_for):
    try:
        s=0
        for item in list_of_items:
            s =  count_within_item(item, look_for)+s
        return s
    except:
        return 0

def count_within_model(model, look_for):
    s=0
    for v in model.values():
        s =  count_within_list(v, look_for)+s
    return s

def count_within_data(dat, look_for):
    s=0
    model_list=[]
    for v in dat.values():
        s =  count_within_model(v, look_for)+s
        if count_within_model(v, look_for)==1:
            model_list.append(v['id'])
    return set(model_list)
    

#find the list of all "object_id" and store it in "unique_list"
def find_within_item(item):
        return item['object_id']


def find_within_list(list_of_items):
    try:
        s=[]
        for item in list_of_items:
            s.append(find_within_item(item))
        return s
    except:
        return []
    

def find_within_model(model):
    s=[]
    for v in model.values():
        s.extend(find_within_list(v))
    return s

def find_within_data(dat):
    s=[]
    for v in dat.values():
        s.extend(find_within_model(v))
    return s


freq=find_within_data(data_lib)
from collections import Counter
egg=Counter(freq)

unique_list = []
for x in freq:
    if x not in unique_list:
        unique_list.append(x)


#link each "object_id" to its assocaited "object_name"
def link_within_item(item):
    dict1 = {}
    dict1[item['object_id']] = item['object_name']
    return dict1


def link_within_list(list_of_items):
    try:
        s={}
        for item in list_of_items:
            s.update(link_within_item(item))
        return s
    except:
        return {}
    

def link_within_model(model):
    s={}
    for v in model.values():
        s.update(link_within_list(v))
    return s

def link_within_data(dat):
    s={}
    for v in dat.values():
        s.update(link_within_model(v))
    return s


linkage=link_within_data(data_lib)


#Create a dictionary which stores each unique object id and its associated models 
# aggregate_model_dict = {}
# for i in unique_list:
#     aggregate_model_dict[i] = count_within_data(data_lib, i)

#This line of code is a more efficient alternative to the above lines of codes:
aggregate_model_dict = {i:count_within_data(data_lib,i) for i in unique_list}


my_dict = {}
my_list = []
conditional_prob_diff = {}
for item,val in aggregate_model_dict.items():
    for item2,val2 in aggregate_model_dict.items():
        if not item==item2:
            if len(val.intersection(val2))>10: #filter out the pairs whose co-occurrence is greater than 10
                #my_list.append((item,item2))
                #my_dict[(item,item2)] = len(val.intersection(val2)) #return the number of co-occurrence for those pairs
                delta_probability = len(val.intersection(val2)) / egg[item2] - egg[item] / len(data_lib) #the difference between the conditional probability and the individual probability P(A|B) - P(A). For example, 
                #(‘Basal ganglia’, “Parkinson’s”): 0.5714. Here ‘Basal ganglia’ is A, “Parkinson’s” is B. It means the additional probability of presence of Basal ganglia across all 1706 models is 0.5714 given the presence of Parkinson’s
                if delta_probability > 0.5 or delta_probability < -0.2:
                    pt=(item,item2)
                    print((linkage[pt[0]], linkage[pt[1]]),':', delta_probability)
                


