# Croning-Naist-Lecture
授業の情報(シラバス)をWebスクレイピングで自動で入手し、データベースに保存するプログラムです。  

![操作画面](https://user-images.githubusercontent.com/53958213/119133779-41a2e080-ba77-11eb-8a0c-10fdec0290a0.png)

# セットアップ方法
gitとdocker-compose, Pythonのパッケージ管理システムであるpipを用いてセットアップができます。  
まず、gitで下記のようにコードをダウンロードします。
~~~
git clone https://github.com/murakami10/croning-naist-lecture.git
~~~  
次に、ダウンロードしたディレクトリに入り、docker-composeを用いてコンテナを立ち上げます。
~~~
cd croning-naist-lecture
docker-compose up -d
~~~
最後にPythonのパッケージを下記のようにインストールすることでセットアップは完了です。
~~~
pip install -r requirements.txt
~~~
(pipを用いるとローカルに直接ダウンロードします。ローカルの環境を汚したくない方は下記のようにpipenvなどを用いることをおすすめします。)
~~~
pipenv install
~~~  
以上でセットアップは完了です。
croning-naist-lecture配下で、以下を実行するとシラバスからWebスクレイピングすることができます。
~~~
python src/main.py
~~~
# 使用技術
- Python
- lxml
- request(Pythonのパッケージ)
- PySimpleGUI
- mongoDB
- Docker/Docker-Compose

