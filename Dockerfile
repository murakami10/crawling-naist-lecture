
FROM python:3.8.10-buster

# バイナリレイヤ下での標準出力とエラー出力を抑制
ENV PYTHONUNBUFFERED 1

ENV SRC=/usr/app
RUN mkdir -p $SRC

WORKDIR $SRC

COPY ./requirements.txt .

# インストールを行う
RUN pip install --upgrade pip && \
    pip install -r requirements.txt