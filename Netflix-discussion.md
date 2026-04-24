- Videos -- S3 buckets

    - Upload in db?
    - Upload in FS?
    - Upload as objects?

    - Video files are in GBs --> Peta bytes
    - Write Once, Ready by many --> WORM patten
    - Object storage --> APIs to access 
    - Data and Meta Data as well 
    - Replication high availability
    - S3 buckets --> Scalable , durable, concurrenty reads at high throughput
    - It maintains the Metadata+versioning

- Database 
    - Write heavy events --> Cassandra/Sylladb/Dynamodb(AWS)
    - Heavy reads Search for movies  --> OpenSearch(AWS)
    - For trasaction data consistancy/availability --> RDS(AWS) -> Mysql/Postgres

- Programming Language:
    - Backend
        - Microservice based architecture
        - Go/Rust --> ? Low latency and speed to start, low compute comparing with java/python

    - Frontend
        - Mobile
            - Androd/IOS -> Kotlin/Swift --> Why not flutter --> large app size, slow performer 
        - Web
            - Angular/React/Vue  --> React+TypeScript
        - Devices
            - Kotlin based Android TV Apps

- Caching (Why caching)
    - Redis , ElasticCashe(AWS)

- Message Brokers
    - Kafka -> High Throughput 

- Orchastration
    - Kubernetes (EKS) , (why not Nomad, Docker Swarm)

- Data pipelines
    s3(data lake)/HDFS,MINIO
    emr(spark)
    redshift (wareshouse)
- Data Analytics 
    Anthena (Trino)
- ML pipelines 

-- Other requirements NFR w.r.t Video
    - Latency

- In Global Data Centers across the globe (may be in multiple reagons)
    - On edge data centers
        - Vijayawada, Trivandrum, Kochi , Mangalore, Pune 
            - IPS Providers(JIO, Airtel, ACT)
            - They deploy on their primise (Edge Servers)
            - Enable Caching on gateways, routins etc
    
    netflix uses Open Connect (Their own system)
    Geo Routing 
    Geo DNS