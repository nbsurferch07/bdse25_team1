# Import module
import pyspark

from pyspark.sql import SparkSession
import pyspark.sql.functions as fn
from pyspark.sql.functions import *
# from pyspark.sql.types import StringType,DoubleType,IntegerType

import pyspark.pandas as ps

# spark ml module
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler
# from pyspark.ml.linalg import Vector



def set_spark_session():
    # Local mode
    spark = SparkSession\
            .builder\
            .appName("price_predict")\
            .getOrCreate()
    
    # optimize
    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", True)
    ps.set_option("compute.default_index_type", "distributed")
    return spark

def load_data(path):
    # load data 
    df = spark.read.csv(path, inferSchema=True, header=True)
    df.createOrReplaceTempView("dfTable")
    
    # Select features
    df = df.select(
        '鄉鎮市區', 
        '交易標的', 
        '建物移轉總面積平方公尺',
        '主建物面積', 
        '建物現況格局-房', 
        '車位總價元', 
        '總價元'
    )
    
    return df


def dummies_encoding(df, cols_list):
    for i in cols_list:
        categ = df.select(i).distinct().rdd.flatMap(lambda x:x).collect()
        exprs = [fn.when(fn.col(i) == cat,1).otherwise(0)\
                .alias(str(cat)) for cat in categ]
        df = df.select(exprs + df.columns)
    return df    


def feature_engineering(df):
    # data processing
    df = df.filter(~col('交易標的').isin(['車位', '土地']))
    
    # get dummies
    cols_list = ['鄉鎮市區', '交易標的'] # without '主要建材'
    df = dummies_encoding(df, cols_list)
    df = df.drop('鄉鎮市區', '交易標的')
    
    # transform to pyspark-dataframe
    feature_cols = df.columns[:-1]
    assembler = VectorAssembler(inputCols = feature_cols, outputCol = 'features')
    df = assembler.transform(df)

    model_df = df.select(['features', '總價元'])
    model_df = model_df.withColumnRenamed('總價元', 'price')
    
    return model_df


def get_predict(model_df):
    
    # Linear regression model
    # Build linear-regression model
    train_df, test_df = model_df.randomSplit([0.70, 0.30], seed=2)
    
    lin_Reg=LinearRegression(labelCol='price', regParam=0.05)
    
    lr_model=lin_Reg.fit(train_df)
    
    training_predictions=lr_model.evaluate(train_df)
    
    # evaluate model
    test_results = lr_model.evaluate(test_df)
    
    print(f'training prediction : {training_predictions.r2}')
    print(f'test result : {test_results.r2}')

    
# if __name__ == "__main__":
#     sys.exit(main())


# Set spark session
spark = set_spark_session()

# load data
path = 'file:///home/dtsurfer07/00_final_project_tutorial/dataset/all_A_台北市_A.csv'
df = load_data(path)

# Data processing
model_df = feature_engineering(df)

# Get predict
get_predict(model_df)