import pandas as pd

class DataCollector:
    def __init__(self, **kwargs):
        """ Initialize the class with user-defined member variables.
        """
        self.__dict__.update(kwargs)

    def add_from_tuple(self, items):
        """ Add member variables from a list of tuples 
        where each tuple contains a name and value.
        
        Inputs
        ------
        items : list of tuples
            [(key, value), (key2, value2), ...]
        """
        for name, value in items:
            self.__dict__[name] = value

    def add_from_list(self, key_list):
        """ Add member variables from a list of where each value is a new key, 
        and default values are Nones.

        Inputs
        ------
        key_list : list
            [key1, key2, ...]
        """
        for key in key_list:
            self.__dict__[key] = None

    def no_nones(self) -> bool:
        """ Validate that user has updated all 
        possible data entrys
        """
        for key, value in self.__dict__.items():
            if value is None:
                return False
        return True

    
    def to_dataframe(self):
        """ Convert member variables into a pandas DataFrame where
        each row contains the variable name and its value.
        """
        data = {
            'key': list(self.__dict__.keys()),
            'value': list(self.__dict__.values())
        }
        return pd.DataFrame(data)
    
    def __str__(self):
        string = 'DataCollector:\n'
        for key, value in self.__dict__.items():
            string += f'Key: {key}, Value: {value}\n'
        return string