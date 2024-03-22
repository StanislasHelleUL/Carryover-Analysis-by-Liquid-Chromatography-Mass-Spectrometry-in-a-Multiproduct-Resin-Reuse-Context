# -*- coding: utf-8 -*-
"""
@author: stanislas helle
"""

def extract_mass_time(file, msms_min_int = 0):
    dict_output=dict()
    lines = file.read().splitlines()
    for line_nb, line_str in enumerate(lines):
        if line_str == 'BEGIN IONS':
            mass_str = lines[line_nb+1].replace('PEPMASS=','').strip()
            mass = float(mass_str)
        elif 'RTINSECONDS=' in line_str:
            msms_list = []
            rt_str = line_str.replace('RTINSECONDS=', '').strip()
            rt = float(rt_str)
            for line_nb2, line_str2 in enumerate(lines[line_nb+1:]):
                if line_str2 != 'END IONS':
                    msms_param = line_str2.split('\t')
                    msms_mass = float(msms_param[0])
                    msms_int = float(msms_param[1])
                    if msms_int > msms_min_int:
                        msms_list.append(msms_mass)
                else:
                    break                                         
        elif line_str == 'END IONS':
            dict_output[f'{mass}'] = (mass,rt,msms_list)
    return dict_output

def round_floats(value):
    if isinstance(value, float):
        return round(value, 2)
    elif isinstance(value, list):
        return [round(num, 2) for num in value]
    else:
        return value

def round_dict_values(dictionary):
    return {
        key: tuple(round_floats(value) for value in values)
        for key, values in dictionary.items()
    }
        
def refine_dict(dict1, dict2, dict3):
    refined_dict = dict()
    dict1r = round_dict_values(dict1)

    dict2r = round_dict_values(dict2)

    dict3r = round_dict_values(dict3)

    for key1 in dict1r: 
        value1 = dict1r[key1]
        rounded_mass1 = value1[0]
        rt1= value1[1]
        msms_list1 = value1[2]
        for key2 in dict2r: 
            value2 = dict2r[key2]
            if rounded_mass1 in value2:
                rt2 = value2[1]
                msms_list2 = value2[2]
                for key3 in dict3r:
                    value3 = dict3r[key3]
                    if rounded_mass1 in value3:
                        rt3 = value3[1]
                        msms_list3 = value3[2]
                        av_rt = (rt1 + rt2 +rt3)/3
                        squared_diff_rt = [(rt1 - av_rt)**2, (rt2 - av_rt)**2, (rt3 - av_rt)**2]
                        mean_squared_diff_rt = sum(squared_diff_rt)/3
                        stdev_rt = mean_squared_diff_rt**0.5
                        av_rt = round(av_rt, 3)
                        stdev_rt = round(stdev_rt, 3)
                        msms_refined = list(set(msms_list1).intersection(msms_list2, msms_list3))
                        msms_refined.sort()
                        av_key = (float(key1) + float(key2) + float(key3))/3.
                        av_key = round(av_key, 7)
                        squared_diff_key = [
                            (float(key1) - av_key)**2, 
                            (float(key2) - av_key)**2, 
                            (float(key3) - av_key)**2]
                        mean_squared_diff_key = sum(squared_diff_key)/3
                        stdev_key = mean_squared_diff_key**0.5
                        stdev_key = round(stdev_key, 7)
                        #print(av_key, "+-", stdev_key, " :\t", key1, "\t", key2, "\t", key3)
                        refined_dict[str(av_key)] = (av_key, stdev_key, av_rt, stdev_rt, msms_refined)
    return refined_dict

def create_probes(refined_dictA, refined_dictB, limit_percent = 50):
    probeA = dict()
    probeB = dict()
    common = dict()
    for keyA in refined_dictA:
        massA = refined_dictA[keyA][0]
        massA_stdev = refined_dictA[keyA][1] 
        massA_up = massA + massA_stdev*10
        massA_down = massA - massA_stdev*10
        rtA = refined_dictA[keyA][2]
        rtA_stdev = refined_dictA[keyA][3]
        rtA_up = rtA + rtA_stdev*2
        rtA_down = rtA - rtA_stdev*2        
        msms_listA = refined_dictA[keyA][4]
        for keyB in refined_dictB:
            massB = refined_dictB[keyB][0]
            massB_stdev = refined_dictB[keyB][1]
            massB_up = massB +  massB_stdev*2
            massB_down = massB - massB_stdev*2
            rtB = refined_dictB[keyB][2]
            rtB_stdev = refined_dictB[keyB][3] 
            rtB_up = rtB + rtB_stdev*2
            rtB_down = rtB - rtB_stdev*2
            msms_listB = refined_dictB[keyB][4]
            if massA_up >= massB_down and massB_up >= massA_down:
               # print(f'{massA_up} >= {massB_down} and {massB_up} >= {massA_down}')
               # print(f'm/z: {massA}+-{massA_stdev*10} similar to {massB}+-{massB_stdev*10}')
                if rtA_up >= rtB_down or rtB_up >= rtA_down:
                   # print(f'RT: {rtA} similar to {rtB}')
                    len_listA = len(msms_listA)
                    len_listB = len(msms_listB)
                    intersection = set(msms_listA) & set(msms_listB)
                    percentage = (len(intersection) / len_listA *100 if len_listA < len_listB \
                                  else len(intersection) / len_listB) * 100    
                    if percentage >= limit_percent:
                     #   print(f'{intersection} are common to A and B')
                        common[keyB]=(massB, massB_stdev, rtB, rtB_stdev, list(intersection))
                    else: probeA[keyA] = (massA, massA_stdev, rtA, rtA_stdev, msms_listA)
                else: probeA[keyA] = (massA, massA_stdev, rtA, rtA_stdev, msms_listA)
            else:

                probeA[keyA] = (massA, massA_stdev, rtA, rtA_stdev, msms_listA)
    for keyB in refined_dictB:
        massB = refined_dictB[keyB][0]
        massB_stdev = refined_dictB[keyB][1]
        rtB = refined_dictB[keyB][2]
        rtB_stdev = refined_dictB[keyB][3]
        msms_listB = refined_dictB[keyB][4] 
        
        if keyB not in common:
            probeB[keyB] = (massB, massB_stdev, rtB, rtB_stdev, msms_listB)
    
    return (probeA, probeB, common)        

def find_contaminant(probe, sample_dict, limit_percent = 50):
    contaminant = dict()
    for keyS in sample_dict:
        massS = sample_dict[keyS][0]
        rtS = sample_dict[keyS][1]   
        msms_listS = sample_dict[keyS][2]
        for keyP in probe:
            massP = probe[keyP][0]
            stdev_massP = probe[keyP][1]
            massP_up = massP + 2*stdev_massP
            massP_down = massP - 2*stdev_massP
            rtP = probe[keyP][2]
            stdev_rtP = probe[keyP][3]
            rtP_up = rtP + 2*stdev_rtP
            rtP_down = rtP - 2*stdev_rtP
            msms_listP = probe[keyP][4]
            if massP_up > massS > massP_down:
                contaminant[f'{keyS}']=(massS,rtS,msms_listS,"N","N")
                if rtP_up > rtS > rtP_down:
                    contaminant[f'{keyS}']=(massS,rtS,msms_listS,"Y","N")
                    
                    len_listP = len(msms_listP)
                    len_listS = len(msms_listS)
                    intersection = set(msms_listP) & set(msms_listS)
                    percentage = (len(intersection) / len_listP *100 if len_listP < len_listS \
                                  else len(intersection) / len_listS) * 100    
                    if percentage >= limit_percent:
                        contaminant[f'{keyS}']=(massS,rtS,msms_listS,"Y","Y")

    return contaminant