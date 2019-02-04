# Facebook-Bot

This project establishes a webserver on a Raspberry Pi via python Flask, on order to parse JSON data from Facebook Messenger.
The data is checked for MQTT topics, and the appropriate messages are sent via MQTT to a ESP32.
