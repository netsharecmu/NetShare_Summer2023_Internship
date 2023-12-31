import pandas as pd
import numpy as np
import collections
import ipaddress
from datetime import datetime
import json
import re
from .preprocessor import Preprocessor


class csv_pre_processor(Preprocessor):
    def __init__(self, input_dataset_path, output_dataset_path, input_config_path, output_config_path):
        super().__init__(input_dataset_path, output_dataset_path, input_config_path, output_config_path)
        self.df = pd.read_csv(input_dataset_path, index_col=0)
        ## special fields store list, IP, time columns and its encoding method.
        self.abnormal_lists = [] 
        self.abnormal_columns = []
        self.special_fields = {}
        self.changed_columns = {}
        self.fields = []
        self.name_lists = collections.defaultdict(list)

    def create_configuration_file(self):
        with open(self._input_config_path, 'r') as openfile:
            json_object = json.load(openfile)
        openfile.close()
        self.abnormal_lists = [0, 0.0, -1, "-1", "NaN", "nan"]
        self.delete_columns = {}
        for field in ["metadata", "timeseries", "timestamp"]:
            for col in json_object["fields"][field]:
                params = {}
                for k, v in col.items():
                    params[k] = v
                res1 = self.detect_abnormal_value(params["name"])
                if res1 == True:
                    res2 = self.create_json_obj(json_object, field, params)
                if res2 == False:
                    if field not in self.delete_columns:
                        self.delete_columns[field] = {}
                    self.delete_columns[field][col["name"]] = col
        json_object["global_config"]["original_data_file"] = str(self._output_dataset_path)
        json_object.pop("fields")
        json_object = json.dumps(json_object, indent=4)
        
        with open(self._output_config_path, "w") as outfile:
          outfile.write(json_object)

    def get_obj(self, column, encoding, params):
        if encoding == "bit":
            n_bits, categorical_mapping = 32, False
            if "n_bits" in params:
                n_bits = params["n_bits"]
            if "categorical_mapping" in params:
                categorical_mapping = params["categorical_mapping"]
            obj = {
                "column": column,
                "type": "integer",
                "encoding": "bit",
                "n_bits": n_bits,
                "categorical_mapping": categorical_mapping
            }
        elif encoding == "word_proto":
            obj = {
                "column": column,
                "type": "integer",
                "encoding": "word2vec_proto"
            }
        elif encoding == "categorical":
            obj = {
                "column": column,
                "type": "string",
                "encoding": "categorical"
            }
        elif encoding == "float":
            normalization, log1p_norm = "ZERO_ONE", True
            if "normalization" in params:
                normalization = params["normalization"]
            if "log1p_norm" in params:
                log1p_norm = params["log1p_norm"]
            obj = {
                "column": column,
                "type": "float",
                "normalization": normalization,
                "log1p_norm": log1p_norm
            }
        elif encoding == "timestamp":
            normalization, generation = "ZERO_ONE", True
            if "normalization" in params:
                normalization = params["normalization"]
            if "generation" in params:
                generation = params["generation"]
            obj = {
                "column": column,
                "generation": generation,
                "encoding": "interarrival",
                "normalization": normalization
            }
        else:
            obj = {
                "column": column,
                "type": "integer",
                "encoding": "word2vec_port"
            }
        return obj

    def judge_para_exist(self, col_name, params):
        if col_name in params:
            return params[col_name]
        else:
            return None

    def create_json_obj(self, json_object, Fields, params):
        # Fields: "metadata", "timestamp", "timeseries"
        # column: column name in dataset
        # format: data format {integer, float, string, timestamp, IP, list}
        # encoding: {bit, word_port, word_proto, float, list_attribute, list_value}
        # type: None or specific value for IP or timestamp (IP: IPv4, IPv6 Timestamp: processed, unprocessed)
        # names: values in the list
        column, format, encoding = params["name"], params["format"], params["encoding"]
        type = self.judge_para_exist("type", params)
        names = self.judge_para_exist("names", params)
        delimiter = self.judge_para_exist("delimiter", params)
        time_format = self.judge_para_exist("time_format", params)
        if format == "integer":
            ## format is integer: encoding will include { bit, word_proto, word_port, categorical }
            if self.df.dtypes[column] == object:
                print('Column ', column, ' may not be integer, so we ignore it.')
                return False
            obj = self.get_obj(column, encoding, params)
            self.fields.append(column)
            json_object["pre_post_processor"]["config"][Fields].append(obj)
        elif format == "string":
            ## format is string: encoding will include { categorical }
            if self.df.dtypes[column] != object:
                print('Column ', column, ' may not be string, so we ignore it.')
                return False
            obj = self.get_obj(column, encoding, params)
            self.fields.append(column)
            json_object["pre_post_processor"]["config"][Fields].append(obj)
        elif format == "float":
            ## format is string: encoding will include { float }
            obj = self.get_obj(column, encoding, params)
            self.fields.append(column)
            json_object["pre_post_processor"]["config"][Fields].append(obj)
        elif format == "timestamp":
            if type == "unprocessed":
                self.special_fields[column] = "timestamp"
                self.changed_columns[column] = {}
                self.changed_columns[column]["encoding"] = "timestamp"
                self.changed_columns[column]["time_format"] = time_format
            obj = self.get_obj(column, "timestamp", params)
            self.fields.append(column)
            json_object["pre_post_processor"]["config"][Fields] = (obj)
        elif format == "IP":
            if self.df.dtypes[column] != object:
                print('Column ', column, ' may not be IP address, so we ignore it.')
                return False
            if type == "IPv4":
                self.special_fields[column] = "IPv4"
                self.changed_columns[column] = "IPv4"
            else:
                self.special_fields[column] = "IPv6"
                self.changed_columns[column] = "IPv6"
            obj = self.get_obj(column, "bit", params)
            self.fields.append(column)
            json_object["pre_post_processor"]["config"][Fields].append(obj)
        elif format == "list":
            ## name_lists =  {"packet__layers": ["IP", "TCP", ....]}
            ## format is list --> encoding is "list_attributes", "list_values"
            if encoding == "list_attributes":
                for name in names:
                    ## special_fields = {"packet__layers": "list__attributes", "IP__src_s": "IPv4"}
                    obj = self.get_obj(column + "_" + name, "categorical", params)
                    self.fields.append(column + "_" + name)
                    json_object["pre_post_processor"]["config"][Fields].append(obj)
                    self.name_lists[column].append(name)
                    self.df[column + "_" + name] = "No"
                    if column not in self.changed_columns:
                        self.changed_columns[column] = {}
                        self.changed_columns[column]["encoding"] = "list_attributes"
                        self.changed_columns[column]["new_columns"] = []
                        self.changed_columns[column]["delimiter"] = delimiter
                    self.changed_columns[column]["new_columns"].append(column + "_" + name)
                    self.special_fields[column] = "list_attributes"
            else:
                ##  current supported version for list values: xxx = xxxx
                for name, encoding in names.items():
                    self.fields.append(column + "_" + name)
                    self.name_lists[column].append(name)
                    obj = self.get_obj(column + "_" + name, encoding, params)
                    if column not in self.changed_columns:
                        self.changed_columns[column] = {}
                        self.changed_columns[column]["encoding"] = "list_values"
                        self.changed_columns[column]["new_columns"] = {}
                        self.changed_columns[column]["delimiter"] = delimiter
                    self.changed_columns[column]["new_columns"][column + "_" + name] = {"encoding": encoding, "origin": name}
                    json_object["pre_post_processor"]["config"][Fields].append(obj)
                self.special_fields[column] = "list_values"
        return True

    def handle_special_fields(self):
        for i in range(len(self.df.index)):
            for col, encoding in self.special_fields.items():
                if encoding == "list_attributes" or encoding == "list_values":
                    if encoding == "list_attributes":
                        delimiter = self.changed_columns[col]["delimiter"]
                        for item in self.df.loc[i, col].split(delimiter):
                            if col in self.name_lists and item in self.name_lists[col]:
                                self.df.loc[i, col + "_" + item] = "Yes"
                    elif encoding == "list_values":
                        origin_strings = self.df.loc[i, col]
                        delimiter = self.changed_columns[col]["delimiter"]
                        for new_col, attrs in self.changed_columns[col]["new_columns"].items():
                            if origin_strings == -1 or origin_strings == "unavailable":
                                if attrs["encoding"] == "string":
                                    self.df.loc[i, new_col] = "Unavailable"
                                else:
                                    self.df.loc[i, new_col] = 0
                            else:
                                match = re.search(attrs["origin"], origin_strings)
                                strs = origin_strings[match.end() + 1:].split(delimiter)[1].strip(' ')
                                if strs == "":
                                    if attrs["encoding"] == "categorical":
                                        self.df.loc[i, new_col] = "Unavailable"
                                    else:
                                        self.df.loc[i, new_col] = 0
                                elif " " in strs:
                                    if attrs["encoding"] == "categorical":
                                        if strs.split("\n")[0] == "":
                                            self.df.loc[i, new_col] = "Unavailable"
                                        else:
                                            self.df.loc[i, new_col] = strs.split("\n")[0]
                                    else:
                                        if strs.split("\n")[0] == "":
                                            self.df.loc[i, new_col] = 0
                                        else:
                                            self.df.loc[i, new_col] = int(strs.split("\n")[0])
                                else:
                                    if attrs["encoding"] == "categorical":
                                        if strs.split("\n")[0] == "":
                                            self.df.loc[i, new_col] = "Unavailable"
                                        else:
                                            self.df.loc[i, new_col] = strs
                                    else:
                                        if strs.split("\n")[0] == "":
                                            self.df.loc[i, new_col] = 0
                                        else:
                                            self.df.loc[i, new_col] = int(strs)
                elif encoding == "IPv4" or encoding == "IPv6":
                    self.convert_IP_to_int(i, self.df.loc[i, col], col, encoding)
                else:
                    time_format = self.changed_columns[col]["time_format"]
                    self.convert_time_to_ns(i, col, time_format)

    def convert_IP_to_int(self, i, orig_ip, colname, type):
        if '.' in orig_ip and type == "IPv4":
            IP__addr = ipaddress.IPv4Address(orig_ip)
            self.df.loc[i, colname] = int(IP__addr)
        elif '.' in orig_ip and type == "IPv6":
            IP__addr = ipaddress.IPv4Address(orig_ip)
            self.df.loc[i, colname] = int(IP__addr)
        else:
            self.df.loc[i, colname] = 0

    def convert_time_to_ns(self, i, col, time_format):
        datetime_str = self.df.loc[i, col]
        strs = datetime.strptime(datetime_str, time_format)
        date64 = np.datetime64(strs)
        ts = (date64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's') * 100000
        ts = int(ts)
        self.df.loc[i, col] = ts

    ## check if one column in df exists -1 or NaN. If all values are abnormal, we delete it, otherwise we change it to 0 
    def detect_abnormal_value(self, col):
        if self.df[col].isin(self.abnormal_lists).any():
            if self.df[col].isin(self.abnormal_lists).all():
                print("all the values in ", col, " are abnormal, so we delete it")
                return False
            else:
                self.abnormal_columns.append(col)
        return True

    def change_abnormal_value(self):
        for col in self.abnormal_columns:
            self.df[col] = self.df[col].replace(self.abnormal_lists, 0)
            self.df[col] = self.df[col].fillna(0)

    def _preprocess(self):
        self.create_configuration_file()
        self.handle_special_fields()
        self.change_abnormal_value()
        for col, v in self.special_fields.items():
            if v == "IPv4" or v == "IPv6" or v == "timestamp":
                self.df[[col]] = self.df[[col]].apply(pd.to_numeric)
            if v == "list_values":
                for new_col, attrs in self.changed_columns[col]["new_columns"].items():
                    if attrs["encoding"] == "bit":
                        self.df[new_col] = self.df[new_col].astype(int)
        print("fields are ", self.fields)
        self.df = self.df[[i for i in self.fields]]
        with open(self._input_config_path) as json_file:
            data = json.load(json_file)
        data['changed_fields'] = self.changed_columns
        #for col in self.deleted_columns:
         #   for element in data["fields"][col['fields']]:
          #      if element["name"] == col["name"]:
           #         print("delete col is ", col["name"])
            #        print(element)
             #       data["fields"][col['fields']].remove(element)
        print("data is ")
        print(data)
        with open(self._output_config_path, 'w') as json_file:
            json.dump(data, json_file)
        self.df.to_csv(self._output_dataset_path, index=False)

