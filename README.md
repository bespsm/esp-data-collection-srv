SERVER SIDE FOR ESP DATA COLLECTION PROJECT
===========================================

This repository collects the data that is deployed to EC2 server instance over terraform configs.
- In folder "scripts" are located the python scripts that forwards all MQTT messages to DynamoDB
- In folder "grafana_cfg" are located configs for the datasource (prometheus) and for ESP32 data collection dashboard

License
=======

MIT License, see [LICENSE](LICENSE).