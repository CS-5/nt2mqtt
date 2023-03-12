# nt2mqtt
WPILib FRC Network Tables to MQTT

## Goals

- Stream live data from the robot to Grafana during test/practice
  - Useful for troubleshooting and testing
  - Same data being sent to the dashboard
- Store data for later analysis
  - Lower-resolution version of the streaming data
  - Use Grafana for post-match analysis of critical systems and sensors
  - Time syncronization to correlate data with points during the match

## Overview

The general flow is as follows:

```mermaid
flowchart
    NT["Network Tables"]--NT Protocol-->Bridge
    Bridge--MQTT Protocol-->Mosquitto
    Mosquitto--Live Stream API-->Grafana
    Mosquitto--Telegraf MQTT Sub-->Telegraf
    Telegraf--HTTP API-->InfluxDB
    InfluxDB--Stored Metrics Query-->Grafana
```