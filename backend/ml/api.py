import pandas as pd
import numpy as np
import os
import pickle
import datetime
from backend.ml.model import NB
from backend.google_cloud.api import GoogleCloudAPI



class MLAPI():
    def __init__(self):
        self.__client = GoogleCloudAPI()
        self.__model = None
        self.__model_name = 'ai_model.pkl'
        self.__nan = 'N/A'


    def predict(self, data: pd.DataFrame):
        """ Reuturns the predicted target Classes.
        
        The model returns a dict containing all the classes,
        in descending order, The first class is selected,
        and the prortional probability to the total pool 
        is also returned.

        Inputs
        -----
        data: pd.DataFrame
            Input X Features

        Returns
        -------
        y_predicted: list
            Model y ouputs. If model is not loaded, fill all values by <self.__nan>

        realative_pob: list
            The Prob of returned classe, in relation to the total pool
        """
        if self.__model is None:
            return [self.__nan] * len(data), [0] * len(data)
        
        preds = self.__model_get_predictions(data)

        def relative_prob(pred_dict):
            target_prob = next(iter(pred_dict.values()))
            total_prob = sum(pred_dict.values())
            return target_prob / total_prob

        probs= [relative_prob(pred_dict) for pred_dict in preds]
        targets = [next(iter(pred_dict.keys())) for pred_dict in preds]

        return targets, probs


    def pull_training_data(self):
        """ Select required columns from the database
        """
        sql=f"""
        SELECT
            KeyDate as date,
            Receiver as receiver,
            Amount as amount,
            Category as category
        FROM
            {self.__client._dataset}.f_transactions
        WHERE
            Category != 'N/A'
        """
        df = self.__client.sql_to_pandas(sql)
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d').dt.date
        df.sort_values('date', inplace=True)
        df = df.dropna().reset_index(drop=True)
        return df
    
        
    def train_new_model(self, data:pd.DataFrame, target_col:str):
        """ Trains and activate a new model, but does not save it automatically

        The input dataframe can contain any amount of features, with different datatypes,
        since those are automatically processed in the API.
        The model can have any number of features, as long as string, and floats are 
        given to correct input variable.

        Inputs
        ------
        data : pd.DataFrame
            All columns are used to train the model

        target_col : str
            The name of the y actuall target classes
        """
        data = data.loc[(data[target_col].notnull()) & (data[target_col] != 'N/A')] # All rows must have a target
        data = data.fillna('') 
        X_numeric = data.select_dtypes(include=['float']).to_numpy()
        X_string = data.drop(target_col, axis=1).select_dtypes(include=['object']).to_numpy()
        y = data[target_col].to_numpy()

        nb = NB()
        nb.fit(X_string, X_numeric, y)
        self.__model = nb


    def save_model_to_gcs(self):
        """ Save a model to a file locally using pickle 
        and upload it to Google Cloud Storage with corresponding ENV prefix
        """
        with open(self.__model_name, 'wb') as f: # Save the model locally
            pickle.dump(self.__model, f)

        self.__client.upload_file_to_gcs(self.__model_name) # Initialize a GCS client and upload the file


    def load_model_from_gcs(self):
        """ Download a model from GCS to the local filesystem,
        and pickle load it.
        """
        self.__client.download_file_from_gcs(self.__model_name) # Pull the file from GCS to Local system
        
        if os.path.isfile(self.__model_name):
            with open(self.__model_name,'rb') as f: # Open the local File
                self.__model = pickle.load(f)


    def get_priors(self) -> dict:
        """ Returns the prior probabilities of all targets
        in descending order as a dict.
        """
        if self.__model is not None:
            return self.__model.get_priors()
        else:
            return {}
        

    def get_likelihoods(self, ntop: int = 20):
        """ Returns the likelihoods for all possible feature token
        and ascending order.
        The Dict is format likes[<target_name>][<toke>]:value
        All levels are in descending order, and all targets contain 
        all possible tokens

        Inputs
        -----
        ntop : int
            Select only the top n tokens
        """
        if self.__model is not None:
            likes = self.__model.get_likelihoods()
            return {key: dict(list(sub_dict.items())[:ntop]) for key, sub_dict in likes.items()}
        else:
            return {}
        

    def validate_model(self, data:pd.DataFrame, target_col:str, accepted_error=1):
        """ Returns the Accuracy information for the given model.

        Inputs
        ------
        data : pd.DataFram
            Validation dataframe
        
        target_col : str
            Name of the target column
        
        accepted_error : int
            The maximum allowed deviation from the first place of the target list.
            The model return a list of all available classes in the order of 
            the propability, and some deviation is allowed when computing the 
            overall accuracy (usefulnes) of the model
        """
        y_predicted = self.__model_get_predictions(data.drop(target_col, axis=1))
        wa, stats = self.__get_statistics(y_predicted, y_valid=data[target_col].to_numpy(), accepted_error=accepted_error)
        return wa, stats
    

    def has_model(self):
        """ Used to check if the model has been initialized
        """
        return self.__model is not None
    

    def __model_get_predictions(self, data: pd.DataFrame)->dict:
        """ Run model prediction
        
        Returns
        -------
        predictions : dict
            A dictionary containing all target classe in descending order of the propability
        """
        data = data.fillna('') 
        data = data.drop(columns=[col for col in data.columns if any(isinstance(val, (datetime.date, datetime.datetime)) for val in data[col])]) # Remove the Date-type column
        X_numeric = data.select_dtypes(include=['float']).to_numpy()
        X_string = data.select_dtypes(include=['object']).to_numpy()
        preds = self.__model.predict(X_string, X_numeric)
        return preds


    def __get_statistics(self, y_predicted: list, y_valid: list, accepted_error: int):
        """ A helper function to compute accuracy statistics for the trained model.

        Inputs
        ------
        y_predicted : list
            Model ouputs for the predicted target classes

        y_valid: list
            Actual target classes

        accepted_error : int
            The maximum allowed deviation from the first place of the target list.
            The model return a list of all available classes in the order of 
            the propability, and some deviation is allowed when computing the 
            overall accuracy (usefulnes) of the model
        """
        def get_accuracy(df_group):
            count = df_group.shape[0]
            trues = df_group.loc[df_group['acceptable'] == True].shape[0]
            return trues / count

        errors = []
        labels = []
        for i, row in enumerate(y_predicted):
            try:
                errors.append(int(list(row.keys()).index(y_valid[i])))
                labels.append(y_valid[i])
            except ValueError:
                pass
        df_errors = pd.DataFrame(zip(labels, errors), columns=['y_valid', 'order'])

        df_accuracy = df_errors.copy()
        df_accuracy['acceptable'] = df_accuracy['order'] <= accepted_error
        df_accuracy = df_accuracy.groupby(['y_valid']).apply(lambda x: get_accuracy(x)).rename('accuracy').reset_index()
        
        df_stats = df_errors.groupby('y_valid').agg(count=('order', 'count'),
                                                    place_q50=('order', lambda x: np.percentile(x, 50)),
                                                    ).reset_index()
        
        df_stats = pd.merge(df_stats, df_accuracy, left_on='y_valid', right_on='y_valid')
        df_stats = df_stats.sort_values(by='count', ascending=False).reset_index(drop=True)

        w_accuracy = np.average(df_stats['accuracy'].values, weights=df_stats['count'].values) # Weighted accuracy
        return w_accuracy, df_stats