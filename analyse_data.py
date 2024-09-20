import os
import pandas as pd


def get_data(path: str)->pd.DataFrame:
    """
    Read the data.

    Arguments:
    ---------
        path: path to the data.
    """
    df = pd.read_csv(path)
    return df


def group_and_aggregate_data_by_country(path: str=os.path.join("data", "tourism_dataset.csv"))->pd.DataFrame:
    """
    Group and Aggregate Data: Group the data by the 'country' column and calculate
    the average value of the "Rating" column for each country. Please include the
    equivalent SQL query as a comment.

    Arguments:
    ---------
        path: path to the data.
              default set to 'data/tourism_dataset.csv' by default

    Returns:
    --------
        df_aggregated: aggregated data giving the average rating per country.


    Alternative SQL command:
    ------------------------
    The source of the data is a csv file located at 'data/tourism_dataset.csv'.
    To aggregate the data as in pandas I will use a CTAS syntax from Apache Spark SQL


    Apache Spark SQL
    ----------------
    CREATE TABLE IF NOT EXISTS tourism_aggreagte AS
    SELECT 
        Country, 
        AVG(Rating) as average_country_rating
    FROM 
        csv.`data/tourism_dataset.csv`
    GROUP BY 
        Country;
    """
    df = get_data(path)
    df_aggregated = df.groupby(by='Country').aggregate({'Rating':'mean'}).rename(columns={'Rating':'average_country_rating'})
    df_aggregated = df_aggregated.reset_index()
    return df_aggregated
    

def get_top_category(path: str=os.path.join("data", "tourism_dataset.csv")):
    """
    Find the top 3 categories with the highest average rate
    across all countries. Please include the equivalent SQL query as a comment.



    Alternative SQL command:
    ------------------------
    The source of the data is a csv file located at 'data/tourism_dataset.csv'.
    To aggregate the data as in pandas I will use a CTAS syntax from Apache Spark SQL


    Apache Spark SQL
    ----------------
    CREATE TABLE IF NOT EXISTS tourism_top_three_categories AS
    SELECT 
        Category, 
        AVG(Rating) as average_rating_category
    FROM 
        csv.`data/tourism_dataset.csv`
    GROUP BY 
        Category
    ORDER BY 
        average_rating_category DESC
    LIMIT 3;

    """
    df = get_data(path)
    df_avg_category = df.groupby(by='Category').aggregate({'Rating':'mean'}).rename(columns={'Rating':'average_rating_category'})
    df_top_three_category = df_avg_category.nlargest(3, 'average_rating_category').reset_index()
    return df_top_three_category


def save_analysis_results(path_country_aggregate: str, 
                          path_to_category_aggregate: str)->None:
    """
    Saves the analysis results to csv.

    Arguments:
    ----------
        path_country_aggregate: path to country aggregate data
        path_to_category_aggregate: path to category aggregate

    Returns
    -------
        None
    """
    df_country_agg = group_and_aggregate_data_by_country()
    df_category_agg = get_top_category()
    df_country_agg.to_csv(path_country_aggregate)
    df_category_agg.to_csv(path_to_category_aggregate)
    print(f"Saved country aggregate data to {path_country_aggregate}")
    print(f"Saved category aggregate data to {path_to_category_aggregate}")




if __name__ =="__main__":
    base_path = "data"
    path_country_aggregate = os.path.join(base_path,"country_aggregate_tourism_dataset.csv")
    path_to_category_aggregate = os.path.join(base_path,"category_aggregate_tourism_dataset.csv")
    save_analysis_results(path_country_aggregate, path_to_category_aggregate)