# Network-Simulator-for-Layer-2-Switch-Performance
**Overview**


This project, Network Simulator for Layer 2 Switch Performance, focuses on implementing and simulating the behavior of Layer 2 (L2) switches in a network. The simulator evaluates the performance of switches under different queueing and scheduling strategies across three key labs, providing insights into the effects of various network components and algorithms.


**Labs Breakdown**


**Lab 1: LAN Components**  
In the first part, we simulate basic LAN components:  
* Host-to-Host Communication: Simulate a Layer 2 link between two hosts. Hosts can generate L2 messages, track network statistics, and communicate using a learning switch.  
* Learning Switch: A simple L2 switch that learns MAC addresses and relays messages between hosts based on the MAC table.  
* MAC Table & Flooding: Implementing an efficient MAC table and network flooding to ensure correct message delivery.


**Lab 2: Queueing and Head-of-Line Blocking**  
The second lab introduces queueing mechanisms in switches, focusing on:  
* Input, Output, and Virtual Output Queues: Simulate various queueing models within the switch to study packet delays.  
* Head-of-Line (HoL) Blocking: Analyze the impact of HoL blocking, where a queue’s front message blocks subsequent messages from being processed.  
This lab compares performance in terms of message finishing times and the percentage of time spent in HoL blocking.


**Lab 3: Scheduling**  
The third lab adds scheduling disciplines that govern the order in which messages are transmitted through the switch. Implemented disciplines include:  
* FIFO (First-In-First-Out): Messages are transmitted in the order they are received.  
* Priority Scheduling: Messages are assigned different priorities, and high-priority messages are transmitted first.  
* PGPS (Packetized Generalized Processor Sharing): Messages are scheduled according to their calculated departure times using a fluid model.


**Features**  
* Customizable Network Topology: Easily adjust the number of hosts, switches, and links for network simulation.  
* Queueing Models: Three different queueing mechanisms for managing messages at switch input and output ports.  
* Scheduling Algorithms: Support for FIFO, Priority, and PGPS scheduling to study their effects on network performance.  
* Performance Metrics: Track and analyze statistics such as message finishing times and HoL blocking percentages.

**Authors**  
Ohav Tbul  
Idan Luski
