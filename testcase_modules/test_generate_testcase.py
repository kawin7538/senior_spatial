import os
from numpy import datetime_as_string
from tqdm import tqdm
import re

list_orig_case = sorted(set([i for i in os.listdir("testcase_modules/testcase_input")
                        if int(i.split('.')[0]) < 1000]), key=lambda x: int(x.split('.')[0]))

list_perm_case = sorted(set([i for i in os.listdir("testcase_modules/testcase_input")
                        if int(i.split('.')[0]) in range(1000,9000)]), key=lambda x: int(x.split('.')[0]))


def create_1000():
    # 1000 series is low mid high with low and high values nearly with mid value
    for orig_case in tqdm(list_orig_case, "generate 1000 series"):
        f_in = open(os.path.join(
            "testcase_modules/testcase_input", orig_case), "r")
        temp_data = f_in.read()
        if temp_data.find('random')!=-1:
            temp_data = temp_data.replace("random", 'random2')
        elif temp_data.find("flower")!=-1 or temp_data.find("outside")!=-1:
            temp_data = temp_data.replace("-high", '-high2').replace("-low", '-low2')
        else:
            temp_data = temp_data.replace("high", 'high2').replace("low", "low2")
        case_number = int(orig_case.split('.')[0])
        f_out = open(os.path.join(
            "testcase_modules/testcase_input", f"{1000+case_number}.in"), "w")
        f_out.write(temp_data)
        f_in.close()
        f_out.close()
        # break;


def create_2000():
    # 2000 series is low mid high with mid and high values nearly with low value
    for orig_case in tqdm(list_orig_case, "generate 2000 series"):
        f_in = open(os.path.join(
            "testcase_modules/testcase_input", orig_case), "r")
        temp_data = f_in.read()
        if temp_data.find('random')!=-1:
            temp_data = temp_data.replace("random", 'random3')
        elif temp_data.find("flower")!=-1 or temp_data.find("outside")!=-1:
            temp_data = temp_data.replace("-high", '-high3').replace("-low", '-low3')
        else:
            temp_data = temp_data.replace("high", 'high3').replace("mid", "mid2")
        case_number = int(orig_case.split('.')[0])
        f_out = open(os.path.join(
            "testcase_modules/testcase_input", f"{2000+case_number}.in"), "w")
        f_out.write(temp_data)
        f_in.close()
        f_out.close()
        # break;


def create_3000():
    # 3000 series is low mid high with mid and low values nearly with high value
    for orig_case in tqdm(list_orig_case, "generate 2000 series"):
        f_in = open(os.path.join(
            "testcase_modules/testcase_input", orig_case), "r")
        temp_data = f_in.read()
        if temp_data.find('random')!=-1:
            temp_data = temp_data.replace("random", 'random4')
        elif temp_data.find("flower")!=-1 or temp_data.find("outside")!=-1:
            temp_data = temp_data.replace("-high", '-high4').replace("-low", '-low4')
        else:
            temp_data = temp_data.replace("low", 'low3').replace("mid", "mid3")
        case_number = int(orig_case.split('.')[0])
        f_out = open(os.path.join(
            "testcase_modules/testcase_input", f"{3000+case_number}.in"), "w")
        f_out.write(temp_data)
        f_in.close()
        f_out.close()
        # break;

def del_perm_case():
    for perm_case in tqdm(list_perm_case,desc="Delete Perm Case"):
        if os.path.isfile(os.path.join("testcase_modules/testcase_input", perm_case)):
            os.remove(os.path.join("testcase_modules/testcase_input", perm_case))

if __name__ == '__main__':
    print("List of all original testcase")
    print(list_orig_case)
    print(list_perm_case)
    
    # create_1000()
    # create_2000()
    # create_3000()

    del_perm_case()