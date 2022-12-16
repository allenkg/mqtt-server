# Simple python server


#### The goal is to write a service to communicate between MQTT and telnet via text messages


# How To Run and Test

#### Start the server 
> install requirements
> pip3 install -r requirements.txt

``` python3 server.py```

#### Run telnet-client

Open terminal and run command

```telnet 127.0.0.1 1234```


#### Text command in telnet-client

1. To subscribe to topic

    ```subscribe topic1/#```

2. To start polling messages from MQTT
   ```poll```


#### Public messages into the topic

> Download [mosquitto](https://mosquitto.org/ "Title")

Open terminal and run 

```mosquitto_pub -t topic1/foo -m "topic message" -h mqtt.eclipseprojects.io```





