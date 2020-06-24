'''
    Copyright 2020 Google LLC

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        https://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    
    Date: 6/8/2020
    Author: Haoran Fei
    A class to load a small batch of sample data in json or csv format to memory as a
    structured data object (currently only supporting Pandas DataFrame). SQL-like
    operations and further analysis will then be performed using the data object.

'''
import pandas as pd

class Loader:
    '''
        Data Loader Class. Loads batch of data files into in-memory objects and pass to user.
        Instand Variables:
            self.df: the dataframe that combines all loaded data files. Keeps
                     the common columns and all rows.
        Public Methods:
            load_json: loads json files.
            load_csv: loads csv files.
            get_data: returns the loaded in-memory object. Defaults to Pandas Dataframe.
    '''

    placeholder = "##"

    def __init__(self):
        self.df = None # pylint: disable=C0103

    def _get_file_names(self, file_path_format_str, range_start, range_end):
        '''Get the file names of data files using the input pattern, starting index and ending
        index. Replace "##" placeholder with two-digit number. '''
        data_file_names = []
        for i in range(range_start, range_end):
            if i < 10:
                data_file_names.append(file_path_format_str.replace(self.placeholder, "0"+str(i)))
            else:
                data_file_names.append(file_path_format_str.replace(self.placeholder, str(i)))
        return data_file_names


    def load_json(self, file_path_format_str, range_start, range_end, out_format="df"):
        '''Load a batch of json data files. Always assume record layout: the file must
        be formatted like {col1->val, col2->val}, {col1->val, col2->val}, ... '''
        data_file_names = self._get_file_names(file_path_format_str, range_start, range_end)

        if out_format == "df":
            for file_name in data_file_names:
                current_frame = pd.read_json(path_or_buf=file_name,
                                             orient="records", typ="frame", lines=True)
                if self.df is None:
                    self.df = current_frame
                else:
                    self.df = self.df.merge(right=current_frame, how="outer")
                    
    def load_csv(self, file_path_format_str, range_start, range_end, out_format="df"):
        '''Load a batch of csv files'''


    def get_data(self, out_format="df"):
        '''Return the current loaded data files as single output object. Files are automatically
        combined upon loading. Currently only supports Pandas DataFrame. '''
        if out_format == "df":
            print("{} revisions loaded".format(self.df.shape[0]))
            return self.df
        return None

def _test():
    pass

if __name__ == "__main__":
    _test()
