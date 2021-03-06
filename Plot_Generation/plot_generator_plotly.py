# Generate the different graphical plots



# Script to process the results and generate the plots

from SQL_Util import SQLUtils
from ES_Manager import ES_Manager
from datetime import datetime
from datetime import timedelta
from matplotlib import pyplot as plt
from statistics import mean
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
from plotly.graph_objects import Layout




sql_obj = SQLUtils()
es_obj = ES_Manager()

class Result_Processor():
    # process the results

    def __init__(self):
        #self.table_name = "user_goal_logs"
        self.table_name = "user_goal_response_time"
        self.experiment_name = "experiment_test3"
        self.index = "response_time"
        #self.latency_index = "experiment_withoutrank_wctrace"
        self.latency_index = "experiment_test4"

    def get_user_goal_records(self,experiment_name):
        query = "select * from " + self.table_name + " where experiment=" + "'" + str(experiment_name) + "';"
        print(query)
        cursor, db_object = sql_obj.query_table(query)
        results = list(cursor)
        result_pair_list = []


        for(id,goal, goal_type,experiment,latency,created_at) in results:
            #print(latency, created_at)
            print (" Experiment ", experiment_name)
            if experiment_name == "experiment_wctrace_sn_6hours" or experiment_name == "experiment_wctrace_sa_6hours":
                if (len(goal)>1):
                    latency = latency - 0.6*int(len(goal)) # avoid network latency this value has been measured

            result_pair = (str(created_at),latency,goal_type)
            result_pair_list.append(result_pair)

        #print(result_pair_list)
        return result_pair_list


    # Function to get the response time of each goal for a given table
    def get_response_time_goal_type(self,experiment_name):
        query = "select goal_type, avg(latency) from " + self.table_name + " where  experiment=" + "'"  + str(experiment_name) + "'" +  " group by goal_type;"
        print (query)
        cursor, db_object = sql_obj.query_table(query)
        results = list(cursor)
        goal_response_dict = {}
        for (goal_type, avg_latency) in results:
            goal_response_dict[goal_type] = avg_latency

        #print (goal_response_dict)
        return goal_response_dict


    def query_es(self,experiment_name):
        # query elasticsearch to obtain the records of microservices for the above said period
        query_result_list = self.get_user_goal_records(experiment_name)

        start_time_string = query_result_list[0][0]
        end_time_string  = query_result_list[len(query_result_list)-1][0]
        print (start_time_string)
        print (end_time_string)

        gte_start_time = datetime.strptime(start_time_string,"%Y-%m-%d %H:%M:%S") -  timedelta(minutes=60)
        gte_start_time = gte_start_time.strftime("%Y/%m/%d %H:%M:%S")

        # reformating time string as per what is needed by ES and time of ES is in UTC, hence timezone difference has to be calculated
        lte_end_time = datetime.strptime(end_time_string,"%Y-%m-%d %H:%M:%S") - timedelta(minutes=60)
        lte_end_time = lte_end_time.strftime("%Y/%m/%d %H:%M:%S")
        query = {
            "query": {
                "range": {
                    "timestamp": {
                        "gte": gte_start_time,
                        "lte": lte_end_time
                    }
                }
            }
        }

        es_manager_scroll_resp = es_obj.scroll_search_es(index=experiment_name, query=query)
        print(es_manager_scroll_resp["_scroll_id"])
        count = 0
        res = es_obj.contine_scroll_es(es_manager_scroll_resp["_scroll_id"])
        result_pair_list = []
        while (len(res['hits']['hits'])):
            res = es_obj.contine_scroll_es(es_manager_scroll_resp["_scroll_id"])
            # print (res['hits'])
            for hit in res['hits']['hits']:
                record = hit["_source"]
                result_pair = (record["timestamp"], record["latency"], record["goal"])
                result_pair_list.append(result_pair)

        return result_pair_list

    def plot_generator(self):
        # generate box plots for the experiments

        latecy_list_without_rank = self.query_latency_records("experiment_test3")
        latecy_list_with_rank = self.query_latency_records("experiment_test4")


        print(len(latecy_list_without_rank))
        print(len(latecy_list_with_rank))

        plt.clf()

        bp = plt.boxplot((latecy_list_without_rank[:5400],latecy_list_with_rank[:5400]), patch_artist=True)
        # fill with colors
        colors = ['#FFE066', '#5386E4']
        # colors = ['#FFE066', '#70C1B3', '#50614F','#247BA0']
        i = 0
        for box in bp['boxes']:
            box.set(facecolor=colors[i], linewidth=2)
            i += 1
        plt.xticks([1, 2], ['dyn_norank', 'dyn_rank'])
        # plt.xticks([1, 2, 3, 4], ['sta_gre', 'tim_Qle', 'lin_gre','lin_Qle'])
        plt.ylabel("Response Time (ms)")
        plt.xlabel("Approaches")
        plt.savefig("box_plot_response_time.png", dpi=300)


    def calculate_perminute_utility_user_goal_sastisfaction(self, record_pair_list, t_max_goal, t_min_goal, p_goal):
        # takes the data ordered as [(timestamp, responsetime), ......]
        # t_goal and p_goal are thresholds and penalty values respectively
        current_time_string = record_pair_list[0][0]
        start_time = datetime.strptime(current_time_string, "%Y-%m-%d %H:%M:%S")
        count_list = []  # for every minute append the ratio of total goals to actual

        print(start_time)

        utility_list = []

        util_val = 0
        sum = 0
        goal_count = 0
        resp_time_count = 0
        for data in record_pair_list:

            time_string = data[0]
            time_val = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
            goal_count += 1

            # resp_time_count+=1

            if data[1] >= t_max_goal :
                util_val = (t_max_goal - data[1]) * p_goal
            #elif data[1] > t_min_goal and data[1] <= t_max_goal:
            #    util_val = (data[1]-t_min_goal)*0.2
            else:
                util_val = (t_max_goal - data[1])

            sum = sum + util_val
            # print(time_val, start_time)
            if data[1] < t_max_goal:
                goal_count +=1

            if (time_val - start_time).seconds >= 60:
                utility_list.append(sum)
                sum = 0
                util_val = 0
                start_time = time_val
                count_list.append(resp_time_count / goal_count)
                goal_count = 0
                resp_time_count = 0
        return utility_list, count_list





    def iot_energy_calculator(self,data_path):
        # calculate the utility values for the IoT energy files
        df_collect_org = pd.read_csv(data_path, sep=",",
                                     index_col="timestamp")  # Read the proccessed data frame
        df_collect_series = df_collect_org.values
        # print(df_collect_org)
        print(type(df_collect_series))

        energy_val_list = []
        for i in range(0, len(df_collect_series)):
            energy_value = 0
            for j in range(0, 22):
                if j not in [1, 15, 16, 17, 18, 19, 20]:
                    # energy_j = prev_vals[j] - df_collect_series[i, j]
                    energy_value = energy_value + df_collect_series[i, j]
                    #print (energy_value)
            energy_val_list.append(energy_value)

        #print (len(energy_val_list))
        #print (sum(energy_val_list))

        return energy_val_list


    def iot_utility_calculator(self,data1,data2,data3):

        without_rank_energy_list = self.iot_energy_calculator(data1)
        with_rank_energy_list = self.iot_energy_calculator(data2)
        static_adap_energy_list = self.iot_energy_calculator(data3)


        p_e = 5 # penalty for energy
        t_e = 1.45 # threshold for energy

        iot_utility_without_rank_list = []

        for data in without_rank_energy_list:
            iot_min_utility = 0
            if data > t_e:
                iot_min_utility = (t_e - data)*p_e
            else:
                iot_min_utility = (t_e-data)*10
            iot_utility_without_rank_list.append(iot_min_utility)

        iot_utility_with_rank_list = []

        for data in with_rank_energy_list:
            iot_min_utility = 0
            if data > t_e:
                iot_min_utility = (t_e - data) * p_e
            else:
                iot_min_utility = (t_e - data)*10

            iot_utility_with_rank_list.append(iot_min_utility)

        iot_utility_static_adap_list = []

        for data in static_adap_energy_list:
            iot_min_utility = 0
            if data > t_e:
                iot_min_utility = (t_e - data) * p_e
            else:
                iot_min_utility = (t_e - data)*10

            iot_utility_static_adap_list.append(iot_min_utility)


        return iot_utility_without_rank_list,iot_utility_with_rank_list,iot_utility_static_adap_list


    def utility_calculator_user_goal(self, experiment1, experiment2, experiment3, experiment4):
        # experiment_name = "experiment_test3"
        penality_val = 0.8
        reward = 1.0
        t_max_goal = 4.0
        t_min_goal = 0.0


        record_list1 = self.get_user_goal_records(experiment1)

        utility_without_rank_list, count_list_norank = self.calculate_perminute_utility_user_goal_sastisfaction(record_list1,
                                                                                                                t_max_goal,
                                                                                                                t_min_goal,
                                                                                                                penality_val)
        #time.sleep(10)
        record_list2 = self.get_user_goal_records(experiment2)
        utility_with_rank_list, count_list_rank = self.calculate_perminute_utility_user_goal_sastisfaction(record_list2,
                                                                                                           t_max_goal,
                                                                                                           t_min_goal,
                                                                                                           penality_val)

        record_list3 = self.get_user_goal_records(experiment3)
        utility_static_list, count_list_static = self.calculate_perminute_utility_user_goal_sastisfaction(record_list3,
                                                                                                          t_max_goal,
                                                                                                          t_min_goal,
                                                                                                          penality_val)

        record_list4 = self.get_user_goal_records(experiment4)
        utility_static_adap_list, count_list_static_adap = self.calculate_perminute_utility_user_goal_sastisfaction(
            record_list4, t_max_goal, t_min_goal,
            penality_val)

        print("util sum no rank ", sum(utility_without_rank_list))
        print("util sum rank ", sum(utility_with_rank_list))

        print("average goal satis index no rank ", sum(count_list_norank) / len(count_list_norank))
        print("average goal satis index rank ", sum(count_list_rank) / len(count_list_rank))

        print("static utility ", sum(utility_static_list))

        return utility_without_rank_list, utility_with_rank_list, utility_static_list, utility_static_adap_list


def cumul_plot_utility_plot_generator(iot_energy_path1, iot_energy_path2,iot_energy_path3,plot_path):
    result_proc_obj =  Result_Processor()
    #goal_utility_without_rank_list,goal_utility_with_rank_list,goal_utility_static_list ,goal_utility_static_adap_list = result_proc_obj.utility_calculator_user_goal("experiment_wctrace_dn_6hours","experiment_wctrace_da_6hours","experiment_wctrace_sn_6hours","experiment_wctrace_sa_6hours")
    goal_utility_without_rank_list,goal_utility_with_rank_list,goal_utility_static_list ,goal_utility_static_adap_list = result_proc_obj.utility_calculator_user_goal("experiment_wctrace_dn_6hours","experiment_wctrace_da_6hours","experiment_wctrace_sn_6hours","experiment_wctrace_sa_6hours")
    #goal_utility_without_rank_list,goal_utility_with_rank_list,goal_utility_static_list ,goal_utility_static_adap_list = result_proc_obj.utility_calculator_user_goal("experiment_clarknet_1_time","experiment_clarknet_2_time","static_test_noadap_wctrace_2","static_test_adap_wctrace_2")





    print (len(goal_utility_without_rank_list), sum(goal_utility_without_rank_list))
    print (len(goal_utility_with_rank_list), sum(goal_utility_with_rank_list))
    print (len(goal_utility_static_list), sum(goal_utility_static_list))
    print (len(goal_utility_static_adap_list), sum(goal_utility_static_adap_list))

    print (" utility sum ", sum(goal_utility_static_list[:300]))
    print (" utility adap sum ", sum(goal_utility_static_adap_list[:300]))

    goal_utility_static_adap_list = goal_utility_static_adap_list[:300] # consider only the 6300 seconds data




    iot_without_rank_util, iot_with_rank_util,iot_static_adap_util = result_proc_obj.iot_utility_calculator(iot_energy_path1,iot_energy_path2,iot_energy_path3)

    print("iot util for without rank ", sum(iot_without_rank_util[:300]))
    print("iot util for with rank ", sum(iot_with_rank_util[:300]))
    print ("iot util for static adap ", sum(iot_static_adap_util[:300]))
    print (" iot util for static no adap ", sum(iot_without_rank_util[:300]))


    # Normalize all the lists to make the graph creation

    # first is user_goal_utility


    print ("length of utility no rank ", len(goal_utility_without_rank_list))
    print ("length of utility  rank ", len(goal_utility_with_rank_list))
    print ("length of static utility  no adap ", len(goal_utility_static_list))
    print ("length of static utility  adap ", len(goal_utility_static_adap_list))

    print("average of utility no rank ", mean(goal_utility_without_rank_list))
    print("average of utility  rank ", mean(goal_utility_with_rank_list))
    print("average  of static utility  no adap ", mean(goal_utility_static_list))
    print("average of static utility  adap ", mean(goal_utility_static_adap_list))

    fixed_length = 300



    if (len(goal_utility_with_rank_list)<fixed_length):
        while(len(goal_utility_with_rank_list)!=fixed_length):
            goal_utility_with_rank_list.append(max(goal_utility_with_rank_list))






    # coeficients of the linear equation for calculating utility
    x1 = 5
    x2 = 0
    x3 = 4

    final_combined_withoutrank_util_list = []
    final_combined_withrank_util_list = []
    final_combined_static_util_list = []
    final_combined_static_adap_util_list = []

    cumulsum_without_rank = 0
    cumulsum_with_rank = 0
    cumulsum_static = 0
    cumulsum_static_adap = 0

    cumul_combined_withoutrank_util_list = []
    cumul_combined_withrank_util_list = []
    cumul_combined_static_util_list = []
    cumul_combined_static_adap_util_list = []


    # normalize the utility to make all in the same scale

    max_goal_util  = 40000

    max_iot = 20

    max_goal_utility_with_rank_list = np.array(goal_utility_with_rank_list)
    normalized_goal_utility_with_rank_list = max_goal_utility_with_rank_list / max_goal_utility_with_rank_list.max()
    goal_utility_with_rank_list = list(normalized_goal_utility_with_rank_list)


    max_goal_utility_without_rank_list = np.array(goal_utility_without_rank_list)
    normalized_goal_utility_without_rank_list = max_goal_utility_without_rank_list / max_goal_utility_with_rank_list.max()
    goal_utility_without_rank_list = list(normalized_goal_utility_without_rank_list)

    max_goal_utility_static_list = np.array(goal_utility_static_list)
    normalized_goal_utility_static_list = max_goal_utility_static_list/max_goal_utility_with_rank_list.max()
    goal_utility_static_list = list(normalized_goal_utility_static_list)

    max_goal_utility_static_adap_list = np.array(goal_utility_static_adap_list)
    normalized_goal_utility_static_adap_list = max_goal_utility_static_adap_list/max_goal_utility_with_rank_list.max()
    goal_utility_static_adap_list = list(normalized_goal_utility_static_adap_list)

    print("average of utility no rank ", mean(goal_utility_without_rank_list))
    print("average of utility  rank ", mean(goal_utility_with_rank_list))
    print("average  of static utility  no adap ", mean(goal_utility_static_list))
    print("average of static utility  adap ", mean(goal_utility_static_adap_list))

    max_iot_with_rank_util = np.array(iot_with_rank_util)
    normalized_iot_with_rank_util = max_iot_with_rank_util / max_iot_with_rank_util.max()
    iot_with_rank_util = list(normalized_iot_with_rank_util)

    max_iot_without_rank_util = np.array(iot_without_rank_util)
    normalized_iot_without_rank_util = max_iot_without_rank_util/max_iot_with_rank_util.max()
    iot_without_rank_util =  list(normalized_iot_without_rank_util)



    max_static_adap_iot_with_rank_util = np.array(iot_static_adap_util)
    normalized_static_iot_with_rank_util = max_static_adap_iot_with_rank_util / max_iot_with_rank_util.max()
    iot_static_adap_util = list(normalized_static_iot_with_rank_util)



    for index in range(0,300):

        withoutrank_util_val = x1*goal_utility_without_rank_list[index]  + x3*iot_without_rank_util[index]

        withrank_util_val = x1*goal_utility_with_rank_list[index]  + x3*iot_with_rank_util[index]

        static_util_val  = x1*goal_utility_static_list[index] + x3*iot_without_rank_util[index] # It is the same as the base one without adaptation

        static_util_adap_val  = x1*goal_utility_static_adap_list[index] + x3*iot_static_adap_util[index] # It is the same as the base one without adaptation




        final_combined_withoutrank_util_list.append(withoutrank_util_val)
        final_combined_withrank_util_list.append(withrank_util_val)
        final_combined_static_util_list.append(static_util_val)
        final_combined_static_adap_util_list.append(static_util_adap_val)

        cumulsum_without_rank = cumulsum_without_rank + (withoutrank_util_val)

        cumul_combined_withoutrank_util_list.append(cumulsum_without_rank)

        cumulsum_with_rank = cumulsum_with_rank + (withrank_util_val)

        cumul_combined_withrank_util_list.append(cumulsum_with_rank)

        cumulsum_static = cumulsum_static + (static_util_val)
        cumul_combined_static_util_list.append(cumulsum_static)

        cumulsum_static_adap = cumulsum_static_adap + (static_util_adap_val)
        cumul_combined_static_adap_util_list.append(cumulsum_static_adap)

    print (sum(final_combined_withoutrank_util_list))
    print (sum(final_combined_withrank_util_list))
    print (sum(final_combined_static_util_list))
    print (sum(final_combined_static_adap_util_list))

    layout = Layout(plot_bgcolor='rgba(0,0,0,0)')

    fig = go.Figure()

    x_axis_time_list = [i for i in range(1,301)]

    #[0,50,100,150,200,250,300]


    print (" DA Util list ", len(cumul_combined_withrank_util_list))
    fig.add_trace(go.Scatter(x=x_axis_time_list,y=cumul_combined_withrank_util_list,name="DA",line=dict(color='#364f6b', width=3.5)))
    fig.add_trace(go.Scatter(x=x_axis_time_list,y=cumul_combined_withoutrank_util_list, name="DN",line=dict(color='indianred', width=3.5,
                              dash='dash')))
    fig.add_trace(go.Scatter(x=x_axis_time_list,y=cumul_combined_static_adap_util_list, name="SA",line=dict(color='royalblue', width=3.5,
                              dash='dot')))
    fig.add_trace(go.Scatter(x=x_axis_time_list,y=cumul_combined_static_util_list, name="SN",line=dict(color='#fc5185', width=3.5,
                              dash='dashdot')))

    fig.update_layout(
        # title='Energy Consumption for Scenario ' + scenario_name,
        xaxis_title='Time in Minutes',
        yaxis_title='Cumulative Utility', font=dict(
            family="sans serif",
            size=18,
            color="black",
        ), margin={"r": 0, "t": 0, "l": 0, "b": 0}, legend=
        dict(
            # orientation="v",
            # anchor="bottom",
            # y=1.02,
            # xanchor="right",
            # x=1.0,
            font=dict(size=18)
        ),
        template='plotly'

    )
    fig.update_layout( legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01
    ))
    #fig.write_image(plot_path+"cumulative_utility_plot_wctrace_plotly.png",format="png",engine="kaleido", width=1024, height=576,scale=10.0)
    fig.write_image(plot_path+"cumulative_utility_plot_wctrace_plotly.png",format="png",engine="kaleido", width=640, height=480,scale=10.0)


    #plt.plot(cumul_combined_withrank_util_list, label="DA", linewidth=2.0, color='#686ee2')

    #plt.plot(cumul_combined_withoutrank_util_list, label="DN", linewidth=2.0, color='#f35c6e')

    #plt.plot(cumul_combined_static_adap_util_list, label="SA", linewidth=2.0, color='#5c3e84')

    #plt.plot(cumul_combined_static_util_list, label="SN", linewidth=2.0, color='#ffa87b')


    #plt.ylabel("Cumulative Utility")
    #plt.xlabel("Time in Seconds ")

    fig.show()

    #plt.legend(loc="upper left")
    #plt.text(x=300, y=cumul_combined_withrank_util_list[299] + 4, s="DA", fontsize=8,
    #         bbox=dict(facecolor='whitesmoke', boxstyle="round, pad=0.4"))
    #plt.text(x=300, y=cumul_combined_withoutrank_util_list[299] + 4, s="DN", fontsize=8,
    #         bbox=dict(facecolor='whitesmoke', boxstyle="round, pad=0.4"))
    #plt.text(x=300, y=cumul_combined_static_adap_util_list[299] + 4, s="SA", fontsize=8,
    #         bbox=dict(facecolor='whitesmoke', boxstyle="round, pad=0.4"))
    #plt.text(x=300, y=cumul_combined_static_util_list[299] + 4, s="SN", fontsize=8,
    #         bbox=dict(facecolor='whitesmoke', boxstyle="round, pad=0.4"))
    #plt.tight_layout()
    #plt.savefig(plot_path + "cumulative_utility_plot_wctrace.png", dpi=300)




    plt.clf()
    plt.figure(figsize=(5, 5))
    bp = plt.boxplot((final_combined_static_util_list,final_combined_static_adap_util_list,final_combined_withoutrank_util_list,final_combined_withrank_util_list), patch_artist=True)
    # fill with colors
    colors = ['#FED8B1', '#247BA0','#5386E4','#50514F',]
    # colors = ['#FFE066', '#70C1B3', '#50614F','#247BA0']
    i = 0
    for box in bp['boxes']:
        box.set(facecolor=colors[i], linewidth=1)
        i += 1
    plt.legend()
    plt.tight_layout()
    plt.legend(loc="upper right")
    plt.xticks([1, 2,3,4], ['SN','SA', 'DN','DA'])
    plt.ylabel("Utility ")
    plt.xlabel("Approaches")
    plt.savefig(plot_path + "box_plot_utility_wctrace.png", dpi=300)



    '''
    ### Create box plot just for goal utility
    plt.clf()
    plt.figure(figsize=(5, 5))
    bp = plt.boxplot((goal_utility_static_list, goal_utility_static_adap_list,
                      goal_utility_without_rank_list, goal_utility_without_rank_list),patch_artist=True)
    # fill with colors

    #colors = ['#ffcccb', '#ffcccb', '#ffcccb', '#ffcccb']
    colors = ['#FED8B1', '#FED8B1', '#FED8B1', '#FED8B1']

    i = 0
    for box in bp['boxes']:
        box.set(color=colors[i], linewidth=1)

        i += 1
    plt.legend()
    # plt.grid(True)
    # plt.axhline(y=6.0, color='green', linestyle='--', linewidth=1.5)
    plt.legend(loc="upper right")
    plt.xticks([1, 2, 3, 4], ['SN', 'SA', 'DN', 'DA'])
    plt.ylabel("Utility ")
    plt.xlabel("Approaches")
    plt.tight_layout()
    plt.savefig(plot_path + "box_plot_utility_wctrace_goal.png", dpi=300)

    print (" average goal utility without rank ", mean(goal_utility_without_rank_list))
    print (" average goal utility with rank ", mean(goal_utility_with_rank_list))

    '''

    fig = go.Figure()

    fig.add_trace(go.Box(y=goal_utility_static_list, quartilemethod="linear", name="SN"))
    fig.add_trace(go.Box(y=goal_utility_static_adap_list, quartilemethod="linear", name="SA"))
    fig.add_trace(go.Box(y=goal_utility_without_rank_list, quartilemethod="linear", name="DN"))
    fig.add_trace(go.Box(y=goal_utility_with_rank_list, quartilemethod="linear", name="DA"))
    #fig.add_trace(go.Box(y=goal_utility_static_list, quartilemethod="linear", name="SN",marker_color='#fc5185'))

    #fig.add_trace(go.Box(y=goal_utility_static_adap_list, quartilemethod="linear", name="SA",marker_color='royalblue'))

    #fig.add_trace(go.Box(y=goal_utility_without_rank_list, quartilemethod="linear", name="DN",marker_color='indianred'))

    #fig.add_trace(go.Box(y=goal_utility_with_rank_list, quartilemethod="linear", name="DA",marker_color='#364f6b'))

    fig.update_layout(
        # title='Energy Consumption for Scenario ' + scenario_name,
        xaxis_title='Approaches',
        yaxis_title='Utility', font=dict(
            family="sans serif",
            size=18,
            color="black",
        ), margin={"r": 0, "t": 0, "l": 0, "b": 0}, legend=
        dict(
            # orientation="v",
            # anchor="bottom",
            # y=1.02,
            # xanchor="right",
            # x=1.0,
            font=dict(size=18)
        ))

    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))

    # fig.layout.plot_bgcolor = 'rgba(0,0,0,0)'
    # fig.layout.grid = 'True'
    fig.show()
    fig.write_image(plot_path + "box_plot_utility_wctrace_goal_plotly.png", format="png",
                    engine="kaleido",
                    width=640, height=480,
                    scale=10.0)


    # generate cumulative graph for energy consumption of each approaches




    ### Create box plot just for IoT utility
    cumul_without_rank_energy_iot = []
    cumul_withrank_energy_iot = []
    cumul_staticadap_energy_iot = []

    without_rank_energy_list = result_proc_obj.iot_energy_calculator(iot_energy_path1)
    with_rank_energy_list = result_proc_obj.iot_energy_calculator(iot_energy_path2)
    static_adap_energy_list = result_proc_obj.iot_energy_calculator(iot_energy_path3)

    cumul_without_energy_sum = 0
    cumul_withrank_energy_sum = 0
    cumul_static_energy_sum = 0
    for index in  range(0,300):
        cumul_without_energy_sum = cumul_without_energy_sum + without_rank_energy_list[index]
        cumul_withrank_energy_sum = cumul_withrank_energy_sum  + with_rank_energy_list[index]
        cumul_static_energy_sum = cumul_static_energy_sum  + static_adap_energy_list[index]

        cumul_without_rank_energy_iot.append(cumul_without_energy_sum)
        cumul_withrank_energy_iot.append(cumul_withrank_energy_sum)
        cumul_staticadap_energy_iot.append(cumul_static_energy_sum)

    plt.clf()
    plt.figure(figsize=(5, 5))
    # ax = fig.add_axes([0, 0, 1, 1])
    approach = ['SN', 'SA', 'DN', 'DA']
    energy = [sum(without_rank_energy_list[:300]), sum(static_adap_energy_list[:300]), sum(without_rank_energy_list[:300]),
              sum(with_rank_energy_list[:300])]
    plt.ylabel("Energy Consumed (Joules)")
    plt.xlabel("Approaches")
    width = 0.5
    y_pos = [0, 0.3, 2, 4.5, 5.5]

    bar_list = plt.bar(approach, energy,width=width)

    def autolabel(rects):
        """
        Attach a text label above each bar displaying its height
        """
        for rect in rects:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width() / 2., 1.0 * height,
                    '%d' % int(height),
                    ha='center', va='bottom')

    autolabel(bar_list)
    '''
    bar_list[0].set_color('#FFE066')
    bar_list[1].set_color('#5386E4')
    bar_list[2].set_color('#247BA0')
    bar_list[3].set_color('#ED6A5A')
    '''
    color_code = '#60AFFE'
    bar_list[0].set_color(color_code)
    bar_list[1].set_color(color_code)
    bar_list[2].set_color(color_code)
    bar_list[3].set_color(color_code)
    #plt.legend(loc="upper left")
    #plt.grid(which='minor')
    plt.tight_layout()
    plt.savefig(plot_path + "barplot_energy_worldcup.png", dpi=300)
    #plt.show()
    '''
    plt.plot(cumul_without_rank_energy_iot, label="DN", linewidth=2.0, color='#ED6A5A')
    plt.plot(cumul_withrank_energy_iot, label="DA", linewidth=2.0, color='#70C1B3')
    plt.plot(cumul_without_rank_energy_iot, label="SN", linewidth=2.0, color='#50514F')
    plt.plot(cumul_staticadap_energy_iot, label="SA", linewidth=2.0, color='#247BA0')

    plt.ylabel("Cumulative Energy Consumption (joules)")
    plt.xlabel("Time in Seconds ")

    plt.grid(True)
    plt.xticks([0, 20, 40, 60, 80, 100], [0, 1200, 2400, 3600, 4800, 6000])
    # plt.yticks([100000, 200000, 300000, 400000, 500000], ['100K', '200K', '300K', '400K', '500K'])
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.savefig("cumulative_energy_wctrace.png", dpi=300)
    '''


def iot_plot_generator():
    print (" generating iot utility plots ")


def bar_plot_generator():
    result_proc_obj = Result_Processor()
    response_dict_da = result_proc_obj.get_response_time_goal_type("experiment_wctrace_da_6hours")
    response_dict_dn = result_proc_obj.get_response_time_goal_type("experiment_wctrace_dn_6hours")
    print (response_dict_da)
    print (response_dict_dn)


    # bar graph plot generator
    approaches = ['DN', 'DA']



    fig = go.Figure(data=[
        go.Bar(name='seq', x=approaches, y=[response_dict_dn["seq"], response_dict_da["seq"]],marker_color ='#8ecae6'),
        go.Bar(name='oneof', x=approaches, y=[response_dict_dn["oneof"], response_dict_da["oneof"]],marker_color='#e07a5f'),
        go.Bar(name='and', x=approaches, y=[response_dict_dn["and"], response_dict_da["and"]],marker_color='#3d405b'),
        go.Bar(name='single', x=approaches, y=[response_dict_dn["single"], response_dict_da["single"]],marker_color='#81b29a'),
        go.Bar(name='or', x=approaches, y=[response_dict_dn["or"], response_dict_da["or"]],marker_color='#f2cc8f')
    ])

    fig.update_layout(barmode='group', xaxis_title='Dynamic Approaches',
        yaxis_title='Average Response Time (Seconds)', font=dict(
            family="sans serif",
            size=18,
            color="black",
        ), margin={"r": 0, "t": 0, "l": 0, "b": 0}, legend=
        dict(
            # orientation="v",
            # anchor="bottom",
            # y=1.02,
            # xanchor="right",
            # x=1.0,
            font=dict(size=18)
        ),
        template='plotly')
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99
    ))
    fig.write_image(plot_path + "bar_graph_goal_response_plotly.png", format="png", engine="kaleido",
                    width=640, height=480, scale=10.0)

    fig.show()


def cumulative_energy_plot_generator(data1,data2,data3):
    result_proc_obj = Result_Processor()
    energy_sn_dn = result_proc_obj.iot_energy_calculator(data1)
    energy_da = result_proc_obj.iot_energy_calculator(data2)
    energy_sa = result_proc_obj.iot_energy_calculator(data3)

    print (len(energy_sn_dn), len(energy_da), len(energy_sa))


    index= 0
    cumul_energy_sn_dn = []
    cumul_energy_da = []
    cumul_energy_sa = []

    energy_sum_sn_dn = 0
    energy_sum_da = 0
    energy_sum_sa = 0


    for index in range(0,301,1):
        energy_sum_sn_dn = energy_sum_sn_dn + energy_sn_dn[index]
        energy_sum_da = energy_sum_da + energy_da[index]
        energy_sum_sa = energy_sum_sa + energy_sa[index]

        cumul_energy_sn_dn.append(energy_sum_sn_dn)
        cumul_energy_da.append(energy_sum_da)
        cumul_energy_sa.append(energy_sum_sa)

    fig = go.Figure()

    x_axis_time_list = [i for i in range(0, 301,1)]

    # [0,50,100,150,200,250,300]

    fig.add_trace(go.Scatter(x=x_axis_time_list, y=cumul_energy_sn_dn,name="SN and DN"
                             ,line=dict(color='indianred', width=3.5,dash='dashdot')))
    fig.add_trace(go.Scatter(x=x_axis_time_list, y=cumul_energy_sa, name="SA",
                             line=dict(color='royalblue', width=3.5,
                                       dash='dot')))
    fig.add_trace(go.Scatter(x=x_axis_time_list, y=cumul_energy_da, name="DA",
                             line=dict(color='#364f6b', width=3.5,
                                      )))

    fig.update_layout(
        # title='Energy Consumption for Scenario ' + scenario_name,
        xaxis_title='Time in Minutes',
        yaxis_title='Cumulative Energy Consumption (Joules)', font=dict(
            family="sans serif",
            size=18,
            color="black",
        ), margin={"r": 0, "t": 0, "l": 0, "b": 0}, legend=
        dict(
            # orientation="v",
            # anchor="bottom",
            # y=1.02,
            # xanchor="right",
            # x=1.0,
            font=dict(size=18)
        ),
        template='plotly',


    )


    fig.show()
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    ))
    fig.write_image(plot_path + "cumulative_energy_plot_plotly.png", format="png", engine="kaleido",
                    width=640, height=480, scale=10.0)


if __name__ == '__main__':

    sn_dn_energy_path  = "iot_energy/aggregate_energy_sn_dn.csv"
    da_energy_path =  "iot_energy/aggregate_energy_da_longer.csv"
    sa_energy_path  =  "iot_energy/aggregate_energy_static_longer.csv"
    plot_path = "plots/result_plots/"
    cumul_plot_utility_plot_generator(sn_dn_energy_path,da_energy_path,sa_energy_path,plot_path)
    bar_plot_generator()
    cumulative_energy_plot_generator(sn_dn_energy_path,da_energy_path,sa_energy_path)



