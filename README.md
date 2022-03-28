Unified Cross-posting and Aggregation Hub Manager


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





