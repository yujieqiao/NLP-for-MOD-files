import zipfile
import hashlib
import os
import pprint
import json
from collections import Counter
import filecmp
import spacy
import tqdm
nlp = spacy.load('en_core_web_sm')
from difflib import Differ
import tlsh
import csv
from difflib import Differ
import nmodl



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

def non_comment_or_title_iterator(text):
    inside_block_comment = False
    for line in text.split(b'\n'):
        line_without_whitespace = line.strip()
        if inside_block_comment:
            if line_without_whitespace.startswith(b"ENDCOMMENT"):
                inside_block_comment = False
        elif line_without_whitespace.startswith(b"COMMENT"):
            inside_block_comment = True
        elif line_without_whitespace.startswith(b"TITLE"):
            # title
            pass
        else:
            yield line


def remove_block_comments_and_title(text):
    return b"\n".join(non_comment_or_title_iterator(text))


def standardize_nmodl(text):
    # the ast process drops single line comments but not block comments
    # and expresses whitespace consistently
    driver = nmodl.NmodlDriver()
    ast = driver.parse_string(remove_block_comments_and_title(text))
    return nmodl.to_nmodl(ast)



def check_user(h):
    for i in names:
        if h == hashlib.sha256(data.read(i+".mod")).hexdigest():
            filename = i.split('/')
            return filename[-1]
            #return i

def check_user2(h):
    for i in names:
        if h == hashlib.sha256(data.read(i+".mod")).hexdigest():
            return data.read(i+".mod")



             
fn_doc={}
non_cleanable={}
for item,val in models_by_mod_file.items():
    a=list(models_by_mod_file[item])[0] #return the first model ID
    data=zipfile.ZipFile("/Users/YUQIAO/Desktop/Projects/metadata/zips/"+str(int(a))+".zip")
    names=[]
    for file in data.namelist():
        if file.endswith(".mod"):
            names.append(os.path.splitext(file)[0])
            #print(a,file)
    try:
        fn_doc[(a,check_user(item))]=nlp(standardize_nmodl(check_user2(item)))
    except:
        non_cleanable[(a,check_user(item))]="non cleanable"


    
#pprint.pprint(fn_doc)
print(len(fn_doc))  
print(len(non_cleanable))        
           
sim_mod={}
for item,val in tqdm.tqdm(fn_doc.items()):
    for item2,val2 in fn_doc.items():
        if item!=item2:
            if val.similarity(val2)>=0.995:
                sim_mod[(item,item2)]=val.similarity(val2) 


compare_mod={}
for item,val in tqdm.tqdm(sim_mod.items()):
    a=item[0][0] #return the model ID
    data=zipfile.ZipFile("/Users/YUQIAO/Desktop/Projects/metadata/zips/"+str(int(a))+".zip")
    for file in data.namelist():
        if os.path.splitext(file)[0].split('/')[-1]==str(item[0][1]):
            try:
                h1=tlsh.hash(standardize_nmodl(data.read(file)).encode("utf8"))
            except:
                blank=[]
         
    b=item[1][0] #return the model ID 
    data2=zipfile.ZipFile("/Users/YUQIAO/Desktop/Projects/metadata/zips/"+str(int(b))+".zip")
    for file in data2.namelist():
        if os.path.splitext(file)[0].split('/')[-1]==str(item[1][1]):
            try:
                h2=tlsh.hash(standardize_nmodl(data2.read(file)).encode("utf8"))
            except:
                blank=[]
    
    try:
        compare_mod[item]=(val,tlsh.diff(h1, h2))
    except:
        compare_mod[item]=(val,[])
    

#pprint.pprint(compare_mod)
#print(len(compare_mod))

diff_mod={}
for item,val in tqdm.tqdm(compare_mod.items()):
    a=item[0][0] #return the model ID
    data=zipfile.ZipFile("/Users/YUQIAO/Desktop/Projects/metadata/zips/"+str(int(a))+".zip")
    for file in data.namelist():
        if os.path.splitext(file)[0].split('/')[-1]==str(item[0][1]):
            try:
                standardized_code1=standardize_nmodl(data.read(file)).split("\n")
            except:
                blank=[]
            
    b=item[1][0] #return the model ID
    data2=zipfile.ZipFile("/Users/YUQIAO/Desktop/Projects/metadata/zips/"+str(int(b))+".zip")
    for file in data2.namelist():
        if os.path.splitext(file)[0].split('/')[-1]==str(item[1][1]):
            try:
                standardized_code2=standardize_nmodl(data2.read(file)).split("\n")
            except:
                blank=[]
            
    i = 0
    y=[]
  
    for line1, line2 in zip(standardized_code1,standardized_code2) :
        i += 1
      
        if line1 != line2:  
                
            y.append("Line "+str(i)+":"+"File 1:"+line1+"             File 2:"+line2)

    diff_mod[item]=(val,y)



with open('nlp_tlsh_mod_preprocessed3.csv', 'w') as f:
    for key in diff_mod.keys():
        f.write("%s,%s\n"%(key,diff_mod[key]))  
