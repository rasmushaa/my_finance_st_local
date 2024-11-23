from backend.google_cloud.api import GoogleCloudAPI


class CategoriesAPI():

    def __init__(self):
        self.__client = GoogleCloudAPI()


    def get_expenditure_categories(self):
        sql = f"""
        SELECT
            Name
        FROM 
            {self.__client._dataset}.d_category
        WHERE
            Type = 'transaction'
        GROUP BY
            1 -- Group for case of duplication
        """
        df = self.__client.sql_to_pandas(sql) 

        return df['Name'].to_list()
    

    def get_asset_categories(self):
        sql = f"""
        SELECT
            Name
        FROM 
            {self.__client._dataset}.d_category
        WHERE
            Type = 'asset'
        GROUP BY
            1 -- Group for case of duplication
        """
        df = self.__client.sql_to_pandas(sql) 
        return df['Name'].to_list()