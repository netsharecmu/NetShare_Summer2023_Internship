import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import ipaddress
from datetime import datetime
import glob 
import json 
import ipaddress
from .postprocessor import Postprocessor
pd.set_option('display.max_columns', None)


class csv_post_processor(Postprocessor):
    def __init__(self, input_dataset_path, output_dataset_path, input_config_path):
        super().__init__(input_dataset_path, output_dataset_path, input_config_path)
        self.input_path = input_dataset_path
        self.output_path = output_dataset_path
        self.metadata = []
        with open(input_config_path) as json_file:
            json_object = json.load(json_file)
            self.changed_fields = json_object["changed_fields"]
            self.columns = []
            for item in json_object["pre_post_processor"]["config"]["metadata"]:
                self.columns.append(item["column"])
                self.metadata.append(item["column"])
            for item in json_object["pre_post_processor"]["config"]["timeseries"]:
                self.columns.append(item["column"])
            self.columns.append(json_object["pre_post_processor"]["config"]["timestamp"]["column"])
        filenames = glob.glob(str(self.input_path) + "/*.csv")
        self.df = pd.read_csv(filenames[0]) 

    def convert_int_to_IP(self, i, int_ip, colname, ip_type):
        int_ip = int(int_ip)
        if int_ip == 0:
            self.df.loc[i, colname] = int(int_ip)
        elif ip_type == "IPv4": 
            IP__addr = str(ipaddress.IPv4Address(int_ip))
            self.df.loc[i, colname] = IP__addr
        elif ip_type == "IPv6":
            IP__addr = str(ipaddress.IPv6Address(int_ip))
            self.df.loc[i, colname] = IP__addr

    def convert_ns_to_time(self, i, colname, time_format):
        ts = self.df.loc[i, colname] 
        date64 = (ts / 100000) * np.timedelta64(1, 's') + np.datetime64('1970-01-01T00:00:00Z')
        datetime = date64.item().strftime(time_format)
        self.df.loc[i, colname] = datetime

    def generate_flow_id(self):
        self.df = self.df.sort_values(self.metadata)
        s = self.df.duplicated(self.metadata)
        self.df["flow_id"] = (~s).cumsum()
        
    def _postprocess(self):
        self.generate_flow_id()
        for col, encoding in self.changed_fields.items():
            if encoding == "IPv4" or encoding == "IPv6": 
                for i in range(len(self.df.index)):
                    self.convert_int_to_IP(i, self.df.loc[i, col], col, encoding)
            else:
                if encoding["encoding"] == "list_attributes": 
                    self.df[col], cols = "", []
                    for i in range(len(self.df.index)):
                        categories = encoding["new_columns"]
                        for c in categories:
                            if c not in cols: 
                                cols.append(c)
                            if self.df.loc[i, c] == "Yes":
                                label = c.split("_")[-1]
                                if len(self.df.loc[i, col]) == 0:
                                    self.df.loc[i, col] += label
                                else:
                                    self.df.loc[i, col] += encoding["delimiter"] + label
                    self.df = self.df.drop(columns = cols)
                elif encoding["encoding"] == "timestamp":
                    time_format = encoding["time_format"]
                    for i in range(len(self.df.index)):
                        self.convert_ns_to_time(i, col, time_format)
                else: 
                    self.df[col], cols = "", []
                    for i in range(len(self.df.index)):
                        columns = encoding["new_columns"]
                        string_lists, cols = [], []
                        for item in columns: 
                            if item not in cols: 
                                cols.append(item)
                            string_lists.append(columns[item]["origin"] + encoding["delimiter"] + str(self.df.loc[i, item]))
                        final_string = "\n".join(string_lists)
                        self.df.loc[i, col] = final_string
                    self.df = self.df.drop(columns = cols)
        self.df.to_csv(self.output_path, index = False)