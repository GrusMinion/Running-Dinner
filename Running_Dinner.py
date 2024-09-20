# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 09:58:38 2021

@author: 884570
"""


"""
BELANGRIJKE AANTEKENINGEN
om dit script te laten werken:
    - installeer alle benodige packages (zie hieronder).
    - pas de benodigde parameters aan (zie hieronder).
    - zorg ervoor dat het input bestand in dezelfde map staat als dit script.
    - zorg dat het input bestand het juiste format heeft (zie bijgeleverd bestand).
    dit betekend o.a. dat kolom namen, werkboek namen en het format van de data
    onveranderd blijven (hoofdletter gevoelig!).
    - zorg ervoor dat de naam de het input bestand overeenkomt met de werkelijke
    naam van het excel bestand.
    - de data moet consistent zijn met elkaar: de namen/adressen die in het
    werkblad 'Bewoners' staan moeten overeenkomen met de andere werkbladen

AANNAMES
    - Dit script gaat door tot er een 'lokaal optimimum' is gevonden. Afhankelijk
    van de grootte van het probleem (= aantal deelnemers/adressen) kan dit LANG
    duren!
    - Dit script zorgt ervoor dat er aan alle HARDE EISEN wordt voldaan (zie 
    hieronder voor de lijst eisen). Indien dit niet mogelijk is op basis van
    de gegeven data zal dit script niet werken. (let op, deze eisen komen niet
    1-op-1 overeen met de werkelijke eisen).
    - 
    
HARDE EISEN
    - iedere deelnemer eet elke gang en eet elke gang op een ander adres
    - iedere deelnemer, behalve degene die zijn uitgezonderd, bereiden 1 gang
    - iedere kok is voor de te bereiden gang op zijn/haar eigen adres ingedeeld
    - het aantal gasten per gang zal nooit het maximum of minimum aantal per
    adres over/onderschreiden.
    - deelnemers bereiden de gang van hun voorkeur
    - indien een huisadres vorig jaar het hoofdgerecht heeft bereid zal het dat
    dit jaar niet doen
    

WENSEN
    - de specifiek aangegeven "paren" worden voor elke gang gezamenlijk ingedeeld
    - deelnemers zitten gedurende de avond nooit meer dan 1 keer gezamenlijk
    aan tafel (uitgezonderd "paren")
    - deelnemers eten niet samen met deelnemers waarmee ze vorig jaar hebben gegeten
    - deelnemers eten niet samen met buren
    - de man/vrouw verhouding per adres is gelijk verdeeld
"""

# zorg ervoor dat deze packages allereerst geinstalleerd zijn
import numpy as np
import pandas as pd
import random
import copy
from collections import Counter

def create_schedule(input_file, update_kpi):
    # vul de volgende parameters in
    penalty_paar_blijft_bij_elkaar = 5000
    penalty_gasten_eten_vaker_samen = 10
    penalty_vorig_jaar_ook_samen = 3
    penalty_buren_eten_samen = 2
    penalty_man_vrouw_verhouding = 1

    # indien er niet veel tijd is, verlaag het maximum aantal iteraties
    max_num_iterations = 100

    # vul de bestandsnamen in van de input/output files (let op: hoofdletter gevoelig)
    input_bestandsnaam = 'Running Dinner dataset 2022'
    output_bestandsnaam = 'Running Dinner planning 2022'


    # %%
    """
    Import data
    """
    Bewoners_df = input_file.bewoners_df
    Adressen_df = input_file.adressen_df
    Bijelkaar_df = input_file.bijelkaar_df
    Buren_df = input_file.buren_df
    Gang_vorigjaar_df = input_file.gang_vorigjaar_df
    Tafelgenoot_vorigjaar_df = input_file.tafelgenoot_vorigjaar_df

    Tafelgenoot_vorigjaar_series1 = {(indv1, indv2) for indv1, indv2 in zip(Tafelgenoot_vorigjaar_df['Bewoner1'], Tafelgenoot_vorigjaar_df['Bewoner2'])}
    Tafelgenoot_vorigjaar_series2 = {(indv2, indv1) for indv1, indv2 in zip(Tafelgenoot_vorigjaar_df['Bewoner1'], Tafelgenoot_vorigjaar_df['Bewoner2'])}

    all_participants = Bewoners_df['Bewoner'].values.tolist()

    # edit "Bijelkaar_df" to copy the dataframe and switch the columns, then append
    # this switched dataframe.This way, whether to individuals should be together
    # is indicated from both perspectives
    cols = Bijelkaar_df.columns.tolist()
    temp = copy.deepcopy(Bijelkaar_df)
    cols = cols[-1:] + cols[:-1]
    temp.columns = cols
    Bijelkaar_df = pd.concat([Bijelkaar_df, temp], ignore_index=True)

    # create a dictionary which for each individual gives their gender, 1 if male
    # and 0 if female
    dict_gender = {}
    for ind, name in enumerate(Bewoners_df['Bewoner']):
        val = int((Bewoners_df['Geslacht'][ind]=='m') == True)
        dict_gender[name] = val


    # %%
    """
    Different aiding functions used throughout the code
    """

    def staying_together_total(dict_more_once):
        # this penalty function calculates how many time pairs that should stay 
        # together do not stay toggether, and applies the corresponding penalty
        # if they are not together for each course
        beta = penalty_paar_blijft_bij_elkaar
        
        penalty = 0
        for indv1, indv2 in zip(Bijelkaar_df['Bewoner1'].to_list(), Bijelkaar_df['Bewoner2'].to_list()):
            if (indv1,indv2) in dict_more_once.keys():
                penalty += beta*(3 - dict_more_once[(indv1,indv2)])
            elif (indv2,indv1) in dict_more_once.keys():
                penalty += beta*(3 - dict_more_once[(indv2,indv1)])
            else:
                penalty += beta*3
            
        return penalty

    def together_dict(solution):
        # this function determines (as a dictionary) the number of times each pair
        # of persons are eating together, 
        indv_together = [tuple(sorted((pers1, pers2))) for course in solution for adrs in course \
                        for ind_pers1, pers1 in enumerate(adrs[:-1]) for pers2 in adrs[ind_pers1+1:]]
        # indv_together = [(pers1, pers2) for course in solution for adrs in course for pers1 in adrs for pers2 in adrs]
        dict_indv_together = dict(Counter(indv_together))
        dict_more_once = dict((k,v) for k,v in dict_indv_together.items() if v > 1)
        
        return dict_indv_together, sum(dict_more_once.values())-len(dict_more_once)


    def num_together_penalty(num_more_together):
        # this function calculates the penalty if people eat together more than once
        # in an evening
        beta = penalty_gasten_eten_vaker_samen

        penalty = beta * num_more_together
        return penalty

    def neighbours_together_penalty(dict_indv_together):
        # this function calculates the penalty if neighbours eat together. Note
        # that if neighbours eat together more than once, the penalty is only
        # assigned once!
        beta = penalty_buren_eten_samen
        
        # total penalty value
        penalty = 0
        
        for indv1, indv2 in zip(Buren_df['Bewoner1'].to_list(), Buren_df['Bewoner2'].to_list()):
            if (indv1, indv2) in dict_indv_together.keys():
                penalty = penalty + beta
            elif (indv2, indv1) in dict_indv_together.keys():
                penalty = penalty + beta
        return penalty

    def prevyear_together_penalty(dict_indv_together):
        # this function calculates the penalty for people how sat together last
        # year and are scheduled together again this year. Again, if people
        # are scheduled together more  than once together for an evening, the 
        # penalty is only  assigned once
        beta = penalty_vorig_jaar_ook_samen
        
        # total penalty value
        penalty = 0
        
        for indv_tuple in dict_indv_together.keys():
            if indv_tuple in Tafelgenoot_vorigjaar_series1:
                penalty += beta * dict_indv_together[indv_tuple]
            elif indv_tuple in Tafelgenoot_vorigjaar_series2:
                penalty += beta * dict_indv_together[indv_tuple]
        return penalty

    def man_vrouw_verhouding_penalty(solution):
        beta = penalty_man_vrouw_verhouding

        sum_of_values = [[sum(dict_gender[indv] for indv in sublist) for sublist in course] for course in solution]    
        
        penalty = sum([abs(males - round(num_guests/2))*beta for sublist1, sublist2 \
                    in zip(sum_of_values, num_guests_dinners) for males, num_guests in \
                    zip(sublist1, sublist2)])

        return penalty


    def calc_objective(solution):

        dict_indv_together, num_more_together = together_dict(solution)
        penalty1 = staying_together_total(dict_indv_together)
        penalty2 = num_together_penalty(num_more_together)
        penalty3 = neighbours_together_penalty(dict_indv_together)
        penalty4 = prevyear_together_penalty(dict_indv_together)
        penalty5 = man_vrouw_verhouding_penalty(solution)
        penalty = penalty1 + penalty2 + penalty3 + penalty4 + penalty5
        return penalty

    # %%
    """
    Create first solution - constructive heuristic
    """

    # first create a list of all adresses
    adresses = Adressen_df.index.values.tolist()

    # determine which of these adresses won't cook any meal, and remove them from the list
    adresses_cook = adresses[:]

    # iterate over all 'bewoners'
    for idx in range(len(Bewoners_df)):
        # if we find someone who doesn't have to cook...
        if Bewoners_df['Kookt niet'][idx] == 1:
            # determine it's address and remove it from the list of addresses that
            # have to cook
            homeadrs = Bewoners_df['Huisadres'][idx]
            if homeadrs in adresses_cook: adresses_cook.remove(Bewoners_df['Huisadres'][idx])

    # create list of courses that are available
    courses = ['Voor','Hoofd','Na']

    # create a variable in which we save which address is responsible for which course
    address_course = [[] for i in range(len(courses))]

    # variable to keep track of the minimum capacity of each address. Same for max
    # cap. Try to find an equal amount of cap for each course.
    min_cap_address = np.zeros(len(courses))
    max_cap_address = np.zeros(len(courses))

    # iterate over all adresses and assign them to a course; start with all those
    # addresses that gave a preference
    address_to_assign = adresses_cook[:]
    for idx in range(len(Adressen_df)):
        course_id_list  = [0,1,2]
        # iterate over the different courses
        for courseidx,course in enumerate(courses):
            # if this address has a preference for this specific course
            if Adressen_df['Voorkeur gang'][idx] == course:
                # assign it to this course
                course_id_list.remove(courseidx)
                chosen_idx = random.choice(course_id_list)
                
                
                chosen_idx = courseidx
                
                
                address_course[chosen_idx].append(Adressen_df.index[idx])
                # and remove it from 'address_to_assign'
                address_to_assign.remove(Adressen_df.index[idx])
                min_cap_address[chosen_idx] += Adressen_df['Min groepsgrootte'][idx]
                max_cap_address[chosen_idx] += Adressen_df['Max groepsgrootte'][idx]
                
    # try to also take into account the addresses that created a 'main course'
    # the previous year. Iterate over all addresses to assign, determine if they
    # cooked a main course previous year and assign them to the course with the
    # lowest maximum capacity (excluding the main course).
    # careful!! We only want to do this, if it does not effect the feasibilty of
    # of the problem. If we get too few max capacity at a specific course, this
    # has to be changed!
    course_not_main = [0,2]
    address_to_iterate = copy.deepcopy(address_to_assign)
    for adr in address_to_iterate:
        if adr in set(Gang_vorigjaar_df.index):
            if Gang_vorigjaar_df['Gang'][adr] == courses[1]:
                # determine for which course this address should cook
                course_idx = course_not_main[max_cap_address[course_not_main].argmin()]
                
                # course_idx = 1
                
                
                # add this address to this course and remove it from address to assign
                address_course[course_idx].append(adr)
                address_to_assign.remove(adr)
                
                # update the minimum and maximum (total) capacity for each course
                min_cap_address[course_idx] += Adressen_df['Min groepsgrootte'][adr]
                max_cap_address[course_idx] += Adressen_df['Max groepsgrootte'][adr]





    # iterate over all addresses that still need to be assigned to a course. Assign
    # the address to the course that still has the lowest capacity. If they are
    # tied for lowest, randomly choose one course
    for adr in address_to_assign:
        # determine for which course this address should cook
        course_idx = max_cap_address.argmin()
        
        # assign the address to this course
        address_course[course_idx].append(adr)
        
        # update min and max capacity per course
        min_cap_address[course_idx] += Adressen_df['Min groepsgrootte'][adr]
        max_cap_address[course_idx] += Adressen_df['Max groepsgrootte'][adr]

    # The variable with the final solution: for each course and each address a list
    # of persons that eat that course at that address
    course_address_person = [[[] for i in range(len(address_course[j]))] for j in range(len(courses))]

    # first assign all individuals that live at the address. Then randomly select 
    # individuals that are not yet assigned for that course to an address. Start with
    # the address that has not yet the minimum amount of guests, and only add if 
    # the amount does not exceed the maximum capacity.
    for course_idx in range(len(courses)):
        # list of all individuals. They have to be added to an address for each
        # course again.
        individuals_to_assign = Bewoners_df['Bewoner'].values.tolist()
        # iterate over all the addresses that are assigned to this course
        for adrs_idx, address in enumerate(address_course[course_idx]):
            # assign hosts to their own addresses. First find all the indices
            # of the hosts in the dataframe 'bewoners_df'. This way we know which
            # indivuals live at the addresses that have to cook.
            person_idx = [i for i, item in enumerate(Bewoners_df['Huisadres'].values.tolist()) \
                        if item == address]
                
            # assign each of these individuals to that course on that address.
            cooks_at_address = Bewoners_df['Bewoner'][person_idx].values.tolist()
            course_address_person[course_idx][adrs_idx] = cooks_at_address
            
            # now remove these cooks from the list of individuals that have to be
            # assigned
            for individual in cooks_at_address:
                individuals_to_assign.remove(individual)
            
        # now assign the remaining individuals. First select any address that
        # does not have the minimum amount of guests (if any).
        
        # continue as long as there are individuals to assign
        while individuals_to_assign:
            # make a list of all addresses that do not yet have the minimum amount
            # of guests assigned
            address_not_min = []
            
            # iterate over all addresses that have to cook this course
            for adrs_idx, address in enumerate(address_course[course_idx]):
                min_address = Adressen_df['Min groepsgrootte'][address]
                # if this address does not meet the minimum, add it to the list
                if len(course_address_person[course_idx][adrs_idx]) < min_address:
                    address_not_min.append(address)
            # if not all addresses have at least the minimum amount, pick one at
            # at random
            if address_not_min:
                address_to_add = random.choice(address_not_min)
            else:
                # else determine which address does not yet have the maximum amount
                address_not_max = []
                
                # first determine the minimum number of people at an adress
                min_indv_assigned = min(len(course_address_person[course_idx][adrs_idx])\
                        for adrs_idx, address in enumerate(address_course[course_idx])\
                            if len(course_address_person[course_idx][adrs_idx]) < Adressen_df['Max groepsgrootte'][address])
                for adrs_idx, address in enumerate(address_course[course_idx]):
                    max_address = Adressen_df['Max groepsgrootte'][address]
                    # if this address does not yet have the maximum amount, add it
                    # to the list
                    if (len(course_address_person[course_idx][adrs_idx]) < max_address)\
                        and (len(course_address_person[course_idx][adrs_idx]) == min_indv_assigned):
                        address_not_max.append(address)
                        
                # pick one address from this list 
                address_to_add = random.choice(address_not_max)
            
            # find the corresponding index of this address
            idx_address = [i for i, address in enumerate(address_course[course_idx]) if address == address_to_add][0]
            
            # pick the first individual that is not yet assigned, and add it to 
            # this course/address
            course_address_person[course_idx][idx_address].append(individuals_to_assign[0])
            individuals_to_assign.remove(individuals_to_assign[0])
            
    # Create a nested list with the number of individuals per address per course, 
    # that we can use to calculate whether male/female ratio is in balance
    num_guests_dinners = [[len(household) for household in course] for course in course_address_person]

    #%%
    """
    Create best solution - improving search heuristic
    """


    # while loop iteration boolean
    improve = True

    # current solution (given by the constructive heuristic)
    current_sol = copy.deepcopy(course_address_person)
    current_num_together_dict, num_together = together_dict(current_sol)

    # corresponding objective value and matrix/dataframe indicating how many time
    # each individual will be eating together with another individual
    current_obj = calc_objective(current_sol)

    # best solution so far is a direct copy of be current solution, since we just
    # start
    best_obj = current_obj

    # number of people per household
    num_per_household = Bewoners_df['Huisadres'].value_counts()

    iter_count = 0

    # keys = [(course, adrs) for courseid, course in enumerate(courses) for adrsid, adrs_sol in enumerate(current_sol[courseid]) for adrs in Bewoners_df['Huisadres'][Bewoners_df['Bewoner'] == adrs_sol[0]]]

    # values = (adrs for course in current_sol for adrs in course)

    # # values = (dinner_table[Bewoners_df['Huisadres'].index([Bewoners_df['Bewoner'] == dinner_table[0]]).value_counts():] for course in current_sol for dinner_table in course)

    # dict_sol = dict(zip(keys, values))

    # exchange_tuples = [(key1, key2, indv1, indv2) for key1 in dict_sol.keys() for key2 in dict_sol.keys() for indv1 in dict_sol.get(key1) for indv2 in dict_sol.get(key2)]

    best_improvement = True
    first_improvement = not best_improvement

    cours_ind_list = [0,1,2]
    while improve:

        continue_nested = True
        # should make this step one that doens't require to calculate the amount of 
        # people per household all the time:
        # Bewoners_df['Huisadres'].values.tolist().count(adrs2)
        
        # iterate over all courses
        random.shuffle(cours_ind_list)
        for course_id in cours_ind_list:
            # iterate over all addresses that have to cook this course. Start the
            # iteration at the first address, end at the second-last address.
            for adrs_idx1, adrs1 in enumerate(address_course[course_id][0:len(address_course[course_id])-1]):
                # determine how many coocks this household has. These (amount of) individuals
                # will not be switched in the current solution.
                num_cooks1 = num_per_household[adrs1]
                
                # iterate over all OTHER individuals (not the cooks) at this household
                # for this specific course
                for indv_idx1, indv1 in enumerate(current_sol[course_id][adrs_idx1][num_cooks1:]):
                    indv_idx1 += num_cooks1
                    # now in the same way we select a second address (starting one after
                    # the current address) and determine an individual from that household
                    for adrs_idx2, adrs2 in enumerate(address_course[course_id][adrs_idx1+1:]):
                        adrs_idx2 += adrs_idx1 + 1
                        num_cooks2 = num_per_household[adrs2]
                        for indv_idx2, indv2 in enumerate(current_sol[course_id][adrs_idx2][num_cooks2:]):
                            indv_idx2 += num_cooks2
                            # swap the two individuals indv1 and indv2. Both individuals
                            # are eating at a different address, but are eating the same
                            # course. indv1 is eating at adrs1 and indv2 is eating at 
                            # adrs2.
                            current_sol[course_id][adrs_idx1][indv_idx1], current_sol[course_id][adrs_idx2][indv_idx2] = \
                                current_sol[course_id][adrs_idx2][indv_idx2], current_sol[course_id][adrs_idx1][indv_idx1]

                            neighbour_obj = calc_objective(current_sol)

                            # if the objective value decreased (better than the best so far)
                            # we update our new best objective and corresponding solution
                            
                            if neighbour_obj < best_obj and best_improvement:
                                swap = copy.deepcopy([course_id,adrs_idx1,indv_idx1,adrs_idx2,indv_idx2])
                                best_obj = neighbour_obj
                                # print(best_obj)
                            elif neighbour_obj < current_obj and first_improvement:
                                current_obj = neighbour_obj
                                continue_nested = False
                                print(current_obj)
                                break
                            if best_improvement:
                                current_sol[course_id][adrs_idx1][indv_idx1], current_sol[course_id][adrs_idx2][indv_idx2] = \
                                current_sol[course_id][adrs_idx2][indv_idx2], current_sol[course_id][adrs_idx1][indv_idx1]
                            if not continue_nested and first_improvement:
                                break
                        if not continue_nested and first_improvement:
                            break
                    if not continue_nested and first_improvement:
                        break
                if not continue_nested and first_improvement:
                    break
            if not continue_nested and first_improvement:
                break

        # if after iterations, the best solution found (of neighbours) is an
        # improvement over the current solution, update the current solution
        if best_obj < current_obj and best_improvement:
            current_obj = best_obj
            course_id,adrs_idx1,indv_idx1,adrs_idx2,indv_idx2 = swap
            current_sol[course_id][adrs_idx1][indv_idx1], current_sol[course_id][adrs_idx2][indv_idx2] = \
            current_sol[course_id][adrs_idx2][indv_idx2], current_sol[course_id][adrs_idx1][indv_idx1]
            print(best_obj)
            update_kpi(current_obj)
        elif first_improvement and not continue_nested:
            update_kpi(current_obj)
            print(current_obj)
        else:
            improve = False
        iter_count += 1
        
        if iter_count > max_num_iterations:
            improve = False
            break
        
    # lp = LineProfiler()
    # lp_wrapper = lp(calc_objective)
    # lp_wrapper(current_sol)
    # lp.print_stats()



    # %%
    solution_df = Bewoners_df.drop('Kookt niet', axis=1).copy()

    sol_data = [['' for j in range(len(solution_df))] for i in range(len(courses))]
    kookt =['' for j in range(len(solution_df))]
    aantal =['' for j in range(len(solution_df))]

    for course_id in range(len(current_sol)):
        for adrs_id, adrs in enumerate(address_course[course_id]):
            for indv in current_sol[course_id][adrs_id]:
                
                indv_ind = solution_df.index[solution_df['Bewoner'] == indv][0]
                sol_data[course_id][indv_ind] = adrs
                
                if solution_df['Huisadres'][indv_ind] == adrs:
                    kookt[indv_ind] = courses[course_id]
                    aantal[indv_ind] = len(current_sol[course_id][adrs_id])

    for course_id, course in enumerate(courses):
        solution_df[course] = sol_data[course_id]
        
    solution_df['kookt'] = kookt
    solution_df['aantal'] = aantal

    return solution_df
    # solution_df.to_excel(output_bestandsnaam + '.xlsx', index=False)

