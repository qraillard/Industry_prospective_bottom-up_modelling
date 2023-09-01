import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import time
import pickle
from pyomo.util.infeasible import log_infeasible_constraints
from pyomo.opt import SolverStatus, TerminationCondition
import pyomo.environ as pe
from pyomo.contrib import appsi
import logging
import warnings
# warnings.filterwarnings("ignore")

from Model.Industry_model_planning import *
from Model.Input_data_ordering import *
from Model.Model_initialization import *



start_overall=time.time()
start=time.time()
print("\033[4m" + "Industry modelling" + "\033[0m")
print("\tInput data import")
Parameters_data= pd.read_excel("Input data/Input_data_reference.xlsx",sheet_name=["TECHNOLOGIES","RESOURCES","TECHNOLOGIES_RESOURCES","TECHNOLOGIES_TECH_TYPE","SECTOR","CCS"])
year_list=list(range(2015,2071))
areas_list=[
            "France",
            "Germany",
            "Italy",
            "Great Britain",
            "Spain",
            "Belgium"
            ]
resource_list=list(Parameters_data["TECHNOLOGIES_RESOURCES"].columns[4:])
sector_list=list(Parameters_data["RESOURCES"]["SECTOR"].unique()) #["Steel","Chemistry","Cement","Glass","All"]#
try:
    sector_list.remove(np.nan)
except:
    pass
# print(sector_list)
tr_df=Parameters_data["TECHNOLOGIES_RESOURCES"]
tr_df["SECTOR"].fillna(0,inplace=True)
tr_df=tr_df[tr_df.SECTOR.isin(sector_list+[0])]
ccs_df=Parameters_data["CCS"].fillna(0)
ccs_df=ccs_df[ccs_df.SECTOR.isin(sector_list+[0])]

t_tt_combinations=tech_and_tech_type_combinations(tr_df)
s_t_combinations=sector_tech_combinations(tr_df)
ccs_tech_combinations=ccs_tech_combinations_fct(ccs_df)
tech_ccs_combinations=tech_ccs_combinations_fct(ccs_df)
sector_tech_ccs_combinations=sector_tech_ccs_combinations_fct(ccs_df,sector_list)
tech_list = list(tr_df.TECHNOLOGIES.dropna().unique())


count=0
prev_output_ratio=0
for parameters_varation in [
# {"Prices_change_ratio":{"Electricity":1,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":1,"No_efuels":1},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":0.9,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":1,"No_efuels":1},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":0.75,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":1,"No_efuels":1},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":0.5,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":1,"No_efuels":1},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":1,"ctax":0.75,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":1,"No_efuels":1},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":1,"ctax":1.5,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":1,"No_efuels":1},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":1,"ctax":2,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":1,"No_efuels":1},
# {"Prices_change_ratio":{"Electricity":1.5,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":1,"No_efuels":1},
# {"Prices_change_ratio":{"Electricity":1.25,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":1,"No_efuels":1},
# {"Prices_change_ratio":{"Electricity":0.75,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":1,"No_efuels":1},
# {"Prices_change_ratio":{"Electricity":0.6,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":1,"No_efuels":1}, #42€/MWh prix ARENH
# {"Prices_change_ratio":{"Electricity":1,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":2,},"Output_post_2030_change_ratio":1,"No_efuels":1},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":0,},"Output_post_2030_change_ratio":1,"No_efuels":1},

# 0

# {"Prices_change_ratio":{"Electricity":1,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":0.8},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":0.9,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":0.8},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":0.75,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":0.8},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":0.5,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":0.8},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":1,"ctax":0.75,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":0.8},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":1,"ctax":1.5,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":0.8},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":1,"ctax":2,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":0.8},
# {"Prices_change_ratio":{"Electricity":1.5,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":0.8},
# {"Prices_change_ratio":{"Electricity":1.25,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":0.8},
# {"Prices_change_ratio":{"Electricity":0.75,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":0.8},
# {"Prices_change_ratio":{"Electricity":0.6,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":1,},"Output_post_2030_change_ratio":0.8}, #42€/MWh prix ARENH{"Prices_change_ratio":{"Electricity":1,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":2,},"Output_post_2030_change_ratio":1},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":2,},"Output_post_2030_change_ratio":0.8},
# {"Prices_change_ratio":{"Electricity":1,"Biogas":1,"ctax":1,"co2_transport_and_storage_cost":0,},"Output_post_2030_change_ratio":0.8},
]:
    Parameters_data = pd.read_excel("Input data/Input_data_reference.xlsx",
                                    sheet_name=["TECHNOLOGIES", "RESOURCES", "TECHNOLOGIES_RESOURCES",
                                                "TECHNOLOGIES_TECH_TYPE", "SECTOR", "CCS"])
    if prev_output_ratio!=parameters_varation["Output_post_2030_change_ratio"]:
        prev_output_ratio=parameters_varation["Output_post_2030_change_ratio"]
        count=0

    print("\033[4m"+"Overall  for "+str(parameters_varation) + "\033[0m")

    print("\tData pre-processing")
    a = time.time()
    u = Parameters_data["RESOURCES"]
    u.loc[u.RESOURCES.isin(["Electricity","Electricity_25%_LF","Electricity_50%_LF"]) & (u.YEAR == 2050) & (u.Parameter == "flow_cost_r"), "Value"] = u.loc[u.RESOURCES.isin(["Electricity","Electricity_25%_LF","Electricity_50%_LF"]) & (u.YEAR == 2050) & (u.Parameter == "flow_cost_r"), "Value"] * parameters_varation["Prices_change_ratio"]["Electricity"]
    u.loc[(~u.RESOURCES.isin(["BYF_Cement","Fast_Carb","Solidia_Cement"])) & (u.YEAR >2030) & (u.Parameter.isin(["output","min_output"])), "Value"] = u.loc[(~u.RESOURCES.isin(["BYF_Cement","Fast_Carb","Solidia_Cement"])) & (u.YEAR == 2050) & (u.Parameter.isin(["output","min_output"])), "Value"] *  parameters_varation["Output_post_2030_change_ratio"]
    if parameters_varation["No_efuels"]==1:
        u.loc[(u.SECTOR=="E-Fuels")&(u.Parameter.isin(["is_product","output","min_output"])), "Value"]=0
    Parameters_data["RESOURCES"]=u

    u=Parameters_data["SECTOR"]
    u.loc[(u.Parameter == "carbon_tax") & (u.YEAR >= 2030), "Value"]=u.loc[(u.Parameter=="carbon_tax") &(u.YEAR>=2030),"Value"]*parameters_varation["Prices_change_ratio"]["ctax"]
    u.loc[(u.Parameter == "co2_transport_and_storage_cost") & (u.YEAR >= 2030), "Value"] = u.loc[(u.Parameter == "co2_transport_and_storage_cost") & (u.YEAR >=2030), "Value"] * parameters_varation["Prices_change_ratio"]["co2_transport_and_storage_cost"]
    Parameters_data["SECTOR"]=u

    u=Parameters_data["TECHNOLOGIES"]
    u.loc[(u.TECHNOLOGIES=="Biogas_Digester")&(u.YEAR==2050)&(u.Parameter=="flow_cost_t"),"Value"]=u.loc[(u.TECHNOLOGIES=="Biogas_Digester")&(u.YEAR==2050)&(u.Parameter=="flow_cost_t"),"Value"]*parameters_varation["Prices_change_ratio"]["Biogas"]
    Parameters_data["TECHNOLOGIES"]=u

    print("\t\tData pre-processing finished within " + str(round(time.time() - a, 0)) + "s")
    print("\tData processing")
    df_dict={}
    a=time.time()
    print("\t\tTECHNOLOGIES Sheet cleaning at "+str(round(a-start,0))+"s")
    df_dict["TECHNOLOGIES"]=technologies_sheet(Parameters_data["TECHNOLOGIES"],tech_list,sector_list,year_list,areas_list)
    print("\t\t\tTECHNOLOGIES Sheet cleaned within "+str(round(time.time()-a,0))+"s")
    a=time.time()
    print("\t\tRESOURCES Sheet cleaning at "+str(round(a-start,0))+"s")
    df_dict["RESOURCES"]=resource_sheet(Parameters_data["RESOURCES"],sector_list,year_list,areas_list,resource_list)
    print("\t\t\tRESOURCES Sheet cleaned within "+str(round(time.time()-a,0))+"s")
    a=time.time()
    print("\t\tTECHNOLOGIES_RESOURCES Sheet cleaning at "+str(round(a-start,0))+"s")
    df_dict["TECHNOLOGIES_RESOURCES"]=technologies_resources_sheet(Parameters_data["TECHNOLOGIES_RESOURCES"],sector_list,year_list,t_tt_combinations,s_t_combinations)
    print("\t\t\tTECHNOLOGIES_RESOURCES Sheet cleaned within "+str(round(time.time()-a,0))+"s")
    a=time.time()
    print("\t\tTECHNOLOGIES_TECH_TYPE Sheet cleaning at "+str(round(a-start,0))+"s")
    df_dict["TECHNOLOGIES_TECH_TYPE"]=technologies_tech_type_sheet(Parameters_data["TECHNOLOGIES_TECH_TYPE"],tech_list,sector_list,year_list,areas_list,t_tt_combinations)
    print("\t\t\tTECHNOLOGIES_TECH_TYPE Sheet cleaned within "+str(round(time.time()-a,0))+"s")
    a=time.time()
    print("\t\tSECTOR Sheet cleaning at "+str(round(a-start,0))+"s")
    df_dict["SECTOR"]=sector_sheet(Parameters_data["SECTOR"],sector_list,year_list,areas_list)
    # u=df_dict["SECTOR"]
    df_dict["SECTOR"]=max_biogas_readjustment(df_dict["SECTOR"],1)
    # v=df_dict["SECTOR"]
    print("\t\t\tSECTOR Sheet cleaned within "+str(round(time.time()-a,0))+"s")
    a=time.time()
    print("\t\tCCS Sheet cleaning at "+str(round(a-start,0))+"s")
    df_dict["CCS"]=ccs_sheet(Parameters_data["CCS"],sector_list,year_list,areas_list,sector_tech_ccs_combinations)
    print("\t\t\tCCS Sheet cleaned within "+str(round(time.time()-a,0))+"s")



    #end region
    Parameters={"TECHNOLOGIES_TECH_TYPE_parameters" : df_dict["TECHNOLOGIES_TECH_TYPE"].reset_index().fillna(0).set_index(['TECHNOLOGIES','TECH_TYPE','SECTOR','AREAS','YEAR']),
                "RESOURCES_parameters" : df_dict["RESOURCES"].reset_index().fillna(0).set_index(['RESOURCES','SECTOR','AREAS','YEAR']),
                "TECHNOLOGIES_RESOURCES_parameters" : df_dict["TECHNOLOGIES_RESOURCES"].reset_index().fillna(0).\
                    melt(id_vars=['TECHNOLOGIES','TECH_TYPE','SECTOR','YEAR'], var_name="RESOURCES",value_name='conversion_factor').\
                    set_index(['TECHNOLOGIES','TECH_TYPE','SECTOR','RESOURCES','YEAR']),
                "TECHNOLOGIES_parameters":df_dict["TECHNOLOGIES"].reset_index().fillna(0).set_index(["TECHNOLOGIES",'SECTOR',"AREAS","YEAR"]),
                "SECTOR_parameters": df_dict["SECTOR"].reset_index().fillna(0).set_index(['SECTOR', 'AREAS', 'YEAR']),
                "CCS_parameters": df_dict["CCS"].reset_index().fillna(0).set_index(['CCS_TYPE', 'TECHNOLOGIES', 'SECTOR', 'AREAS', 'YEAR'])
                }

    # with open('Input_data.pickle', 'wb') as file:
    #     pickle.dump(Parameters, file, protocol=pickle.HIGHEST_PROTOCOL)
    # file.close()

    a=time.time()

    if count==0:
        print("\n\tModel Creation at "+str(round(a-start,0))+"s")
        model=GetIndustryModel(Parameters,t_tt_combinations,s_t_combinations,tech_ccs_combinations,sector_tech_ccs_combinations)#emission
        var_value_map = get_var_value_map(model)
        print("\t\t\tCreated within " + str(round(time.time() - a, 0)) + "s")


    else:
        print("\n\tModel Parameter Change at "+str(round(a-start,0))+"s")
        # print(model.V_cost_total.display())
        # set_var_value_from_map(model, var_value_map)
        # model=Update_Model(model,Parameters,prev_output_ratio,parameters_varation["Output_post_2030_change_ratio"],t_tt_combinations,s_t_combinations,sector_tech_ccs_combinations)
        model=Update_Modelv2(model,Parameters)
        # print(model.V_cost_total.display())
        print("\t\t\tCreated within " + str(round(time.time() - a, 0)) + "s")
    count+=1
    a = time.time()
    print("\n\tStart solving at " + str(round(a - start, 0)) + "s")
    # opt=appsi.solvers.Highs()
    # res = opt.solve(model)
    opt = SolverFactory('mosek')
    res = opt.solve(model, tee=False, options={"iparam.infeas_report_auto": 1,
                                               "iparam.infeas_report_level": 1,
                                               "iparam.infeas_generic_names": 1,
                                               "iparam.write_generic_names": 1})
    # log_infeasible_constraints(model, log_expression=True, log_variables=True)
    # logging.basicConfig(filename='errors.log', encoding='utf-8', level=logging.INFO)

    counter=0
    try:
        if (res.solver.termination_condition == TerminationCondition.infeasible):
            print("\n\t\t\tInfeasibility check")
            for c in model.component_objects(ctype=pe.Constraint):
                sub_counter = 0
                infeasible_index_list = []
                if c.is_indexed():
                    index_dict = c.id_index_map()
                    for key in index_dict.keys():
                        if c[index_dict[key]].slack() < -5e-5:
                            # print(c[index_dict[key]].slack())
                            sub_counter += 1
                            infeasible_index_list.append(index_dict[key])
                    if sub_counter > 0:
                        print(f'\t\t\t\tConstraint {c.name} is not satisfied for the following indexes:',
                              infeasible_index_list)

                else:
                    if c.slack() < -5e-5:  # constraint is not met
                        sub_counter += 1
                        print(c.slack())
                        print(f'\t\t\t\tConstraint {c.name} is not satisfied')
                counter += sub_counter
    except:
        pass
    if counter>0:
        print(counter,"constraints are not satisfied")
        print("\t\t\tSolving stopped within " + str(round(time.time() - a, 0)) + "s")
        # exit()
    else:
        print("\t\t\tSolved within "+str(round(time.time()-a,0))+"s")

        a=time.time()
        print("\n\tResults extraction at "+str(round(a-start,0))+"s")

        results={}
        results["tech_tech_type_combinations_parameters"]=t_tt_combinations
        results["Parameters"]=Parameters
        model_vars = model.component_map(ctype=Var)
        for k in model_vars.keys():   # this is a map of {name:pyo.Var}
            v = model_vars[k]
            s = pd.Series(v.extract_values(), index=v.extract_values().keys())
            results[k]=pd.DataFrame(s)


        variation_name=f'{parameters_varation["Output_post_2030_change_ratio"]:.2f}'+"output_"
        variation_name+=f'{parameters_varation["Prices_change_ratio"]["Electricity"]:.2f}'+"elec_"
        variation_name+=f'{parameters_varation["Prices_change_ratio"]["Biogas"]:.2f}'+"biogas_"
        variation_name += f'{parameters_varation["Prices_change_ratio"]["ctax"]:.2f}'+ "ctax_"
        variation_name += f'{parameters_varation["Prices_change_ratio"]["co2_transport_and_storage_cost"]:.2f}' + "co2st"
        if parameters_varation["No_efuels"]==1:
            variation_name+="_no_efuels"
        with open('Results/Result files/Results_'+variation_name+'.pickle', 'wb') as f:
            pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
        print("\t\t\tExtracted within "+str(round(time.time()-a,0))+"s")
    #Empty the RAM
    # del model
    # del res
    # del Parameters
    del df_dict
    del results

    prev_output_ratio = parameters_varation["Output_post_2030_change_ratio"]

print("\nFinished after "+str(round(time.time()-start_overall,0))+"s")
