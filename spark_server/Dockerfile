FROM jupyter/pyspark-notebook

RUN pip install redis

CMD python /home/code/top_ten_cart_items.py > /home/data/top_ten_cart_items.log

CMD sleep infinity