# Real-Time Order and Payment Streaming Pipeline (McDonald's Data Simulation)

<img width="1811" height="681" alt="diagram-export-16-10-2025-10_04_08-PM" src="https://github.com/user-attachments/assets/3ab6e182-25fc-4e11-a45a-677a4764b64e" />


## Overview
This project demonstrates an **end-to-end real-time data engineering pipeline** simulating McDonald's order and payment events.  
The system ingests, processes, and analyzes streaming data using **Apache Kafka (Confluent Cloud)**, **ksqlDB**, and **MongoDB Atlas**, and visualizes real-time insights through a **Streamlit dashboard**.

The purpose of this project is to replicate how modern enterprises build **real-time analytics and monitoring platforms** — tracking transactions, detecting payment delays, and enabling instant decision-making.

---

## Business Use Case
McDonald's receives thousands of orders every minute through multiple channels (in-store, drive-thru, mobile app).  
Each order generates multiple events — orders, payments, and delivery statuses.  
The goal of this project is to **capture, process, and analyze these events in real time** to answer key business questions:

- How many orders are being placed and paid in real time?
- Which payment methods are most frequently used?
- What is the average order-to-payment delay?
- Which menu items generate the most revenue?

This solution creates a **real-time operational analytics layer**, enabling data-driven monitoring for business and operational teams.

---

## Architecture

### High-Level Flow
1. **Mock Data Generation (Python)**  
   - Generates synthetic **order** and **payment** events using Python.  
   - Each record is serialized using **Avro** and published to Kafka topics on **Confluent Cloud**.  
   - Schema management is handled by **Confluent Schema Registry**.

2. **Kafka & Schema Registry (Confluent Cloud)**  
   - Kafka acts as the **event backbone**, managing two topics:  
     - `mcd_orders` – order details  
     - `mcd_payments` – payment details  
   - Schema Registry enforces consistent Avro schema evolution and validation.

3. **Stream Processing (ksqlDB)**  
   - ksqlDB processes and joins live streams for analytics.  
   - The joined stream merges order and payment data for real-time insights.

4. **Data Sink (MongoDB Atlas)**  
   - Kafka **MongoDB Sink Connector** continuously consumes from the joined stream topic (`maacd_orders_payments_joined`)  
     and writes enriched order-payment documents to a MongoDB Atlas collection.
   - This enables real-time storage and downstream analytics.

5. **Visualization (Streamlit Dashboard)**  
   - The dashboard connects directly to MongoDB to visualize live data.  
   - Key metrics displayed:
     - Total Orders & Total Revenue  
     - Orders by Payment Method  
     - Average Order Value  
     - Recent Order Activity Timeline  

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-------------|----------|
| Data Generation | **Python**, **Avro** | Simulates order & payment events |
| Messaging Backbone | **Apache Kafka (Confluent Cloud)** | Real-time event streaming |
| Schema Management | **Confluent Schema Registry** | Avro schema validation |
| Stream Processing | **ksqlDB** | Stream joins & transformations |
| Storage | **MongoDB Atlas** | Persistent data sink |
| Visualization | **Streamlit** | Real-time analytics dashboard |
| Serialization | **Avro Serializer / Deserializer** | Compact, schema-driven event serialization |


## Setup and Execution

### Prerequisites
- Python 3.10+
- Confluent Cloud account (Kafka + Schema Registry + ksqlDB)
- MongoDB Atlas account
- Kafka Python client libraries (`confluent_kafka`, `avro`)
- Streamlit installed (`pip install streamlit pymongo pandas`)

### Steps

1. **Set up Confluent Cloud**
   - Create Kafka cluster and Schema Registry.
   - Create topics: `mcd_orders`, `mcd_payments`.
   - Create a ksqlDB cluster and run the SQL commands listed above.

2. **Run Mock Data Producer**
   - Update credentials in `mock_data_producer.py`.
   - Execute:
     ```bash
     python mock_data_producer.py
     ```

3. **Deploy MongoDB Sink Connector**
   - Use Confluent Cloud connector UI to connect joined topic (`mcd_orders_payments_joined`) to MongoDB Atlas.

4. **Launch Streamlit Dashboard**
   - Update MongoDB connection string in `app.py`.
   - Run:
     ```bash
     streamlit run app.py
     ```

5. **Observe Real-Time Insights**
   - Dashboard updates every few seconds with live orders and payments.

---

## Key Outcomes
- Built a **real-time streaming pipeline** using industry-standard tools.
- Implemented **event-driven data modeling** with Avro and Schema Registry.
- Processed and **joined live streams** with time-window semantics using ksqlDB.
- Created **end-to-end observability** from event generation to real-time visualization.

---

## Future Enhancements
- Add **Delivery stream** to monitor delivery SLAs.
- Integrate **Grafana Cloud** for metric-based alerts and monitoring.
- Build a **dedicated API layer** for dashboard queries instead of direct MongoDB access.
- Implement **stream windowing aggregations** for time-based trend analysis.

---

## Author
**Kartik Tripathi**  
Senior Data Engineer
