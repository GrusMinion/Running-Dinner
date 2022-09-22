import pandas as pd
import numpy as np
import math


class DataTransformer():
    def __init__(self, oplossing_df, bewoners_df, adressen_df, bijelkaar_df, 
                 buren_df, gang_vorigjaar_df, tafelgenoot_vorigjaar_df, gangen = ['Voor','Hoofd','Na']):
        self.oplossing_df = oplossing_df
        self.bewoners_df = bewoners_df
        self.adressen_df = adressen_df
        self.bijelkaar_df = bijelkaar_df
        self.buren_df = buren_df
        self.gang_vorigjaar_df = gang_vorigjaar_df
        self.tafelgenoot_vorigjaar_df = tafelgenoot_vorigjaar_df
        self.gangen = gangen
        
        self.adressen_df = self.adressen_df.set_index('Huisadres')
        self.gang_vorigjaar_df = self.gang_vorigjaar_df.set_index('Huisadres')
        
        self.eet_niet_data = None
        self.penalty0()
        
        self.kookt_niet_foutief = None
        self.kookt_wel_foutief = None
        self.penalty1()
        
        self.mis_eigen_adres = None
        self.penalty2()

        self.adrs_te_veel_deelnemers = None
        self.adrs_te_weinig_deelnemers = None
        self.penalty3()
        
        self.deelnemers_niet_samen = None
        self.penalty4()

        self.deelnemers_samen = None
        self.huishoudens_samen = None
        self.penalty5()

        self.adres_wederom_hoofd = None
        self.penalty6()

        self.kookt_niet_voorkeur = None
        self.penalty7()

        self.buren_samen = None
        self.penalty8()

        self.deelnemers_wederom_samen = None
        self.penalty9()

        dict_KPI = {
            'Aantal deelnemers dat voor EEN gang niet is ingedeeld' : len(self.eet_niet_data),
            'Aantal huishoudens dat foutief NIET is ingedeeld om te koken' : len(self.kookt_niet_foutief),
            'Aantal huishoudens dat foutief WEL is ingedeeld om te koken' : len(self.kookt_wel_foutief),
            'Aantal deelnemers dat als kok niet is ingedeeld op het eigen adres' : len(self.mis_eigen_adres),
            'Aantal huishoudens met te veel gasten' : len(self.adrs_te_veel_deelnemers),
            'Aantal huishoudens met te weinig gasten' : len(self.adrs_te_weinig_deelnemers),
            'Aantal keer dat koppels niet samen eten' : len(self.deelnemers_niet_samen),
            'Aantal keer dat huishoudens te vaak samen eten' : sum([sublist[-1] for sublist in self.huishoudens_samen]),
            'Aantal keer dat deelnemers te vaak samen eten' : sum([sublist[-1] for sublist in self.deelnemers_samen]),
            'Aantal huishoudens dat wederom een hoofdgerecht moet bereiden' : len(self.adres_wederom_hoofd),
            'Aantal huishoudens dat niet het voorkeursgerecht krijgt toegewezen' : len(self.kookt_niet_voorkeur),
            'Aantal keer dat buren samen eten' : len(self.buren_samen),
            'Aantal keer dat deelnemers wederom als vorgaand jaar samen eten': len(self.deelnemers_wederom_samen),
        }
        self.table_KPI = pd.DataFrame.from_dict(dict_KPI, orient='index')


        # self.column_names = ['Aantal deelnemers dat voor EEN gang niet is ingedeeld',
        #                 'Aantal huishoudens dat foutief NIET is ingedeeld om te koken',
        #                 'Aantal huishoudens dat foutief WEL is ingedeeld om te koken',
        #                 'Aantal deelnemers dat als kok niet is ingedeeld op het eigen adres',
        #                 'Aantal huishoudens met te veel gasten',
        #                 'Aantal huishoudens met te weinig gasten',
        #                 'Aantal keer dat koppels niet samen eten',
        #                 'Aantal keer dat huishoudens te vaak samen eten',
        #                 'Aantal keer dat deelnemers te vaak samen eten',
        #                 'Aantal huishoudens dat wederom een hoofdgerecht moet bereiden',
        #                 'Aantal huishoudens dat niet het voorkeursgerecht krijgt toegewezen',
        #                 'Aantal keer dat buren samen eten',
        #                 'Aantal keer dat deelnemers wederom als vorgaand jaar samen eten']
        
        # self.output_df = pd.DataFrame(columns = self.column_names)
        
        # self.output_data = [len(self.eet_niet_data), len(self.kookt_niet_foutief), len(self.kookt_wel_foutief),
        #                len(self.mis_eigen_adres), len(self.adrs_te_veel_deelnemers), len(self.adrs_te_weinig_deelnemers),
        #                len(self.deelnemers_niet_samen), sum([sublist[-1] for sublist in self.huishoudens_samen]),
        #                sum([sublist[-1] for sublist in self.deelnemers_samen]), len(self.adres_wederom_hoofd),
        #                len(self.kookt_niet_voorkeur), len(self.buren_samen), len(self.deelnemers_wederom_samen)]
        # self.output_df.loc[:] = self.output_data
        # self.table_KPI = self.output_df.transpose(copy = True)
        
        
    def penalty0(self):
        self.eet_niet_data = []
        for deelnemer_id, deelnemer in enumerate(self.bewoners_df['Bewoner']):
            for gang_id, gang in enumerate(self.gangen):
                if self.oplossing_df[gang][deelnemer_id] in self.bewoners_df['Huisadres'].values.tolist():
                    continue
                else:
                    self.eet_niet_data.append([deelnemer, gang])
        
    def penalty1(self):
        self.kookt_niet_foutief = []
        self.kookt_wel_foutief = []
        
        for deelnemer_id, deelnemer in enumerate(self.bewoners_df['Bewoner']):
            adrs = self.bewoners_df['Huisadres'][self.bewoners_df['Bewoner'] == deelnemer].values[0]
            indx_oplossing =  np.where((self.oplossing_df['Bewoner']==deelnemer).values)[0][0]
            if self.oplossing_df['kookt'][indx_oplossing] in self.gangen:
                if math.isnan(self.adressen_df['Min groepsgrootte'][adrs]):
                    self.kookt_wel_foutief.append([deelnemer, adrs, 'kookt wel foutief'])
                else:
                    continue
            else:
                if math.isnan(self.adressen_df['Min groepsgrootte'][adrs]):
                    continue
                else:
                    self.kookt_niet_foutief.append([deelnemer, adrs, 'kookt niet foutief'])
                    
    def penalty2(self):
        self.mis_eigen_adres = []
        for deelnemer_id, deelnemer in enumerate(self.bewoners_df['Bewoner']):
            indx_oplossing =  np.where((self.oplossing_df['Bewoner']==deelnemer).values)[0][0]
            gang = self.oplossing_df['kookt'][indx_oplossing]
            if gang in self.gangen:
                indx_huisadres = np.where((self.bewoners_df['Bewoner']==deelnemer).values)[0][0]
                if self.bewoners_df['Huisadres'][indx_huisadres] == self.oplossing_df[gang][indx_oplossing]:
                    continue
                else:
                    self.mis_eigen_adres.append([deelnemer,gang])

    def penalty3(self):
        self.adrs_te_veel_deelnemers = []
        self.adrs_te_weinig_deelnemers = []
        
        for adrs in self.adressen_df.index:
            num_guests = 0
            for gang in self.gangen:
                num_guests += len(self.oplossing_df[gang][self.oplossing_df[gang] == adrs])
            if self.adressen_df['Max groepsgrootte'][adrs] < num_guests:
                self.adrs_te_veel_deelnemers.append([adrs,num_guests])
            elif self.adressen_df['Min groepsgrootte'][adrs] > num_guests:
                self.adrs_te_weinig_deelnemers.append([adrs,num_guests])

    def penalty4(self):
        self.deelnemers_niet_samen = []

        for idx, deelnemer1 in enumerate(self.bijelkaar_df['Bewoner1']):
            deelnemer2 = self.bijelkaar_df['Bewoner2'][idx]
            for gang in self.gangen:
                adrs_deelnemer1 = self.oplossing_df[gang][self.oplossing_df['Bewoner'] == deelnemer1].values[0]
                adrs_deelnemer2 = self.oplossing_df[gang][self.oplossing_df['Bewoner'] == deelnemer2].values[0]
                if adrs_deelnemer1 != adrs_deelnemer2:
                    # in dat geval eten deze deelnemers niet samen, terwijl dat wel zou moeten.
                    self.deelnemers_niet_samen.append([deelnemer1, deelnemer2, gang])

    def penalty5(self):
        self.deelnemers_samen = []
        self.huishoudens_samen = []
        for id1 in range(len(self.oplossing_df)-1):
            for id2 in range(id1+1,len(self.oplossing_df)):
                counter_tuple = 0
                for gang in self.gangen:
                    if self.oplossing_df[gang][id1] == self.oplossing_df[gang][id2]:
                        counter_tuple += 1
                
                if counter_tuple > 1:
                    deelnemer1 = self.oplossing_df['Bewoner'][id1]
                    deelnemer2 = self.oplossing_df['Bewoner'][id2]
                    adrs1 = self.bewoners_df['Huisadres'][self.bewoners_df['Bewoner'] == deelnemer1].values[0]
                    adrs2 = self.bewoners_df['Huisadres'][self.bewoners_df['Bewoner'] == deelnemer2].values[0]
                    if adrs1 == adrs2:
                        self.huishoudens_samen.append([deelnemer1, deelnemer2, counter_tuple - 1])
                    else:
                        self.deelnemers_samen.append([deelnemer1, deelnemer2, counter_tuple - 1])

    def penalty6(self):
        self.adres_wederom_hoofd = []
        for adrs in self.gang_vorigjaar_df[self.gang_vorigjaar_df['Gang'] == 'Hoofd'].index:
            if (self.oplossing_df['Huisadres'][self.oplossing_df['kookt'] == 'Hoofd'] == adrs).any():
                self.adres_wederom_hoofd.append(adrs)

    def penalty7(self):
        self.kookt_niet_voorkeur = []
        for gang in self.gangen:
            for adrs in self.adressen_df[self.adressen_df['Voorkeur gang'] == gang].index:
                if (self.oplossing_df['kookt'][self.oplossing_df['Huisadres'] == adrs] == gang).all():
                    continue
                else:
                    self.kookt_niet_voorkeur.append([adrs,gang])

    def penalty8(self):
        self.buren_samen = []
        for ind in range(len(self.buren_df['Bewoner1'])):
            bewoner1 = self.buren_df['Bewoner1'][ind]
            bewoner2 = self.buren_df['Bewoner2'][ind]
            for gang in self.gangen:
                adrs_pers_1 = self.oplossing_df[gang][self.oplossing_df['Bewoner'] == bewoner1].values[0]
                adrs_pers_2 = self.oplossing_df[gang][self.oplossing_df['Bewoner'] == bewoner2].values[0]
                if adrs_pers_1 == adrs_pers_2:
                    self.buren_samen.append([bewoner1, bewoner2, gang])
                    
    def penalty9(self):
        self.deelnemers_wederom_samen = []
        for idx in range(len(self.tafelgenoot_vorigjaar_df)):
            bewoner1 = self.tafelgenoot_vorigjaar_df['Bewoner1'][idx]
            bewoner2 = self.tafelgenoot_vorigjaar_df['Bewoner2'][idx]
            deelnemer1_doet_mee = (self.Bewoners_df['Bewoner'] == bewoner1).any()
            deelnemer2_doet_mee = (self.Bewoners_df['Bewoner'] == bewoner2).any()
            if deelnemer1_doet_mee and deelnemer2_doet_mee:
                for gang in self.gangen:
                    adrs_pers_1 = self.oplossing_df[gang][self.oplossing_df['Bewoner'] == bewoner1].values[0]
                    adrs_pers_2 = self.oplossing_df[gang][self.oplossing_df['Bewoner'] == bewoner2].values[0]
                    if adrs_pers_1 == adrs_pers_2:
                        if not [bewoner1, bewoner2, gang] in self.deelnemers_wederom_samen:
                            self.deelnemers_wederom_samen.append([bewoner1, bewoner2, gang])
