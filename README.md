Unified Cross-posting and Aggregation hub Manager


(TODO: properly format README)

Software for cross-posting and aggregation of content in social networks

Pull and setup docker container:
(TODO: create script for it)

    sudo docker pull  cassandra:3.11
    sudo docker run  --name cassandra_db -p 9042:9042 -d cassandra:3.11
    docker exec -it cassandra_db /bin/bash    
    apt update
    apt install python3-pip
    pip3 install cassandra-driver



Migrate db (from /UCAH-Manager/loader):
(TODO: implement script for this)

    python3 ./manage.py sync_cassandra


Create and prepare virtual environment (from /UCAH-Manager):

    python3.10 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
    python3.10 -m pip install --upgrade pip



Run script for start container with cassandra (from /UCAH-Manager/.ci) 
    
    cassandra_start.sh

Sync db:

    python3.10 manage.py makemigrations
    python3.10 manage.py syncdb
    python3.10 manage.py migrate --run-syncdb


Run app:
    
    python manage.py runserver





Getting VK oath token:

    https://oauth.vk.com/authorize?client_id=8194798&display=page&redirect_uri=https://vk.com/luciole7&scope=offline,wall,manage,photos,wall,offline,docs,groups&response_type=token&v=5.131&state=123456
    
    where client_id - id of standalone APP
    https://example - page of redirection
    
    then copy token for access to API methods



https://oauth.vk.com/authorize?client_id=8194798&display=page&redirect_uri=https://vk.com/luciole7&scope=manage,photos,messages,wall,offline,docs,groups,stats&response_type=token&v=5.131&state=123456