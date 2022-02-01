import zipfile
import hashlib
import os
import pprint
import json
from collections import Counter


#Generate a dictionary called “v”. For “v” - each key represents the model id number, e.g. ‘87284’. And the value for each key is a list of strings which stands for the sha256 numbers of mod files
models_by_mod_file = {}
for zip_file in os.listdir("/Users/YUQIAO/Desktop/Projects/metadata/zips"):
    names = (os.path.splitext(zip_file)[0])
    if zip_file.endswith(".zip"):
        data=zipfile.ZipFile("/Users/YUQIAO/Desktop/Projects/metadata/zips/"+zip_file)
        for file in data.namelist():
            if file.endswith(".mod"):
                mod_file_id = hashlib.sha256(data.read(file)).hexdigest()
                models_by_mod_file.setdefault(mod_file_id, set())
                models_by_mod_file[mod_file_id].add(names)


#print(len(models_by_mod_file))

with open("modeldb-metadata.json") as peach:
    data_lib = json.load(peach)



#print(len(data_lib))

def find_within_item(item):
        return item['object_name']

def find_within_list(list_of_items):
    try:
        s=[]
        for item in list_of_items:
            s.append(find_within_item(item))
        return s
    except:
        return []

def find_within_model(model):
    if 'currents' in model:
        s=find_within_list(model['currents'])
        #s = list(set(s))
    else:
        return []
    return s


#a=find_within_model(data_lib['87284'])
#print(a)
#print(data_lib['87284']['currents'])

currents_dict = {}
currents_dict1 = {}
for item,val in models_by_mod_file.items():
    v=[]
    for p in val:
        v.extend(find_within_model(data_lib[p]))
    currents_dict[item]=[x for x in Counter(v).items() if x[1] >= 4]
    #currents_dict[item]=v
    if currents_dict[item]!=[]:
        currents_dict1[item]=currents_dict[item]


#pprint.pprint(currents_dict)
#print("The models assocaited with 'dce220cef3c30f66aefdc235631666ead0ff1a9e3a340614f0a7c6918f4e1176' are: ", models_by_mod_file['dce220cef3c30f66aefdc235631666ead0ff1a9e3a340614f0a7c6918f4e1176'])
#print("The currents appeared in model '87535' are: ", find_within_model(data_lib['87535']))
#print("The currents appeared in model '170030' are: ", find_within_model(data_lib['170030']))
#print("All the currents associated with 'dce220cef3c30f66aefdc235631666ead0ff1a9e3a340614f0a7c6918f4e1176' are: ", currents_dict['dce220cef3c30f66aefdc235631666ead0ff1a9e3a340614f0a7c6918f4e1176'])
#print(currents_dict1)

data=zipfile.ZipFile("/Users/YUQIAO/Desktop/Projects/metadata/zips/87535.zip")
names=[]
for file in data.namelist():
    if file.endswith(".mod"):
        pathname, extension = os.path.splitext(file)
        filename = pathname.split('/')
        names.append(filename[-1])

#print("List of mod files names in model '87535' are: ", names)

def check_user(h):
    for i in names:
        if h == hashlib.sha256(data.read(i+".mod")).hexdigest():
            filename = i.split('/')
            return filename[-1]
            #return i


#print("The mod file name for 'dce220cef3c30f66aefdc235631666ead0ff1a9e3a340614f0a7c6918f4e1176' are: ", check_user('dce220cef3c30f66aefdc235631666ead0ff1a9e3a340614f0a7c6918f4e1176'))

mod_currents_dict={}
for item,val in currents_dict1.items():
    a=list(models_by_mod_file[item])[0] #return the first model ID
    data=zipfile.ZipFile("/Users/YUQIAO/Desktop/Projects/metadata/zips/"+str(int(a))+".zip")
    names=[]
    for file in data.namelist():
        if file.endswith(".mod"):
            names.append(os.path.splitext(file)[0])
            #pathname, extension = os.path.splitext(file)
            #filename = pathname.split('/')
            #names.append(filename[-1])
    mod_currents_dict[(a,check_user(item))]=val

pprint.pprint(mod_currents_dict)
#print(len(currents_dict))
#print(len(currents_dict1))
#print(len(mod_currents_dict))
#print(mod_currents_dict['magical7/h'])