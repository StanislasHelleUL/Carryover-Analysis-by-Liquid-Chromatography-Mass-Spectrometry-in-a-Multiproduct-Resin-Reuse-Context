# -*- coding: utf-8 -*-
"""
@author: stanislas helle
"""

import mprr_4
import os

#find the directory where the program is
my_dir = os.getcwd()

#create dict for stdA
with open(f'{my_dir}\\input\\std_A\\20230526_Pf-10-CHM.mgf','r') as fileA1:
    dictA1 = mprr_4.extract_mass_time(fileA1)
del fileA1
print('data from fileA1 extracted')
    
with open(f'{my_dir}\\input\\std_A\\20230526_Pf15-CHM.mgf','r') as fileA2:
    dictA2 = mprr_4.extract_mass_time(fileA2)
del fileA2
print('data from fileA2 extracted')
    

with open(f'{my_dir}\\input\\std_A\\20230526_Pf-Std-CHM.mgf','r') as fileA3:
    dictA3 = mprr_4.extract_mass_time(fileA3)
del fileA3
print('data from fileA3 extracted')

refined_dictA = mprr_4.refine_dict(dictA1, dictA2, dictA3)
del dictA1; del dictA2; del dictA3
print('dictA created')


#create dict for stdB
with open(f'{my_dir}\\input\\std_B\\20230526_EL_Std.mgf','r') as fileB1:
    dictB1 = mprr_4.extract_mass_time(fileB1)
del fileB1
print('data from fileB1 extracted')
    
with open(f'{my_dir}\\input\\std_B\\20230526_EL-10-CHM-2.mgf','r') as fileB2:
    dictB2 = mprr_4.extract_mass_time(fileB2)
del fileB2
print('data from fileB2 extracted')

with open(f'{my_dir}\\input\\std_B\\20230526_EL-15-CHM-2.mgf','r') as fileB3:
    dictB3 = mprr_4.extract_mass_time(fileB3)
del fileB3
print('data from fileB3 extracted')


refined_dictB = mprr_4.refine_dict(dictB1, dictB2, dictB3)
del dictB1; del dictB2; del dictB3
print('dictB created')

#create probes and the list of common peaks between A and B
probeA, probeB, common = mprr_4.create_probes(refined_dictA, refined_dictB)
del refined_dictA
del refined_dictB

with open(f'{my_dir}\\output\\probeA.txt', 'w') as file:
    file.write(str(probeA))
del file

print('probeA created')
with open(f'{my_dir}\\output\\probeB.txt', 'w') as file:
    file.write(str(probeB))
del file

print('probeB created')

with open(f'{my_dir}\\output\\common.txt', 'w') as file:
    file.write(str(common))

del file
del common
print('common created')

#test samples against probe A
for filename in os.listdir(f'{my_dir}\\test_file\\against_probeA'):
    with open(f'{my_dir}\\test_file\\against_probeA\\{filename}', 'r') as test_file:
        test_dict = mprr_4.round_dict_values(mprr_4.extract_mass_time(test_file))
    del test_file
    name = filename.replace(".mgf","")
    print(f'{name} extracted')
    contaminant_dict = mprr_4.find_contaminant(probeA, test_dict)
    with open(f'{my_dir}\\output_contaminant\\{name}.txt', 'w') as contaminant_file:
        line = 1
        for key in contaminant_dict:
            yn_rt = contaminant_dict[f'{key}'][3]
            yn_msms = contaminant_dict[f'{key}'][4]
            contaminant_file.write(f'{line}\t{key}\tRT:{yn_rt}\tMSMS:{yn_msms}\n')
            line += 1
            del yn_rt
            del yn_msms
    print(f'{name} contaminant file created')
    #table output for samples against probe A
    with open(f'{my_dir}\\output_table\\{name}.txt', 'w') as contaminant_file:
        contaminant_file.write('peak\tm/z\n')
        line = 1
        for key in contaminant_dict:
            yn_rt = contaminant_dict[f'{key}'][3]
            yn_msms = contaminant_dict[f'{key}'][4]
            if yn_rt == 'Y' and yn_msms == 'Y':
                contaminant_file.write(f'{line}\t{key}\n')
                line += 1
            del yn_rt
            del yn_msms
    print(f'{name} table created')
    
    
del probeA
del name    
del contaminant_file  

#test samples against probe B
for filename in os.listdir(f'{my_dir}\\test_file\\against_probeB'):
    with open(f'{my_dir}\\test_file\\against_probeB\\{filename}', 'r') as test_file:
        test_dict = mprr_4.round_dict_values(mprr_4.extract_mass_time(test_file))
    del test_file
    name = filename.replace(".mgf","")
    print(f'{name} extracted')
    contaminant_dict = mprr_4.find_contaminant(probeB, test_dict)
    del test_dict
    with open(f'{my_dir}\\output_contaminant\\{name}.txt', 'w') as contaminant_file:
        line = 1
        for key in contaminant_dict:
            yn_rt = contaminant_dict[f'{key}'][3]
            yn_msms = contaminant_dict[f'{key}'][4]
            contaminant_file.write(f'{line}\t{key}\tRT:{yn_rt}\tMSMS:{yn_msms}\n')
            line += 1
            del yn_rt
            del yn_msms
    print(f'{name} contaminant file created')
    #table output for samples against probe B
    with open(f'{my_dir}\\output_table\\{name}.txt', 'w') as contaminant_file:
        contaminant_file.write('peak\tm/z\n')
        line = 1
        for key in contaminant_dict:
            yn_rt = contaminant_dict[f'{key}'][3]
            yn_msms = contaminant_dict[f'{key}'][4]
            if yn_rt == 'Y' and yn_msms == 'Y':
                contaminant_file.write(f'{line}\t{key}\n')
                line += 1
            del yn_rt
            del yn_msms
    print(f'{name} table created')

del line
del contaminant_dict
del filename
del key    
del probeB 
del name    
del contaminant_file  
del(my_dir)
print("done!")