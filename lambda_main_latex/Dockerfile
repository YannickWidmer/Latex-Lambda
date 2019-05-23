FROM lambci/lambda:build-python3.6





FROM lambci/lambda:build-python3.6

WORKDIR /var/task


COPY --from=0 /var/task/ /var/task/
COPY python_packages/ /var/task

COPY lambda_function.py /var/task