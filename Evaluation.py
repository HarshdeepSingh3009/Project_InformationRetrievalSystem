import os, errno

class Evaluation:
    def __init__(self):
        self.relevant_doc_per_query = self.get_relevant_docs()
        self.files = self.read_files()

    def get_relevant_docs(self):
        list_of_docs_per_query = {}
        filename = "cacm.rel"
        f = open(filename,'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            x = line.split()
            if x[0] in list_of_docs_per_query:
                list_of_docs_per_query[x[0]].append(x[2])
            else:
                list_of_docs_per_query[x[0]] = [x[2]]
        return list_of_docs_per_query

    def read_files(self):
        list_of_files = []
        path = "Final_Top_100results_per_query"
        for f in os.listdir(path):
            print("getting file names")
            list_of_files.append(f)
        return list_of_files

    def create_files(self):
        final_list_values = {}
        files = self.read_files()
        path = "Final_Top_100results_per_query"
        i = 0
        q = 0
        p = 0.00
        r = 0.00
        q_p = 0.00
        r_r = 0.00
        system_name = ""
        average_p_query = {}
        reciprocal_rank_query = {}
        reciprocal_rank_model = {}
        average_p_model = {}
        p_at_5 = []
        average_p_at_5 = {}
        p_at_20 = []
        average_p_at_20 = {}
        t_r = {}
        y = 0
        model_level_details = {}
        for item in self.files:
            j = 0
            f = open(path+"/" + item, 'r')
            f.readline()
            lines = f.readlines()
            f.close()
            local_dic = {}
            p_at_5 = []
            p_at_20 = []
            for line in lines:
                j += 1
                i += 1
                x = line.split()
                if int(q) != int(x[0]):
                    if not q == 0:
                        average_p_query[q] = q_p
                        reciprocal_rank_query[q] = r_r
                    q = int(x[0])
                    p = 0.00
                    r = 0.00
                    q_p = 0.00
                    y = 0
                    system_name = x[4]

                    if x[0] in self.relevant_doc_per_query:
                        t_r[x[0]] = len(self.relevant_doc_per_query[x[0]])
                    else:
                        t_r[x[0]] = 0
                if x[0] in self.relevant_doc_per_query:
                    if x[2] in self.relevant_doc_per_query[x[0]]:
                        y += 1
                        if y == 1:
                            r_r = float(y)/int(x[1])
                        p = float(y)/int(x[1])

                        q_p += float(p)/int(t_r[x[0]])
                        r = float(y)/int(t_r[x[0]])
                        if int(x[1]) == 5:
                            p_at_5.append(float(p))
                        elif int(x[1]) == 20:
                            p_at_20.append(float(p))
                        final_list_values[i] = (x[0], x[1], x[2], x[3], str(1), str(p), str(r), x[4])
                        local_dic[j] = (x[0], x[1], x[2], x[3], str(1), str(p), str(r), x[4])
                    else:
                        p = float(y) / int(x[1])
                        r = float(y)/int(t_r[x[0]])
                        if int(x[1]) == 5:
                            p_at_5.append(float(p))
                        elif int(x[1]) == 20:
                            p_at_20.append(float(p))
                        final_list_values[i] = (x[0], x[1], x[2], x[3], str(0), str(p), str(r), x[4])
                        local_dic[j] = (x[0], x[1], x[2], x[3], str(0), str(p), str(r), x[4])
                model_level_details[x[4]] = local_dic
            average_p_model[system_name] = sum(average_p_query.values())/float(52)
            reciprocal_rank_model[system_name] = sum(reciprocal_rank_query.values())/float(52)
            average_p_at_5[system_name] = sum(p_at_5)/float(52)
            average_p_at_20[system_name] = sum(p_at_20)/float(52)
        self.write_data_to_files(final_list_values, average_p_model, reciprocal_rank_model,
                                 average_p_at_5, average_p_at_20, model_level_details)

    def make_sure_path_exists(self, path):  # checks if a directory exists and create it if not exists
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def write_data_to_files(self, final_values, average_p_model, reciprocal_rank_model,
                                 average_p_at_5, average_p_at_20, model_level_details):
        p = "Evaluation_files"
        self.make_sure_path_exists(p)
        f = open(p + "/" + "query_level_values.txt", 'w')
        f.write("QueryID" + "   " + "Rank" + "    " + "DOCID" + "    " + "     Score" + "    " + "Rel/Non-Rel"
                + "   " + "Precision" + "     " + "Recall" + "    " + "  System")
        f.write("\n")
        for item in final_values:
            f.write("{0:" ">9}".format(final_values[item][0]) + "    " + "{0:" ">4}".format(final_values[item][1])
                    + "    " + "{0:" ">6}".format(final_values[item][2]) + "   " + final_values[item][3][:5]
                    + "    " + "{0:" ">11}".format(final_values[item][4]) + "   " +
                    "{0:" ">9}".format(final_values[item][5][:5]) + "   " +"{0:" ">6}".format(final_values[item][6][:5])
                    + "    " + "{0:" "<18}".format(final_values[item][7]))
            f.write("\n")
        f.close()

        for a in model_level_details:
                f = open(p + "/" + a + ".txt", 'w')
                f.write("QueryID" + "   " + "Rank" + "    " + "DOCID" + "    " + "     Score" + "    " + "Rel/Non-Rel"
                        + "   " + "Precision" + "     " + "Recall" + "    " + "  System")
                f.write("\n")
                for item in model_level_details[a]:
                    f.write("{0:" ">9}".format(model_level_details[a][item][0]) + "    " + "{0:" ">4}".format(model_level_details[a][item][1])
                            + "    " + "{0:" ">6}".format(model_level_details[a][item][2]) + "   " + model_level_details[a][item][3][:5]
                            + "    " + "{0:" ">11}".format(model_level_details[a][item][4]) + "   " +
                            "{0:" ">9}".format(model_level_details[a][item][5][:5]) + "   " + "{0:" ">6}".format(
                        model_level_details[a][item][6][:5])
                            + "    " + "{0:" "<18}".format(model_level_details[a][item][7]))
                    f.write("\n")
                f.close()

        f = open(p + "/" + "MAP_MRR_values.txt", 'w')
        f.write("{0:" "<18}".format("System") + "     " + "Values(MAP)")
        f.write("\n")
        for item in average_p_model:
            f.write("{0:" "<18}".format(item) + "     " + str(average_p_model[item])[:6])
            f.write("\n")
        f.write("\n")
        f.write("{0:" "<18}".format("System") + "     " + "Values(MRR)")
        f.write("\n")
        for item in reciprocal_rank_model:
            f.write("{0:" "<18}".format(item)+ "     " + str(reciprocal_rank_model[item])[:6])
            f.write("\n")
        f.write("\n")
        f.write("{0:" "<18}".format("System") + "     " + "Values(P@K = 5)")
        f.write("\n")
        for item in average_p_at_5:
            f.write("{0:" "<18}".format(item) + "     " + str(average_p_at_5[item])[:6])
            f.write("\n")
        f.write("\n")
        f.write("{0:" "<18}".format("System") + "     " + "Values(P@K = 20)")
        f.write("\n")
        for item in average_p_at_20:
            f.write("{0:" "<18}".format(item) + "     " + str(average_p_at_20[item])[:6])
            f.write("\n")
        f.close()
