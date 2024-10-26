# from pyspark.sql.functions import udf
# from pyspark.sql.types import StringType


def extract_text_from_pdf(input_table, output_table):
    pass
    # TODO: use spark global in Databricks context
    # spark = get_spark_session()
    # df = spark.read.format("delta").table(input_table)

    # # UDF to extract text
    # def pdf_to_text(binary_content):
    #     # Implement text extraction logic
    #     pass

    # pdf_to_text_udf = udf(pdf_to_text, StringType())
    # result_df = df.withColumn("text", pdf_to_text_udf(df["content"]))

    # result_df.write.format("delta").mode("overwrite").saveAsTable(output_table)
