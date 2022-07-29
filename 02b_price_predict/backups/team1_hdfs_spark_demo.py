# Import module
import pyspark

from pyspark.sql import SparkSession
import pyspark.sql.functions as fn
from pyspark.sql.functions import *
from pyspark.sql.types import StringType,DoubleType,IntegerType

import pyspark.pandas as ps

# spark ml module
from pyspark.ml.regression import LinearRegression
from pyspark.ml.feature import VectorAssembler
# from pyspark.ml.linalg import Vector



def set_spark_session():
    # Local mode
    # spark = SparkSession\
    #        .builder\
    #        .appName("price_predict")\
    #        .getOrCreate()

    # Standalone
    spark = SparkSession\
        .builder\
        .master("spark://bdse187.example.com:7077")\
        .config('spark.cores.max','99')\
        .config('spark.executor.memory','1G')\
        .appName("team1gogogogo")\
        .getOrCreate()


    # optimize
    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", True)
    ps.set_option("compute.default_index_type", "distributed")
    print('set spark session')
    return spark


def load_data(path):
    # load data
    df = spark.read.csv(path, inferSchema=True, header=True)
    df.createOrReplaceTempView("dfTable")

    # Select features
    df = df.select(
        '城市代碼',
        '鄉鎮市區',
        '交易標的',
        '建物移轉總面積平方公尺',
        '主建物面積',
        '建物現況格局-房',
        '車位總價元', 
        '總價元'
    )
    print('dataset loaded')
    return df


def data_processing(df):
    # data processing
    # select target without garage & land
    df = df.filter(~col('交易標的').isin(['車位', '土地']))

    # drop outliers
    df = df.filter(~(col('主建物面積') == 0))

    # change unit
    df = df.withColumn("總價元", df.總價元/10000)
    df = df.withColumn("車位總價元", df.車位總價元/10000)

    # change dtype
    df = df.withColumn("建物移轉總面積平方公尺", df["建物移轉總面積平方公尺"].cast(DoubleType()))
    df = df.withColumn("主建物面積", df["主建物面積"].cast(DoubleType()))
    df = df.withColumn("建物現況格局-房", df["建物現況格局-房"].cast(IntegerType()))
    df = df.withColumn("車位總價元", df["車位總價元"].cast(IntegerType()))
    df = df.withColumn("總價元", df["總價元"].cast(IntegerType()))

    # drop NaN columns
    df = df.dropna()
    df.count()

    print('data processing finished')
    return df


def select_city(df, city_code):
    df = df.filter(col('城市代碼') == city_code)
    return df


def dummies_encoding(df, cols_list):
    for i in cols_list:
        categ = df.select(i).distinct().rdd.flatMap(lambda x:x).collect()
        exprs = [fn.when(fn.col(i) == cat,1).otherwise(0)\
                .alias(str(cat)) for cat in categ]
        df = df.select(exprs + df.columns)
    return df  


def feature_engineering(df, city_name):
    # six municipalities 
    city_dict = {
        '台北市' : 'A',
        '新北市' : 'F',
        '桃園市' : 'H',
        '台中市' : 'B',
        '台南市' : 'D',
        '高雄市' : 'E'
    }
    city_code = city_dict[city_name]

    # select city
    select_city(df, city_code)

    # get dummies
    cols_list = ['鄉鎮市區', '交易標的'] # without '主要建材'
    df = dummies_encoding(df, cols_list)
    df = df.drop('鄉鎮市區', '交易標的', '城市代碼')

    # transform to pyspark-dataframe
    feature_cols = df.columns[:-1]
    assembler = VectorAssembler(inputCols = feature_cols, outputCol = 'features')
    df = assembler.transform(df)

    df = df.select(['features', '總價元'])
    df = df.withColumnRenamed('總價元', 'price')

    print('feature engineering finished')
    return df

# Linear regression model
def get_lr_predict(df, city_name):
    # get processed dataframe
    model_df = feature_engineering(df, city_name)

    # Build linear-regression model
    train_df, test_df = model_df.randomSplit([0.70, 0.30])

    lin_Reg=LinearRegression(labelCol='price', regParam=0.05)

    lr_model=lin_Reg.fit(train_df)

    training_predictions=lr_model.evaluate(train_df)

    # evaluate model
    test_results = lr_model.evaluate(test_df)

    print(f'{city_name}:')
    print(f'training prediction: {training_predictions.r2}')
    print(f'test result: {test_results.r2}')
    return 0

# if __name__ == "__main__":
#     sys.exit(main())


# Set spark session
spark = set_spark_session()

# load data
path = 'hdfs://bdse197.example.com/tmp/all_combined_AB.csv'
raw_df = load_data(path)

# Data processing
pr_df = data_processing(raw_df)


# Get predict
get_lr_predict(pr_df, '台北市')
get_lr_predict(pr_df, '新北市')
get_lr_predict(pr_df, '桃園市')
get_lr_predict(pr_df, '台中市')
get_lr_predict(pr_df, '台南市')
get_lr_predict(pr_df, '高雄市')
