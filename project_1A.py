
import random
import numpy as np
from enum import Enum
import queue
import networkx as nx
import matplotlib.pyplot as plt
from tabulate import tabulate

#n = lmada * T
FLAG = False #print enabale = True, disable = False
scale_parameter = 0.5 #lamda
cut_time = 1000 
num_of_packets = int(round(2*scale_parameter * cut_time)) # N = {lamda} * Time
#num_of_packets = 4
ENABLE_CUT_TIME = False
FLUID = False #if false we send immediately
TRANS_RATE = 100000
TTL = 0.01
num_of_hosts = 3
SHOW_TABLE_SWITCH = True
FLOODING_FLAG = False #show flooding 

VALID_LINK_FLAG = True #show the next time a linl is avaliable
FLAG_HOST = False #shoe host massegw
SHOW_TOPOLOGY = False 

class EventType(str, Enum):
    CREATE = "create a message"
    SEND   = "send a message"
    


headers = ['MAC', 'Port', 'TTL']


def print_large_text():
    large_text = """
  ____  _             _                                    
 / ___|| |_ __ _ _ __| |_
 \___ \| __/ _` | '__| __| 
  ___) | || (_| | |  | |_ 
 |____/ \__\__,_|_|   \__|   

"""
    print(large_text)




class Base():
    """all objects inherit from BASE"""
    obj_list = []
    ID_count = 0
    def __init__(self, type_obj) -> None:
        self.ID = Base.ID_count
        Base.ID_count += 1 #next ID
        self.type_obj = type_obj #[Host, Link , MessageL2]
        


class Event():


    def __init__(self, Schedule_time, Event_type, Schedule_obj_ID, target_obj_ID, message_ID=None) -> None:
        self.Schedule_time = Schedule_time
        self.Event_type = Event_type
        self.Schedule_obj_ID = Schedule_obj_ID
        self.target_obj_ID = target_obj_ID
        self.message_ID = message_ID
        self.alive = True
        

    
class Time():
    """class that represent time and wheach object createit"""

    def __init__(self, id):   
         self.time = np.random.exponential(scale=scale_parameter, size=None)
         self.ID= id


def custom_sort_key(time):
    return (time.time, time.ID)

def custom_sort_key2(time,id):
    return (time, id)
    

class Timeline():
    

    def __init__(self) -> None:
        self.order_timeline = []
        self.event_timeline = []
        self.current = 0 #current
        self.index = 0


  
    def merge_lists(self, *args:list[Time]): #to marge the times of all hosts 
        merge_list = []
        for time_list in args:
            merge_list.extend(time_list)
        self.order_timeline = sorted(merge_list, key= custom_sort_key)


    
    def insert_into_ordered_list(self, event:Event): #insert new event in the sorted enent list 
     
        index = self.index 
        while index < len(self.event_timeline)-1 and self.event_timeline[index].Schedule_time < event.Schedule_time:
            index += 1
            if index == len(self.event_timeline)-1:
                    self.event_timeline.append(event)
                    return
            
        while self.event_timeline[index].Schedule_time == event.Schedule_time and index < len(self.event_timeline)  :
            if event.Schedule_obj_ID < self.event_timeline[index].Schedule_obj_ID or index == len(self.event_timeline)-1 : 
                if index == len(self.event_timeline)-1:
                    self.event_timeline.append(event)
                    return
                break
            index += 1
            
       
        self.event_timeline.insert(index, event)
    





class L2Message(Base):
    """
    A message is an object that “passes” from one host to another and
    simulates information sent.
    """
    Min = 42
    Max = 1500
    Header = 14 #bytes
    total_instance = 0
    def __init__(self, source_mac_address, dest_mac_address, msg_size) -> None:
        super().__init__(type_obj=self.__class__.__name__)
        self.source_mac_address = source_mac_address
        self.dest_mac_address = dest_mac_address
        self.msg_size = msg_size + L2Message.Header
        self.Message_type = "data"
        self.alive =True
        self.total=0 # total time : current+propogation+error+delays
        self.send_time=0
        L2Message.total_instance += 1
        Base.obj_list.append(self)
    

        
    



class Host(Base):
    """
    A host is an object that both creates and destroys L2 messages.
    """
    Host_list = []
    
    def __init__(self, host_mac_address) -> None:
        super().__init__(type_obj=self.__class__.__name__)
        self.host_mac_address = host_mac_address
        self.nic = -1
        self.total_byte_sent = 0
        self.total_byte_recieved = 0
        self.time = []
        self.queue = queue.Queue()
        Base.obj_list.append(self)
        Host.Host_list.append(self)
        G.add_node(self.ID, name=f"Host: {self.host_mac_address}") 
        

    def get_dest_uniformely(self): #randomlt choose target host
        dest = Host.Host_list[random.randint(0, len(Host.Host_list)-1)]
        while(self.ID == dest.ID):
            dest = Host.Host_list[random.randint(0, len(Host.Host_list)-1)]
        return dest
    

    def remove_object_by_id(object_list: list[Base], unique_id):
        for obj in object_list:
            if obj.ID == unique_id:
                object_list.remove(obj)
                break

    def create_L2Message(self, time, timeline:Timeline):
        schedual = 0 # 0 --> sent massege immediatly , if not 0 send in time = current + schedual
        dest = self.get_dest_uniformely()
        payload_size = random.randint(L2Message.Min, L2Message.Max+1)
        msg = L2Message(self.host_mac_address, dest.host_mac_address ,payload_size)
        self.total_byte_sent += payload_size
        link = Base.obj_list[self.nic]
        if FLAG_HOST: 
            print(f"t= {schedual + time} : Host {self.host_mac_address} created an L2 Message (size: {payload_size + L2Message.Header}) send to {dest.host_mac_address} ")
 
        if FLUID:
            schedual = np.random.exponential(scale=scale_parameter, size=None) 
  
        dest_event = link.first_end_point  #find dest for event from link
        if self.ID == link.first_end_point:
            dest_event = link.second_end_point

        transmission_time = (msg.msg_size * 8)/ link.transmission_rate #seconds
        t_prop = link.prop_delay
        msg.total = t_prop +transmission_time + link.error
        if time+ schedual>=link.valid_time[self.ID]:#the link is valid
           msg.send_time = time+ schedual
           msg.total+=time+ schedual
           Base.obj_list[self.nic].valid_time[self.ID]= msg.total #update the next time the link is valid
           timeline.insert_into_ordered_list(Event(schedual+time, EventType.SEND, self.nic, dest_event, msg.ID)) #the source is the link and the dest is the next hop, different from source and dest in L2massege
           print(f"link empty the valid time is: {Base.obj_list[self.nic].valid_time[self.ID]}") if FLAG else None
        else:
           msg.send_time = link.valid_time[self.ID] #when we will send the massege - the next time the link is valid
           print(f"will be send in t= {Base.obj_list[self.nic].valid_time[self.ID]}") if FLAG else None
           msg.total += link.valid_time[self.ID]
           Base.obj_list[self.nic].valid_time[self.ID]= msg.total #update the next time the link is valid
           timeline.insert_into_ordered_list(Event(link.valid_time[self.ID], EventType.SEND, self.nic, dest_event, msg.ID))
           print(f"recieved in t= {Base.obj_list[self.nic].valid_time[self.ID]}") if FLAG else None



    def recieve_L2Message(self, msg: L2Message,link=None ):
        if msg.dest_mac_address != self.host_mac_address: #not all masseges are directed to this host - flooding
            print(f"the rcieved is {self.host_mac_address} but arrived {msg.dest_mac_address}")
            #msg.alive = False
            return
        print(f"host mac: {self.host_mac_address} recieved massage ") if FLAG_HOST else None
        self.total_byte_recieved += msg.msg_size #TODO check fi its include payload or not
        link = Base.obj_list[self.nic]
    

        if FLAG_HOST:
            print("#------------------------------------------------#")
            print(f"message with ID {msg.ID}:\n source: {msg.source_mac_address}\n destination: {msg.dest_mac_address}\n send time:{msg.send_time}\n arrive time:{msg.total}\ntotal byte recieve {self.total_byte_recieved}")
            print(f"Host {self.host_mac_address} destroyed an L2 Message (size: {msg.msg_size})\ntime:{msg.total}")
            print("#------------------------------------------------#")
            
        msg.alive = False
        
        

    def acumulate(self):
        acc =0
        acumulative = []
        for t in self.time:
            acc += t.time
            t.time = acc
            acumulative.append(t)
        self.time = acumulative    


    def statistics(self):  
        if FLAG:
            print(f"statistics of host {self.host_mac_address} :\nTotal byte sent: {self.total_byte_sent}\nTotal byte recieved: {self.total_byte_recieved}")  



class Link(Base):
    """
    A link has 2 end-points and is characterized by rate. The links are FullDuplex
    """
    msg_list = []
    def __init__(self, first_end_point, second_end_point, prop_delay=0,error=0, port1=None, port2=None) -> None:
        super().__init__(type_obj=self.__class__.__name__)
        self.first_end_point = first_end_point
        self.second_end_point = second_end_point
        self.transmission_rate = TRANS_RATE
        self.prop_delay = prop_delay
        self.error = error
        self.valid_time={first_end_point:0,second_end_point:0} #the next time in timeline the link will be empty for me to send, if i want to send i check the time for my id                                          
        Base.obj_list.append(self)
        G.add_edge(self.first_end_point,self.second_end_point, lable=f"Link {self.ID}")

    def get_id_from_mac(mac_adress):
        for obj in Base.obj_list:
            if obj.type_obj == "Host" and obj.host_mac_address == mac_adress:
                return obj.ID

class Entry():
    """
    entry for mac table contain:
      |  mac adrress   |  port number  | number of entry time |
      
    """
    def __init__(self, mac_adress, port_number, ttl) -> None:
        self.used = True
        self.mac_adress = mac_adress
        self.port_number = port_number
        self.ttl = ttl
        
    def get_mac_adress(self):
        return self.mac_adress    


class Switch(Base):
    """
    The Switch object learns MAC addresses and associates them with its
    ports, floods the network when needed, and, most importantly, relays
    messages from one host to another.
    """
    
    def __init__(self, ports_size, mac_table_size, mac_num) -> None:
        super().__init__(type_obj=self.__class__.__name__)
        self.ports = [None for i in range(ports_size)] #inside port we have link id that we know
        self.mac_table_size = mac_table_size
        self.used_ports = []
        self.mac_table = []
        self.mac_num = mac_num
        Base.obj_list.append(self)
        G.add_node(self.ID, name=f"switch {self.ID}")

    def change_port(self, port_num, link_id):
        self.ports[port_num] = link_id

    def is_full(self):
        """check if can the mac table is full or not"""
        if len(self.mac_table) >= self.mac_table_size :
            return True
        else:
            False

    def is_in_mac_table(self, mac_adress):
        """if in mac table return port number"""

        for i in range(len(self.mac_table)):
            if self.mac_table[i].get_mac_adress() == mac_adress:
                return True
        return False
            
    def add_entry(self, mac_address, port):
        "if the table is not full --> append"
        "if full --> find the first entrie that isnt valid and change"
        "if all entries are valid ----> change the entrie with the minimum last time used"
        new_entry = Entry(mac_address, port, timeline.current)
        if self.is_full():
            min = self.mac_table[0].ttl
            min_index = 0
            for (index ,entry) in enumerate(self.mac_table):
                if abs(timeline.current - entry.ttl)>= TTL:
                     print(f"ttl exceed swap {self.mac_table[index]} ")
                     self.mac_table[index] = new_entry
                     return
                if entry.ttl < min:
                    min  = entry.ttl
                    min_index = index
            self.mac_table[min_index] = new_entry
        else:
            self.mac_table.append(new_entry)        

    def get_entry_index(self,mac_adress):
        """if inside mac adress return index if not None"""
        for (index,entry) in enumerate(self.mac_table):
            if entry.mac_adress == mac_adress:
                return index
        return None 
   
    def get_port_from_link(self,link_id):
        return self.ports.index(link_id)
    
    def update_mac_table(self,  mac_address, link_id):
        if not(self.is_in_mac_table(mac_address)):#if not in mac table
            port = self.get_port_from_link(link_id)
            self.add_entry(mac_address, port)
        else:
            index = self.get_entry_index(mac_address)
            print("2updating  TTL...") if SHOW_TABLE_SWITCH else None
            self.mac_table[index].ttl = timeline.current 
        self.print_table() if SHOW_TABLE_SWITCH else None
        
    def print_table(self):
        data = []
        for entry in self.mac_table:
            data.append([entry.mac_adress,entry.port_number, entry.ttl])

        print(tabulate(data, headers, tablefmt='grid'))    





    def recieve_L2Message(self, msg: L2Message, link_id):
        #msg.alive = False
        #these link id is the link we reach the swich from
        time = timeline.current #TODO check if remove
        # learn the source port. if not exist update the mac table
        #check if the  destination exist . if not make flooding even if yes use SEND evend and send the message and uppdate.
        self.update_mac_table(msg.source_mac_address, link_id) #update the source in the table
        
    
        

        
        if self.is_in_mac_table(msg.dest_mac_address):
            
            dest_index = self.get_entry_index(msg.dest_mac_address)
            if abs(timeline.current - self.mac_table[dest_index].ttl) < TTL:# if  exist
                print("NO flooding") if FLOODING_FLAG else None
                self.mac_table[dest_index].ttl = timeline.current #update the lase time used to dest entrie
                print("1updating  TTL...") if SHOW_TABLE_SWITCH else None
                dest_port = self.mac_table[dest_index].port_number
                target_link_id = self.ports[dest_port]
                dest = Base.obj_list[target_link_id].first_end_point
                if self.ID == Base.obj_list[target_link_id].first_end_point:
                    dest = Base.obj_list[target_link_id].second_end_point
            
                     
                #we have the mac in the table
                
                
                link_obj = Base.obj_list[target_link_id]
                transmission_time = (msg.msg_size * 8)/ link_obj.transmission_rate #seconds
                t_prop = link_obj.prop_delay
                msg.total = t_prop +transmission_time + link_obj.error
                if time >=link_obj.valid_time[self.ID]: #link is empty 
                   msg.send_time = time
                   msg.total+=time
                   Base.obj_list[target_link_id].valid_time[self.ID]= msg.total
                   timeline.insert_into_ordered_list(Event(time, EventType.SEND, target_link_id, dest, msg.ID)) #same idia like sent in host
                   #print (f"1 sending from {msg.source_mac_address} ----> {msg.dest_mac_address}, the current time is: {timeline.current} and the event time  send is: {time} msg id {msg.ID}")
                   print(f"link empty the valid time is: {link_obj.valid_time[self.ID]}") if VALID_LINK_FLAG else None
                   
                else:
                   msg.send_time = link_obj.valid_time[self.ID]
                   print(f"will be send in t= {link_obj.valid_time[self.ID]}") if FLAG else None
                   msg.total += link_obj.valid_time[self.ID]
                   link_obj.valid_time[self.ID]= msg.total
                   timeline.insert_into_ordered_list(Event(link_obj.valid_time[self.ID], EventType.SEND, target_link_id, dest, msg.ID))
                   #print (f"2 sending from {msg.source_mac_address} ----> {msg.dest_mac_address}, the current time is: {timeline.current} and the event time  send is: {link_obj.valid_time[self.ID]} msg id {msg.ID}")
                   print(f"recieved in t= {link_obj.valid_time[self.ID]}") if FLAG else None
                   #send message to ths nic in dedicated port
                   
                return
            else:
                self.mac_table.pop(dest_index) #the entrie is not valid, delete it
        #flooding - create new massege and send it to all ports (without the reciving port)
        print("performing flooding") if FLOODING_FLAG else None
        #print (f"sending from {msg.source_mac_address} ----> {msg.dest_mac_address}")
        for nic_id in self.ports:
            if nic_id != None and nic_id != link_id:
                link_obj = Base.obj_list[nic_id]
                dest = link_obj.first_end_point   #find dest for event
                if self.ID == link_obj.first_end_point:
                        dest = link_obj.second_end_point
                #dest is the id of the other side of the link (not necesseraly the  host)
                #L2 message will alway be source mac to dest mac of two hosts in LAN
                
                #dest_mac_adress = Base.obj_list[dest].mac_adress
                flood_msg = L2Message(msg.source_mac_address, msg.dest_mac_address, msg.msg_size )
                

                transmission_time = (flood_msg.msg_size * 8)/ link_obj.transmission_rate #seconds
                t_prop = link_obj.prop_delay
                flood_msg.total = t_prop +transmission_time + link_obj.error
                if time >=link_obj.valid_time[self.ID]: # the link empty , we can send
                    flood_msg.send_time = time
                    flood_msg.total+=time
                    link_obj.valid_time[self.ID]= flood_msg.total
                    timeline.insert_into_ordered_list(Event(time, EventType.SEND, nic_id, dest, flood_msg.ID)) #same idia like sent in host
                    #print (f"3 sending from {msg.source_mac_address} ----> {msg.dest_mac_address} thgho link {nic_id}, the current time is: {timeline.current} and the event time  send is: {time} msg id {flood_msg.ID}")

                    print(f"link empty the valid time is: {link_obj.valid_time[self.ID]}") if VALID_LINK_FLAG else None
                else:
                    flood_msg.send_time = link_obj.valid_time[self.ID]
                    print(f"will be send in t= {link_obj.valid_time[self.ID]}") if FLAG else None
                    flood_msg.total += link_obj.valid_time[self.ID]
                    link_obj.valid_time[self.ID]= flood_msg.total
                    timeline.insert_into_ordered_list(Event(link_obj.valid_time[self.ID], EventType.SEND, nic_id, dest, flood_msg.ID))
                    #print (f"4 sending from {msg.source_mac_address} ----> {msg.dest_mac_address} thgho link {nic_id}, the current time is: {timeline.current} and the event time  send is: {link_obj.valid_time[self.ID]} msg id {flood_msg.ID}")

            #self.print_table()

                        
                    
                    

                    



def generate_mac_address(): #return mac
    # Generate six pairs of hexadecimal digits
    mac = [random.randint(0x00, 0xFF) for _ in range(6)]
    # Format as a MAC address
    mac_address = ':'.join(f'{byte:02X}' for byte in mac)
    return mac_address
             






timeline = Timeline()
G = nx.Graph()


def show_topology():
    node_lables = nx.get_node_attributes(G, 'name')
    edge_lables = nx.get_edge_attributes(G, 'lable')
    pos = nx.spring_layout(G)
    nx.draw(G,pos, with_labels=True, labels=node_lables, node_color='lightblue', font_size=6)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_lables, font_color='red')
    plt.title('Netwok topology')
    plt.show() if SHOW_TOPOLOGY else None
    #plt.close()

def main():
    
    print_large_text()

    
#2 switch LAN
    #making hosts group    
    num_host_1 = random.randint(2,5)
    group_host1 = [Host(generate_mac_address())for i in range(num_host_1)]
    num_host_2 = random.randint(2,5)
    group_host2 = [Host(generate_mac_address())for i in range(num_host_2)]
    

    #making 2 switch
    switch1= Switch(10,3,generate_mac_address())
    switch2= Switch(10,3,generate_mac_address())
    
    
    #connecte links
    times=[]
    switch_Link= Link(switch1.ID,switch2.ID)
    switch1.ports[0]= switch_Link.ID
    switch2.ports[0]= switch_Link.ID
    for (index,host) in enumerate(group_host1):
        for i in range(num_of_packets):
            host.time.append( Time(host.ID))
        host.acumulate()
        times.append(host.time)    
        link = Link(host.ID,switch1.ID)
        host.nic = link.ID
        switch1.ports[index+1] = link.ID

    for (index,host) in enumerate(group_host2):
        for i in range(num_of_packets):
            host.time.append( Time(host.ID))
        times.append(host.time)
        host.acumulate()    
        link = Link(host.ID,switch2.ID)
        host.nic = link.ID
        switch2.ports[index+1] = link.ID    
    
    timeline.merge_lists(*times) #linst of order events


#Hosts for test switch A    
    # host1 = Host("AA:AA:AA:AA")
    # host2= Host("BB:BB:BB:BB")
    # host3= Host("CC:CC:CC:CC")


# idan work ---------------
    # 3 Host switch scenario
    # switch1= Switch(10,2, "DD:DD:DD:DD")
    # link1= Link(host1.ID, switch1.ID)
    # switch1.ports[0] = link1.ID
    # link2 = Link(switch1.ID,host2.ID)
    # switch1.ports[1] = link2.ID
    # link3 = Link(switch1.ID,host3.ID)
    # switch1.ports[2] = link3.ID
    # host1.nic = link1.ID
    # host2.nic = link2.ID
    # host3.nic = link3.ID
# ----------------------------
    #HOST to HOST scenario
    # link = Link(host1.ID,host2.ID)
    # host1.nic = link.ID
    # host2.nic = link.ID

    show_topology()

    # for i in range(num_of_packets):
    #     host1.time.append( Time(host1.ID)) #t=
    #     host2.time.append( Time(host2.ID))#[0, 0.2, 0.4 , 0.5]
    #     host3.time.append( Time(host3.ID))

    # host1.acumulate()
    # host2.acumulate()
    # host3.acumulate() 
         
    # timeline.merge_lists(host1.time, host2.time, host3.time) #linst of order events
    counter = 0
    for t in timeline.order_timeline:
        timeline.event_timeline.append(Event(t.time, EventType.CREATE, Base.obj_list[t.ID].ID, Base.obj_list[t.ID].nic))

    for (index,event) in  enumerate(timeline.event_timeline):
        timeline.current = event.Schedule_time #TODO check
        if (timeline.current >= cut_time) and ENABLE_CUT_TIME:
            print("end simulation")
            break
        
        timeline.index = index
        if event.Event_type == EventType.CREATE  :
            event.alive = False
            Base.obj_list[event.Schedule_obj_ID].create_L2Message(event.Schedule_time, timeline)
            
        elif event.Event_type == EventType.SEND :#deleted event.alive
            msg = Base.obj_list[event.message_ID]
            if msg.alive :
                event.alive = False
                Base.obj_list[event.target_obj_ID].recieve_L2Message(msg, event.Schedule_obj_ID) 
                counter += 1

        # elif event.Event_type == EventType.FLOODING and event.alive:
        #     msg = Base.obj_list[event.message_ID]
        #     if msg.alive:
        #         event.alive = False
        #         Base.obj_list[event.target_obj_ID].recieve_L2Message(msg) 
        #         counter += 1        
        
        #timeline.current = event.Schedule_time
        
    for host in Host.Host_list:
        #avg_recive = host.total_byte_recieved/(counter/NUM_OF_HOST)
        avg_recive = host.total_byte_recieved/(num_of_packets)
        print(f"host {host.ID} mac {host.host_mac_address} average is : {avg_recive}")

    #run on time line if it schedual






if __name__ == "__main__":
    main()