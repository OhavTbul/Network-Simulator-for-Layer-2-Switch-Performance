
import random
import numpy as np
from enum import Enum
import queue
import networkx as nx
import matplotlib.pyplot as plt
from tabulate import tabulate
from colorama import Fore, Style, init
from collections import deque
import copy
class EventType(str, Enum):
    CREATE = "create a message"
    SEND   = "send a message"
    RECIEVE = "recieve a message"
    OpenLink = "the link is empty"
    
class alorithm(str, Enum):
    FIFO = "FIFO"
    Priority = "Priority"
    PGPS = "PGPS"
    
 
class Qeueu_type(str, Enum):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    VIRTUAL = "VIRTUAL" 

class BackGround(str, Enum):
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_RESET = '\033[49m'
     
np.random.seed(1801)
#n = lmada * T
FLAG = False #print enabale = True, disable = False
scale_parameter = 0.2 #lamda
cut_time = 2000
num_of_packets = int(round(2*scale_parameter * cut_time)) # N = {lamda} * Time
num_of_packets = 100
ENABLE_CUT_TIME = False
FLUID = False #if false we send immediately
TRANS_RATE = 100000
BufferQueue = 1000
TTL = 10000000
SHOW_TABLE_SWITCH = False
FLOODING_FLAG = False #show flooding 
FLAG_HOST_SEND = False
FLAG_HOST_RECIEVED = False
FLAG_HOST_CREATE = False
FLAG_QUEUE_PRINT = False
FLAG_HOST = False #shoe host massegwcccccbkvhvkhefulnchhfkbbgggtjbjhjgbvlhirdkbe
PRIORITY_NUM = 3

VALID_LINK_FLAG = False #show the next time a linl is avaliable

SHOW_TOPOLOGY = False 
TYPE_QUEUE = Qeueu_type.OUTPUT
TYPE_algorithm = alorithm.Priority
SHOW_BAR_QUEUE = False
max_size_queue =0
RECIEVE_TRANS = 500#link transmitiion of recieve link



init(autoreset=True)
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"
YELLOW = "\033[33m"
PINK = "\033[35m"
BLUE = "\033[34m"
ORANGE = '\033[38;5;214m'
CYAN = '\033[36m'



type_to_shape = {
    'host': 'o',
    'switch': 's',
    'diamond': 'd'
}

  

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
    queue_list = []
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
        self.last_create =False
        
        

    
class Time():
    """class that represent time and wheach object createit"""

    def __init__(self, id):   
        self.time = np.random.exponential(scale=scale_parameter, size=None)
        #  if id == 1:
        #      self.time = 1.001
        #  else:
        #self.time = 1    
             
         
        self.ID= id


def custom_sort_key(time):
    return (time.time, time.ID)


#plain data 

    

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


    
    def insert_into_ordered_list(self, event:Event,two =False): #insert new event in the sorted enent list 
        
        index = self.index 

        while index < len(self.event_timeline)-1 and self.event_timeline[index].Schedule_time < event.Schedule_time:
            index += 1
            if index == len(self.event_timeline)-1:
                    self.event_timeline.append(event)
                    return
            
        while self.event_timeline[index].Schedule_time == event.Schedule_time and index < len(self.event_timeline)  :
            if index == len(self.event_timeline)-1:
                    self.event_timeline.append(event)
                    return
            if (event.Schedule_obj_ID < self.event_timeline[index].Schedule_obj_ID or index == len(self.event_timeline)-1) and event.Event_type == EventType.CREATE  : 
                if index == len(self.event_timeline)-1:
                    self.event_timeline.append(event)
                    return
                break
            
            index += 1
            
        if index == len(self.event_timeline)-1:
             self.event_timeline.append(event)
             return
        
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
        self.total=0 # total time : current+propogation+error+delays arriving time
        self.send_time=0
        L2Message.total_instance += 1
        self.real_msg_id = None #save the real ID in case of duplications
        Base.obj_list.append(self)
        self.enter_queue = 0
        self.enter_HOL = 0
        self.departure = 0
        self.priority = 0
        self.real_size = msg_size + L2Message.Header


        #Use only for statisitc!
        self.Hol_link = None
    

        
    



class Host(Base):
    """
    A host is an object that both creates and destroys L2 messages.
    """
    Host_list = []
    priority = 0
    def __init__(self, host_mac_address) -> None:
        super().__init__(type_obj=self.__class__.__name__)
        self.host_mac_address = host_mac_address
        self.nic = -1
        self.total_byte_sent = 0
        self.total_byte_recieved = 0
        self.time = []
        self.queue = queue.Queue()
        self.dest_group = []
        self.priority = Host.priority
        Host.priority += 1
        Base.obj_list.append(self)
        Host.Host_list.append(self)
        G.add_node(self.ID, name=f"Host: {self.host_mac_address}", type="host") 
        


    def make_random_set_dest(self):
        """
        generate subset in random size 2 and return a list of MAC address
        """
        host_copy = [i for i in Host.Host_list]
        host_copy.remove(self)
        subset_size  = 2
        random_subset = random.sample(host_copy, subset_size)
        random_subset = [i.ID for i in random_subset]
        self.dest_group = random_subset
    

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

    def create_L2Message(self, time, timeline:Timeline, index):
        schedual = 0 # 0 --> sent massege immediatly , if not 0 send in time = current + schedual
        if self.ID == 2:
            num = random.choice(self.dest_group)
            dest = Base.obj_list[num]
        else:
           dest = Base.obj_list[0]
        #payload_size = random.randint(L2Message.Min, L2Message.Max+1) #george aloowed us
        payload_size = 986
        msg = L2Message(self.host_mac_address, dest.host_mac_address ,payload_size)
        msg.real_msg_id = msg.ID
        msg.Hol_link = metadata_connections[msg.dest_mac_address]
        msg.priority = self.priority
        self.total_byte_sent += payload_size
        link = Base.obj_list[self.nic]
        if FLAG_HOST_CREATE: 
            print(f"t= {schedual + time} : Host {self.host_mac_address} created an L2 Message (size: {payload_size + L2Message.Header}) send to {dest.host_mac_address} ")
 
        if FLUID:
            schedual = np.random.exponential(scale=scale_parameter, size=None) 
  
        

        transmission_time = (msg.msg_size * 8)/ link.transmission_rate #seconds
        t_prop = link.prop_delay
        msg.total = t_prop +transmission_time + link.error
        if time+ schedual>=link.valid_time[self.ID]:#the link is valid
           msg.send_time = time+ schedual
           msg.total+=time+ schedual
           if cut_time_func(msg.total):
               Base.obj_list[self.nic].valid_time[self.ID]= msg.total #update the next time the link is valid
               timeline.insert_into_ordered_list(Event(max(timeline.current,schedual+time), EventType.SEND, self.nic , self.ID, msg.ID)) #the source is the link and the dest is the next hop, different from source and dest in L2massege
               print(f"link empty the valid time is: {Base.obj_list[self.nic].valid_time[self.ID]}") if FLAG else None
        else:
           msg.send_time = max(timeline.current,link.valid_time[self.ID]) #when we will send the massege - the next time the link is valid
           print(f"will be send in t= {Base.obj_list[self.nic].valid_time[self.ID]}") if FLAG else None
           msg.total += msg.send_time
           if cut_time_func(msg.total):
               Base.obj_list[self.nic].valid_time[self.ID]= msg.total #update the next time the link is valid
               timeline.insert_into_ordered_list(Event(msg.send_time, EventType.SEND, self.nic, self.ID, msg.ID))
               print(f"recieved in t= {Base.obj_list[self.nic].valid_time[self.ID]}") if FLAG else None

    def send_L2Message(self, msg: L2Message,link=None , index=0):

        dest_event = Base.obj_list[self.nic].first_end_point  #find dest for event from link
        if self.ID == Base.obj_list[self.nic].first_end_point:
            dest_event = Base.obj_list[self.nic].second_end_point
        if FLAG_HOST_SEND:
                   print(f"{PINK}#------------------------------------------------#")
                   print(f"{PINK}message with ID {msg.ID}:\n source: {msg.source_mac_address}\n destination: {msg.dest_mac_address}\n send time:{msg.send_time}\n")
                   print(f"{PINK}L2 Message (size: {msg.msg_size})")
                   print(f"{PINK}#------------------------------------------------#")
        
        
        timeline.insert_into_ordered_list(Event(msg.total, EventType.RECIEVE, self.nic,dest_event , msg.ID))
        
    

    def recieve_L2Message(self, msg: L2Message,link=None , index=0):
        link_obj = Base.obj_list[link]
        dest = link_obj.first_end_point   #only for output
        if self.ID == link_obj.first_end_point:
            dest = link_obj.second_end_point

        Base.obj_list[link].busy[dest] = False #only for output
        if msg.dest_mac_address != self.host_mac_address: #not all masseges are directed to this host - flooding
            print(f"{RED}msg ID {msg.real_msg_id} : the Host rcieve massage is {self.host_mac_address} but arrived from {msg.dest_mac_address}") if FLOODING_FLAG else None
            msg.alive = False #TODO try
            
            return
        print(f"{GREEN}host mac: {self.host_mac_address} recieved massage ID {msg.real_msg_id} ") if FLAG_HOST else None
        self.total_byte_recieved += msg.real_size #TODO check fi its include payload or not
        link = Base.obj_list[self.nic]
    

        if FLAG_HOST_RECIEVED:
            print(f"{BLUE}#------------------------------------------------#")
            print(f"{BLUE}message with ID {msg.real_msg_id}:\n arrive time:{msg.total}\ntotal byte recieve {self.total_byte_recieved}")
            print(f"{BLUE}Host {self.host_mac_address} destroyed an L2 Message (size: {msg.msg_size})")
            print(f"{BLUE}switch arrive  {msg.enter_queue} ")
            print(f"{BLUE}switch departure: {msg.departure}")
            print(f"{BLUE}#------------------------------------------------#")
            
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
        self.link_open =[0]
        self.link_close = []
        self.busy={first_end_point:False,second_end_point:False}   #only for output for now                                   
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






def update_current(packet_list_sorted, current, current_packets, waiting_queue):#flow [1,2,3] priority [1,2,4]
    for index,packet in enumerate(packet_list_sorted):
        if index == 0:
            continue
        if current == packet.enter_queue:
            if  current_packets[packet.priority - 1] != None:
                waiting_queue[packet.priority].append(packet)
                packet_list_sorted.remove(packet)
            else:
                current_packets[packet.priority - 1] = packet
                packet_list_sorted.remove(packet)
        else:

            break


def relative_BW_Calc(relative_BW, current_packets):

    sum = 0
    for packet in current_packets:
        if packet != None:
            sum += packet.priority

    for flow,packet in enumerate(current_packets):
        if packet != None:
            relative_BW[flow] = (current_packets[flow].priority/sum)

def calc_min_finish(relative_BW,current_packets):
    min = 100000000
    for packet in current_packets:
        if packet != None:
            end_time = packet.msg_size/(relative_BW[packet.priority-1]*RECIEVE_TRANS)
            if end_time < min:
                min = end_time

    return min











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
        self.host_mac_address = mac_num
        Base.obj_list.append(self)
        G.add_node(self.ID, name=f"switch {self.ID}", type="switch")

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
            self.mac_table[index].ttl = timeline.current 
        self.print_table() if SHOW_TABLE_SWITCH else None
        
    def print_table(self):
        data = []
        for entry in self.mac_table:
            data.append([entry.mac_adress,entry.port_number, entry.ttl])
        title = f"switch {self.ID}"   
        print(title)
        print("=" * len(title))
        print(tabulate(data, headers, tablefmt='grid'))    




    def send_L2Message(self, msg: L2Message,link=None, index =0 ):
        #not happening 
        timeline.insert_into_ordered_list(Event(timeline.current, EventType.RECIEVE, link,self.id, msg.ID))
        
        
        

    def recieve_L2Message(self, msg: L2Message, link_id, index):
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
                   if cut_time_func(msg.total):
                       Base.obj_list[target_link_id].valid_time[self.ID]= msg.total
                       
                       timeline.insert_into_ordered_list(Event(msg.total, EventType.RECIEVE, target_link_id, dest, msg.ID)) #same idia like sent in host
                   #print (f"1 sending from {msg.source_mac_address} ----> {msg.dest_mac_address}, the current time is: {timeline.current} and the event time  send is: {time} msg id {msg.ID}")
                   print(f"link empty the valid time is: {link_obj.valid_time[self.ID]}") if VALID_LINK_FLAG else None
                   
                else:
                   msg.send_time = link_obj.valid_time[self.ID]
                   print(f"will be send in t= {link_obj.valid_time[self.ID]}") if FLAG else None
                   msg.total += link_obj.valid_time[self.ID]
                   if cut_time_func(msg.total):
                       link_obj.valid_time[self.ID]= msg.total
                       
                       timeline.insert_into_ordered_list(Event(link_obj.valid_time[self.ID], EventType.RECIEVE, target_link_id, dest, msg.ID))
                       
                   #print (f"2 sending from {msg.source_mac_address} ----> {msg.dest_mac_address}, the current time is: {timeline.current} and the event time  send is: {link_obj.valid_time[self.ID]} msg id {msg.ID}")
                   print(f"recieved in t= {link_obj.valid_time[self.ID]}") if FLAG else None
                   #send message to ths nic in dedicated port
                   
                return
            else:
                self.mac_table.pop(dest_index) #the entrie is not valid, delete it
        #flooding - create new massege and send it to all ports (without the reciving port)
        print("performing flooding") if FLOODING_FLAG else None
        msg.alive = False #TODO try
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
                flood_msg.real_msg_id = msg.real_msg_id

                transmission_time = (flood_msg.msg_size * 8)/ link_obj.transmission_rate #seconds
                t_prop = link_obj.prop_delay
                flood_msg.total = t_prop +transmission_time + link_obj.error
                if time >=link_obj.valid_time[self.ID]: # the link empty , we can send
                    flood_msg.send_time = time
                    flood_msg.total+=time
                    if cut_time_func(flood_msg.total):
                        link_obj.valid_time[self.ID]= flood_msg.total
                        
                        timeline.insert_into_ordered_list(Event(flood_msg.total, EventType.RECIEVE, nic_id, dest, flood_msg.ID)) #same idia like sent in host
                        
                    #print (f"3 sending from {msg.source_mac_address} ----> {msg.dest_mac_address} thgho link {nic_id}, the current time is: {timeline.current} and the event time  send is: {time} msg id {flood_msg.ID}")

                    print(f"link empty the valid time is: {link_obj.valid_time[self.ID]}") if VALID_LINK_FLAG else None
                else:
                    flood_msg.send_time = link_obj.valid_time[self.ID]
                    print(f"will be send in t= {link_obj.valid_time[self.ID]}") if FLAG else None
                    flood_msg.total += link_obj.valid_time[self.ID]
                    if cut_time_func(flood_msg.total):
                        link_obj.valid_time[self.ID]= flood_msg.total
                        
                        timeline.insert_into_ordered_list(Event(link_obj.valid_time[self.ID], EventType.RECIEVE, nic_id, dest, flood_msg.ID))
                        
                    #print (f"4 sending from {msg.source_mac_address} ----> {msg.dest_mac_address} thgho link {nic_id}, the current time is: {timeline.current} and the event time  send is: {link_obj.valid_time[self.ID]} msg id {flood_msg.ID}")

            #self.print_table()

                        
class SwitchQueue(Base):
    """
    object queue will be located on switch 
    """

    def __init__(self,src_port=None,dest_port=None) -> None:
        super().__init__(type_obj=self.__class__.__name__)
        self.queue = deque()
        self.src_port = src_port
        self.dest_port = dest_port
        self.last_departure = 0
        self.HOL_enter = 0
        Base.queue_list.append(self.ID)
        Base.obj_list.append(self)
        self.total_Hol = 0
        self.max_queue = 0
    
    def put(self,msg:L2Message):
        self.queue.append(msg)
        if self.max_queue < len(self.queue):
            self.max_queue = len(self.queue)

    def get(self):
        return self.queue.popleft()

    def empty(self):
        if len(self.queue)==0:
            return True
        else:
            return False


class Switch2(Switch):
    """
    a class that work with queues for project 2
    """
    def __init__(self,ports_size, mac_table_size, mac_num, num_of_connected, Q_type =Qeueu_type.INPUT.value,SchedualAlg=alorithm.FIFO.value,is_fluid=False  ) -> None:
        super().__init__(ports_size, mac_table_size, mac_num)
        self.Q_type = Q_type
        self.SchedualAlg = SchedualAlg
        self.is_fluid = is_fluid
        self.switch_queue ={}  
        self.num_of_connected = num_of_connected
        self.TotalHolTime = []
        self.priority_queues ={}
        self.packet_list = {1:None,2:None,3:None} #list for calculate GPS
        self.FIRST_IN_SWITCH = True
        self.first_in_switch_val = 0
        self.last_in_switch_val = 0
        self.lst_times = []
        self.finish_times_by_priority = {1:0,2:0,3:0}

        if self.Q_type == Qeueu_type.INPUT.value:
            for i in range(self.num_of_connected):
                self.switch_queue[(i,None)] = SwitchQueue(src_port=i)
                self.TotalHolTime.append(0)
 
        elif self.Q_type == Qeueu_type.OUTPUT.value:
            if self.SchedualAlg == alorithm.FIFO.value:
                for i in range(self.num_of_connected):
                    self.switch_queue[(None,i)] = SwitchQueue(dest_port=i)
                    self.TotalHolTime.append(0)
                    
            if (self.SchedualAlg == alorithm.Priority.value):
                for i in range(self.num_of_connected):
                    for pr in range(PRIORITY_NUM):
                            self.priority_queues[(None,i,pr + 1)] = SwitchQueue(dest_port=i)

            if  (self.SchedualAlg == alorithm.PGPS.value):
                    for pr in range(PRIORITY_NUM):
                            self.priority_queues[(None,0,pr + 1)] = SwitchQueue(dest_port=0)  #[(None, dest port, priority)]              
            




        elif self.Q_type == Qeueu_type.VIRTUAL.value:
            for i in range(self.num_of_connected):
                for j in range(self.num_of_connected):
                    if i != j:
                        self.switch_queue[(i,j)] = SwitchQueue(src_port=i, dest_port=j)
                        self.TotalHolTime.append(0)


            

    def recieve_L2Message(self, msg: L2Message, link_id, index):
        # if self.SchedualAlg == alorithm.Priority:
        #     priority = random.randint(0,PRIORITY_NUM - 1)
        #     msg.priority = priority    
        time = timeline.current #TODO check if remove
        # learn the source port. if not exist update the mac table
        #check if the  destination exist . if not make flooding even if yes use SEND evend and send the message and uppdate.
        
        self.update_mac_table(msg.source_mac_address, link_id) #update the source in the table
        src_port = self.get_port_from_link(link_id)
        if self.Q_type == Qeueu_type.INPUT:  
            if self.switch_queue[(src_port,None)].empty():
                self.switch_queue[(src_port,None)].HOL_enter = timeline.current
            self.switch_queue[(src_port,None)].put((msg,src_port))
            msg.enter_queue = timeline.current
            print(f"{CYAN}event {index} massage ID {msg.ID} enque to INPUT Queue ({src_port},None) in queue now : {len(self.switch_queue[(src_port,None)].queue)}" ) if FLAG_QUEUE_PRINT else None
            if len(self.switch_queue[(src_port,None)].queue) == 1 :
                #timeline.insert_into_ordered_list(Event(timeline.current, EventType.OpenLink, link_id, self.ID, msg.ID))
                next_time = Base.obj_list[link_id].valid_time[self.ID]
                timeline.insert_into_ordered_list(Event(max(timeline.current,next_time), EventType.OpenLink, link_id, self.ID, msg.ID))
                
            return


        
        if self.is_in_mac_table(msg.dest_mac_address):
            
            dest_index = self.get_entry_index(msg.dest_mac_address)
            if abs(timeline.current - self.mac_table[dest_index].ttl) < TTL:# if  exist
                print("NO flooding") if FLOODING_FLAG else None
                self.mac_table[dest_index].ttl = timeline.current #update the lase time used to dest entrie
                dest_port = self.mac_table[dest_index].port_number
                target_link_id = self.ports[dest_port]
                dest = Base.obj_list[target_link_id].first_end_point
                if self.ID == Base.obj_list[target_link_id].first_end_point:
                    dest = Base.obj_list[target_link_id].second_end_point


                next_time = Base.obj_list[target_link_id].valid_time[self.ID]
                msg.enter_queue = timeline.current #update the time message enter the queue
                
                # if self.Q_type == Qeueu_type.INPUT.value:
                #     if self.switch_queue[(src_port,None)].empty():
                #        self.switch_queue[(src_port,None)].HOL_enter = timeline.current
                #     self.switch_queue[(src_port,None)].put((msg,target_link_id))
                #     print(f"{CYAN} massage ID {msg.ID} enque to Queue ({src_port},None)" ) if FLAG_QUEUE_PRINT else None

                if self.Q_type == Qeueu_type.OUTPUT.value:
                    if self.SchedualAlg == alorithm.FIFO.value:
                        if self.switch_queue[(None, dest_port)].empty() and not(Base.obj_list[target_link_id].busy[self.ID]):
                            timeline.insert_into_ordered_list(Event(max(timeline.current,next_time), EventType.OpenLink, target_link_id, self.ID, msg.ID))
                        self.switch_queue[(None, dest_port)].put((msg,target_link_id))
                        msg.enter_queue = timeline.current
                        print(f"{CYAN} massage ID {msg.ID} enque to Queue (None,{dest_port})" ) if FLAG_QUEUE_PRINT else None

                    if self.SchedualAlg == alorithm.Priority.value:
                        if self.priority_queues[(None, dest_port,msg.priority)].empty() and not(Base.obj_list[target_link_id].busy[self.ID]):
                            timeline.insert_into_ordered_list(Event(max(timeline.current,next_time), EventType.OpenLink, target_link_id, self.ID, msg.ID))
                        self.priority_queues[(None, dest_port,msg.priority)].put((msg,target_link_id))
                        msg.enter_queue = timeline.current
                        print(f"{CYAN} massage ID {msg.ID} enque to Queue (None,{dest_port},{msg.priority})" ) if FLAG_QUEUE_PRINT else None 

                    if self.SchedualAlg == alorithm.PGPS.value:
                        if self.priority_queues[(None, dest_port,msg.priority)].empty() and not(Base.obj_list[target_link_id].busy[self.ID]):
                            timeline.insert_into_ordered_list(Event(max(timeline.current,next_time), EventType.OpenLink, target_link_id, self.ID, msg.ID))
                        self.priority_queues[(None, dest_port,msg.priority)].put((msg,target_link_id))
                        msg.enter_queue = timeline.current
                        print(f"{CYAN} massage ID {msg.ID} enque to Queue (None,{dest_port},{msg.priority}) now in queue {len(self.priority_queues[(None, dest_port,msg.priority)].queue)}" ) if FLAG_QUEUE_PRINT else None 
    

                          

                    

                elif self.Q_type == Qeueu_type.VIRTUAL.value:
                    print(self.switch_queue.get((src_port, dest_port)))
                    if self.switch_queue[(src_port, dest_port)].empty() and not(Base.obj_list[target_link_id].busy[self.ID]) :
                        timeline.insert_into_ordered_list(Event(max(timeline.current,next_time), EventType.OpenLink, target_link_id, self.ID, msg.ID))
                    self.switch_queue[(src_port, dest_port)].put((msg,target_link_id))
                    msg.enter_queue = timeline.current
                    print(f"{CYAN} massage ID {msg.ID} enque to Queue ({src_port},{dest_port})" ) if FLAG_QUEUE_PRINT else None
                else:
                    raise Exception("not Q type match")    

                return
            
            else:
                self.mac_table.pop(dest_index) #the entrie is not valid, delete it
        #flooding - create new massege and send it to all ports (without the reciving port)
        # elif self.Q_type != Qeueu_type.INPUT:
        print("performing flooding") if FLOODING_FLAG else None
        msg.alive = False #TODO try
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
                dest_port = self.get_port_from_link(nic_id)
                flood_msg = L2Message(msg.source_mac_address, msg.dest_mac_address, msg.msg_size )
                flood_msg.Hol_link = metadata_connections[flood_msg.dest_mac_address]
                flood_msg.real_msg_id = msg.real_msg_id

                    
                next_time = link_obj.valid_time[self.ID]
                flood_msg.enter_queue = timeline.current #update the time message enter the queue
                    # if self.Q_type == Qeueu_type.INPUT.value:
                    #     if self.switch_queue[(src_port,None)].empty():
                    #         self.switch_queue[(src_port,None)].HOL_enter = timeline.current
                    #     self.switch_queue[(src_port,None)].put((flood_msg,nic_id))
                    #     print(f"{CYAN} massage ID {msg.ID} enque to Queue ({src_port},None)" ) if FLAG_QUEUE_PRINT else None


                if self.Q_type == Qeueu_type.OUTPUT.value:
                    if self.SchedualAlg == alorithm.FIFO:
                        if self.switch_queue[(None, dest_port)].empty() and not(Base.obj_list[nic_id].busy[self.ID]):
                            timeline.insert_into_ordered_list(Event(max(timeline.current,next_time), EventType.OpenLink, link_obj.ID, self.ID, flood_msg.ID))
                            self.switch_queue[(None, dest_port)].put((flood_msg,nic_id))
                            msg.enter_queue = timeline.current
                            print(f"{CYAN} massage ID {msg.ID} enque to Queue (None,{dest_port})" ) if FLAG_QUEUE_PRINT else None
                    if self.SchedualAlg == alorithm.Priority:
                        for pr in range(PRIORITY_NUM ,0, -1):
                            if self.priority_queues[(None, dest_port,pr)].empty() and not(Base.obj_list[nic_id].busy[self.ID]):
                                timeline.insert_into_ordered_list(Event(max(timeline.current,next_time), EventType.OpenLink, link_obj.ID, self.ID, flood_msg.ID))
                                self.priority_queues[(None, dest_port,pr)].put((flood_msg,nic_id))
                                msg.enter_queue = timeline.current
                                print(f"{CYAN} massage ID {msg.ID} enque to Queue (None,{dest_port})" ) if FLAG_QUEUE_PRINT else None
                                break

                   



                elif self.Q_type == Qeueu_type.VIRTUAL.value:
                    if self.switch_queue[(src_port, dest_port)].empty() and not(Base.obj_list[nic_id].busy[self.ID]):
                        timeline.insert_into_ordered_list(Event(max(timeline.current,next_time), EventType.OpenLink, link_obj.ID, self.ID, flood_msg.ID))

                    self.switch_queue[(src_port, dest_port)].put((flood_msg,nic_id))
                    msg.enter_queue = timeline.current
                    print(f"{CYAN} massage ID {msg.ID} enque to Queue ({src_port},{dest_port})" ) if FLAG_QUEUE_PRINT else None

                else:
                    raise Exception("not Q type match in floofing")
                      

    def InputHandel(self,src_port, dest,index_event):
        selected_msg = None
        selected_index = 0
        
        for (index,Queue) in enumerate(self.switch_queue.values()):
                if not Queue.empty():
                    
                    msg = Queue.queue[0][0]
                    # target_link = Queue.queue[0][1]
                    
                    if selected_msg is None:
                        selected_msg = msg
                        selected_index = index
                    else:
                        if selected_msg.enter_queue > msg.enter_queue:
                            selected_msg = msg
                            selected_index = index
                            src_port = Queue.src_port
                    


        if selected_msg is None:
            return None,None
        else:
            queue = list(self.switch_queue.values())[selected_index]
            queue.get() #dequeue from queue

            print(f"{CYAN} event {index_event} massage ID {selected_msg.real_msg_id} dequeue from Queue ({queue.src_port},None) left in queue {len(queue.queue)}") if FLAG_QUEUE_PRINT else None
            queue.last_depature = timeline.current
            selected_msg.departure = timeline.current
            self.TotalHolTime[selected_index] += selected_msg.departure - queue.HOL_enter
            if not queue.empty():
                queue.HOL_enter = timeline.current
            return selected_msg, src_port    



    def OutputHandel(self,link_id, dest):
        #NOTE in this situation there is no head of line
        port = self.get_port_from_link(link_id)
        if not self.switch_queue[(None,port)].empty():
            msg = self.switch_queue[(None,port)].queue[0][0]
            self.switch_queue[(None,port)].get()
            Base.obj_list[link_id].busy[self.ID] = True #only for output
            self.switch_queue[(None,port)].last_depature = timeline.current
            msg.departure = timeline.current
            selected_index = 0
            lst_value = list(self.switch_queue.values())
            selected_index = lst_value.index(self.switch_queue[(None,port)])
            print(f"{CYAN} massage ID {msg.real_msg_id} dequeue from Queue (None,{port}) left in queue {len(self.switch_queue[(None,port)].queue)}") if FLAG_QUEUE_PRINT else None
            q = self.switch_queue[(None,port)].HOL_enter
            self.TotalHolTime[selected_index] += msg.departure - self.switch_queue[(None,port)].HOL_enter
            if not self.switch_queue[(None,port)].empty():
                self.switch_queue[(None,port)].HOL_enter = timeline.current
            return msg,port
        return None,None
    

    def priorityHandel(self,link_id, dest):
        #NOTE in this situation there is no head of line
        port = self.get_port_from_link(link_id)

        for priority in range(PRIORITY_NUM ,0, -1):
            if not self.priority_queues[(None,port,priority)].empty():
                msg = self.priority_queues[(None,port,priority)].queue[0][0]
                self.priority_queues[(None,port,priority)].get()
                Base.obj_list[link_id].busy[self.ID] = True #only for output
                self.priority_queues[(None,port,priority)].last_depature = timeline.current
                msg.departure = timeline.current
                #selected_index = 0
                #lst_value = list(self.switch_queue.values())
                #selected_index = lst_value.index(self.switch_queue[(None,port,priority)])
                print(f"{CYAN} massage ID {msg.real_msg_id} dequeue from Queue (None,{port},{priority}) left in queue {len(self.priority_queues[(None,port,priority)].queue)}") if FLAG_QUEUE_PRINT else None
                #q = self.switch_queue[(None,port)].HOL_enter
                #self.TotalHolTime[selected_index] += msg.departure - self.switch_queue[(None,port)].HOL_enter
                # if not self.switch_queue[(None,port)].empty():
                #     self.switch_queue[(None,port)].HOL_enter = timeline.current
                return msg,port
        return None,None

    def VirtualHandel(self,link_id, dest): 

        selected_msg = None
        selected_index = 0
        port = self.get_port_from_link(link_id)

        for (index,Queue) in enumerate(self.switch_queue.values()):
            if Queue.dest_port == port and Queue.src_port != port:   
                if not Queue.empty():
                    msg = Queue.queue[0][0]
                    target_link = Queue.queue[0][1]
                    if target_link == link_id:
                        if selected_msg is None:
                            selected_msg = msg
                            selected_index = index
                        else:
                            if selected_msg.enter_queue > msg.enter_queue:
                                selected_msg = msg
                                selected_index = index  
        if selected_msg is None:
            return None,None
        else:
            queue = list(self.switch_queue.values())[selected_index]
            queue.get()
            Base.obj_list[link_id].busy[self.ID] = True
            print(f"{CYAN} massage ID {selected_msg.real_msg_id} dequeue from Queue ({queue.src_port},{queue.dest_port}) left in queue {len(queue.queue)}") if FLAG_QUEUE_PRINT else None
            queue.last_depature = timeline.current
            selected_msg.departure = timeline.current
            self.TotalHolTime[selected_index] += selected_msg.departure - queue.HOL_enter
            if not queue.empty():
                queue.HOL_enter = timeline.current   
            return selected_msg,selected_index

    def get_link_from_port(self, port):
        return self.ports[port]

    def flooting_for_input(self, msg: L2Message, src_port, link_id):
        time = timeline.current #TODO check if remove
        # learn the source port. if not exist update the mac table
        #check if the  destination exist . if not make flooding even if yes use SEND evend and send the message and uppdate.
        self.update_mac_table(msg.source_mac_address, link_id) #update the source in the table
        src_port = self.get_port_from_link(link_id)
        if self.is_in_mac_table(msg.dest_mac_address):
            
            dest_index = self.get_entry_index(msg.dest_mac_address)
            if abs(timeline.current - self.mac_table[dest_index].ttl) < TTL:# if  exist
                print("NO flooding") if FLOODING_FLAG else None
                self.mac_table[dest_index].ttl = timeline.current #update the lase time used to dest entrie
                dest_port = self.mac_table[dest_index].port_number
                target_link_id = self.ports[dest_port]
                dest = Base.obj_list[target_link_id].first_end_point
                if self.ID == Base.obj_list[target_link_id].first_end_point:
                    dest = Base.obj_list[target_link_id].second_end_point

                #send without  flooding   

                link_obj = Base.obj_list[target_link_id]
                transmission_time = (msg.msg_size * 8)/ link_obj.transmission_rate #seconds
                t_prop = link_obj.prop_delay
                msg.total = t_prop +transmission_time + link_obj.error
                if time >=link_obj.valid_time[self.ID]: #link is empty 
                   msg.send_time = time
                   msg.total+=time
                   if cut_time_func(msg.total):
                       self.switch_queue[(src_port,None)].total_Hol += self.calculate_HOL(self.switch_queue[(src_port,None)].queue ,target_link_id, link_obj.valid_time[self.ID],timeline.current)
                       Base.obj_list[target_link_id].valid_time[self.ID]= msg.total
                       Base.obj_list[target_link_id].link_close.append(msg.send_time)
                       Base.obj_list[target_link_id].link_open.append(msg.total)
                       timeline.insert_into_ordered_list(Event(msg.total, EventType.RECIEVE, target_link_id, dest, msg.ID)) #same idia like sent in host
                       timeline.insert_into_ordered_list(Event(time, EventType.OpenLink, link_id, self.ID, msg.ID))
                       print(f"Link {link_obj.ID} will open in t = {msg.total}")
                   #print (f"1 sending from {msg.source_mac_address} ----> {msg.dest_mac_address}, the current time is: {timeline.current} and the event time  send is: {time} msg id {msg.ID}")
                   print(f"link empty the valid time is: {link_obj.valid_time[self.ID]}") if VALID_LINK_FLAG else None
                   
                else:
                   self.switch_queue[(src_port,None)].queue.appendleft((msg,target_link_id))
                   print(f"{CYAN}event  massage ID {msg.ID} enque to top of the head to INPUT Queue ({src_port},None) in queue now : {len(self.switch_queue[(src_port,None)].queue)}" ) if FLAG_QUEUE_PRINT else None

                   timeline.insert_into_ordered_list(Event(link_obj.valid_time[self.ID], EventType.OpenLink, link_id, self.ID, msg.ID))
                #    msg.send_time = link_obj.valid_time[self.ID]
                #    print(f"will be send in t= {link_obj.valid_time[self.ID]}") if FLAG else None
                #    msg.total += link_obj.valid_time[self.ID]
                #    next_time = link_obj.valid_time[self.ID] #next time the switch will be ready for another packet
                #    if cut_time_func(msg.total):
                #        self.switch_queue[(src_port,None)].total_Hol += self.calculate_HOL(self.switch_queue[(src_port,None)].queue ,target_link_id, link_obj.valid_time[self.ID],msg.send_time)
                #        link_obj.valid_time[self.ID]= msg.total
                       
                #        timeline.insert_into_ordered_list(Event(link_obj.valid_time[self.ID], EventType.RECIEVE, target_link_id, dest, msg.ID))
                #        timeline.insert_into_ordered_list(Event(next_time, EventType.OpenLink, link_id, self.ID, msg.ID))
                #        print(f"Link {link_obj.ID} will open in t = {msg.total}")
                #    #print (f"2 sending from {msg.source_mac_address} ----> {msg.dest_mac_address}, the current time is: {timeline.current} and the event time  send is: {link_obj.valid_time[self.ID]} msg id {msg.ID}")
                #    print(f"recieved in t= {link_obj.valid_time[self.ID]}") if FLAG else None
                #    #send message to ths nic in dedicated port
                   
                return

                
            
            else:
                self.mac_table.pop(dest_index) #the entrie is not valid, delete it
        #flooding - create new massege and send it to all ports (without the reciving port)
        # elif self.Q_type != Qeueu_type.INPUT:
        print("performing flooding") if FLOODING_FLAG else None
        msg.alive = False #TODO try
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
                dest_port = self.get_port_from_link(nic_id)
                flood_msg = L2Message(msg.source_mac_address, msg.dest_mac_address, msg.msg_size )
                flood_msg.Hol_link = metadata_connections[flood_msg.dest_mac_address]
                flood_msg.real_msg_id = msg.real_msg_id


                transmission_time = (flood_msg.msg_size * 8)/ link_obj.transmission_rate #seconds
                t_prop = link_obj.prop_delay
                flood_msg.total = t_prop +transmission_time + link_obj.error
                if time >=link_obj.valid_time[self.ID]: # the link empty , we can send
                    flood_msg.send_time = time
                    flood_msg.total+=time
                    if cut_time_func(flood_msg.total):
                        self.switch_queue[(src_port,None)].total_Hol += self.calculate_HOL(self.switch_queue[(src_port,None)].queue ,nic_id, link_obj.valid_time[self.ID],time)
                        link_obj.valid_time[self.ID]= flood_msg.total
                        Base.obj_list[nic_id].link_close.append(flood_msg.send_time)
                        Base.obj_list[nic_id].link_open.append(flood_msg.total)
                        print(f"Link {link_obj.ID} will open in t = {link_obj.valid_time[self.ID]}")    
                        timeline.insert_into_ordered_list(Event(flood_msg.total, EventType.RECIEVE, nic_id, dest, flood_msg.ID)) #same idia like sent in host
                        timeline.insert_into_ordered_list(Event(time, EventType.OpenLink, link_id, self.ID, flood_msg.ID))
                            
                    #print (f"3 sending from {msg.source_mac_address} ----> {msg.dest_mac_address} thgho link {nic_id}, the current time is: {timeline.current} and the event time  send is: {time} msg id {flood_msg.ID}")

                    print(f"link empty the valid time is: {link_obj.valid_time[self.ID]}") if VALID_LINK_FLAG else None
                else:
                    flood_msg.send_time = link_obj.valid_time[self.ID]
                    print(f"will be send in t= {link_obj.valid_time[self.ID]}") if FLAG else None
                    flood_msg.total += link_obj.valid_time[self.ID]
                    next_time = link_obj.valid_time[self.ID]
                    if cut_time_func(flood_msg.total):
                        self.switch_queue[(src_port,None)].total_Hol += self.calculate_HOL(self.switch_queue[(src_port,None)].queue ,nic_id, link_obj.valid_time[self.ID],flood_msg.send_time)

                        link_obj.valid_time[self.ID]= flood_msg.total
                            
                        timeline.insert_into_ordered_list(Event(link_obj.valid_time[self.ID], EventType.RECIEVE, nic_id, dest, flood_msg.ID))
                        timeline.insert_into_ordered_list(Event(next_time, EventType.OpenLink, link_id, self.ID, flood_msg.ID))
                        print(f"Link {link_obj.ID} will open in t = {link_obj.valid_time[self.ID]}")    
                    #print (f"4 sending from {msg.source_mac_address} ----> {msg.dest_mac_address} thgho link {nic_id}, the current time is: {timeline.current} and the event time  send is: {link_obj.valid_time[self.ID]} msg id {flood_msg.ID}")

            #self.print_table()



    def calculate_HOL(self,queue, link_id, interval_min, interval_max):
        if len(queue)==0 or queue[0][0].Hol_link == link_id:
            return 0
        else:
            min_val = None
            for msg in (t[0] for t in queue):
                if msg.Hol_link == link_id and msg.enter_queue > interval_min:
                    min_val = msg.enter_queue
                    break
            if min_val:
                return interval_max - min_val
            else:
                return 0



        pass

    def GPS(self): # [1:msg1,2:msg2,3:msg3]
        threshold = 0.000001
        result_list = [value for value in self.packet_list.values() if value is not None] #list without None
        packet_list_sorted = sorted(result_list, key=lambda x: (x.enter_queue, -1*x.priority))
        waiting_queue = [ deque() for i in range(PRIORITY_NUM )]
        current_packets = [None,None,None]
        relative_BW = [None,None,None]
        start_index =0 #there is at leest one packet
        flow = packet_list_sorted[0].priority
        current = packet_list_sorted[0].enter_queue
        current_packets[flow-1] = packet_list_sorted.pop(0)




        while len(packet_list_sorted):
            update_current(packet_list_sorted, current, current_packets,waiting_queue)

            relative_BW_Calc(relative_BW, current_packets)
            min = calc_min_finish(relative_BW,current_packets)

            if (min + current) < packet_list_sorted[0].enter_queue:# if the packete end before new packet arrive
                current += min
                for packet in current_packets:
                    if packet != None:
                        packet.msg_size = packet.msg_size - min * relative_BW[packet.priority - 1]*RECIEVE_TRANS
                        if abs(packet.msg_size) < threshold:
                            packet.msg_size = 0.0

                        if packet.msg_size == 0:
                            self.packet_list[packet.priority] = None
                            return packet
                            # if len(waiting_queue[packet.flow - 1]) :
                            #     current_packets[packet.flow - 1] = waiting_queue[packet.flow - 1].pop()
                            # else:
                            #     current_packets[packet.flow - 1] = None
            else:
                new_packet = packet_list_sorted.pop(0)

                if current_packets[new_packet.priority  - 1] != None:
                    waiting_queue[new_packet.priority - 1].append(new_packet)
                    continue
                else:
                    last_current = current
                    current = new_packet.enter_queue
                    for packet in current_packets:
                        if packet != None:
                            packet.msg_size = packet.msg_size - (new_packet.enter_queue - last_current) * relative_BW[packet.priority - 1] * RECIEVE_TRANS
                            if abs(packet.msg_size) < threshold:
                                packet.msg_size = 0.0
                            if packet.msg_size == 0:
                                self.packet_list[packet.priority] = None
                                return packet
                                # if len(waiting_queue[packet.flow - 1]):
                                #     current_packets[packet.flow - 1] = waiting_queue[packet.flow -1 ].pop()
                                # else:
                                #     current_packets[packet.flow - 1] = None

                    current_packets[new_packet.priority - 1] = new_packet

      
        while any(x is not None for x in current_packets):
            relative_BW_Calc(relative_BW, current_packets)
            min = calc_min_finish(relative_BW, current_packets)
            current += min
            for packet in current_packets:
                if packet != None:
                    packet.msg_size = packet.msg_size - min * relative_BW[packet.priority - 1] * RECIEVE_TRANS
                    if abs(packet.msg_size) < threshold:
                        packet.msg_size = 0.0
                    if packet.msg_size == 0:
                        self.packet_list[packet.priority] = None
                        return packet
                        if len(waiting_queue[packet.priority - 1]):
                            current_packets[packet.priority - 1] = waiting_queue[packet.priority - 1].pop()
                        else:
                            current_packets[packet.priority - 1] = None


    def HandelQueue(self, link_id, index=0):
        #the link id is the link where the message is going to go NOT wherre it came from
        """
        this function go over all the relevant queues and search if there is msg to send
        if there is, 
        1.dequeue it from relevant queue
        2.make recieve event to send the messge next

        if there is not msg to send is not doing eneting 
        """
        msg = None 
        src_port = -1
        dest = Base.obj_list[link_id].first_end_point
        if self.ID == Base.obj_list[link_id].first_end_point:
            dest = Base.obj_list[link_id].second_end_point       
        
        if self.Q_type == Qeueu_type.INPUT.value:
            msg,src_port  = self.InputHandel(link_id, dest, index)
           

        elif self.Q_type == Qeueu_type.OUTPUT.value:
            if self.SchedualAlg == alorithm.FIFO.value:
                msg,dest_port = self.OutputHandel(link_id, dest)

            if self.SchedualAlg == alorithm.Priority.value:
                msg,dest_port = self.priorityHandel(link_id, dest)

            if self.SchedualAlg == alorithm.PGPS.value:
                
                for key in self.priority_queues.keys():
                    if self.priority_queues[key].empty():
                        continue
                    else:
                        if self.packet_list[key[2]] == None:
                            temp_msg = self.priority_queues[key].get() #insert message to packet list for GPS
                            print(f"{CYAN}  massage ID {temp_msg[0].real_msg_id} dequeue from Queue (None,0,{key[2]}) left in queue {len(self.priority_queues[key].queue)}") if FLAG_QUEUE_PRINT else None
                            self.packet_list[key[2]] = temp_msg[0] #this is type L2message
                count = 0        
                for key in self.packet_list:
                    if self.packet_list[key] != None:
                        count += 1
                        send_msg = self.packet_list[key]
                if count == 1:
                    msg = send_msg
                    self.packet_list[send_msg.priority] = None
                    msg.departure =timeline.current 
                    
                elif count > 1:
                    msg = self.GPS()
                    msg.departure =timeline.current 
                    
                else:
                    msg = None               

                 
                     


        elif self.Q_type == Qeueu_type.VIRTUAL.value:
            msg,queue_index = self.VirtualHandel(link_id, dest)
        else:
            raise Exception("couldn't finde the correct type Queue")
       
        if msg is None:
            return
        
        if self.Q_type == Qeueu_type.INPUT.value:
           #check if flooding or not, any case, send a massage or massages
           self.flooting_for_input(msg, src_port,link_id)
           return
        
        
        dest = Base.obj_list[link_id].first_end_point
        if self.ID == Base.obj_list[link_id].first_end_point:
            dest = Base.obj_list[link_id].second_end_point
            
        # queue =  None
        # if self.Q_type == Qeueu_type.VIRTUAL.value: 
        #     queue = list(self.switch_queue.values())[queue_index]
        # else:
        #     queue =  self.switch_queue[(None,dest_port)]

        link_obj = Base.obj_list[link_id]
        if link_obj.valid_time[self.ID] >  timeline.current and False:#never happend because we get to this function only when the link is valid
            if self.Q_type == Qeueu_type.OUTPUT :
                queue.queue.appendleft((msg,link_id))
                
            elif self.Q_type == Qeueu_type.VIRTUAL:
                
                queue.appendleft((msg,link_id))    

        transmission_time = (msg.real_size * 8)/ link_obj.transmission_rate #seconds
        t_prop = link_obj.prop_delay
        msg.total = t_prop +transmission_time + link_obj.error
        msg.send_time = timeline.current
        msg.total+=max(timeline.current,Base.obj_list[link_id].valid_time[self.ID])
        if cut_time_func(msg.total):
            # queue.total_Hol += self.calculate_HOL(queue.queue ,link_id, link_obj.valid_time[self.ID],timeline.current)
            Base.obj_list[link_id].valid_time[self.ID]= max(msg.total,Base.obj_list[link_id].valid_time[self.ID])
            timeline.insert_into_ordered_list(Event(Base.obj_list[link_id].valid_time[self.ID], EventType.RECIEVE, link_id, dest, msg.ID)) #same idia like sent in host
            timeline.insert_into_ordered_list(Event(Base.obj_list[link_id].valid_time[self.ID], EventType.OpenLink, link_id, self.ID, msg.ID))
            msg.departure = Base.obj_list[link_id].valid_time[self.ID]
            self.lst_times.append((msg.enter_queue,msg.departure,msg.priority))
            if self.FIRST_IN_SWITCH:
                self.first_in_switch_val = msg.departure
                self.FIRST_IN_SWITCH = False
            self.last_in_switch_val = msg.departure
            self.finish_times_by_priority[msg.priority] += (msg.departure- msg.enter_queue )/num_of_packets
            if self.SchedualAlg == alorithm.PGPS.value:
                print(f"{BackGround.BG_GREEN}msg, arrive: {msg.enter_queue} departure : {msg.departure} priority {msg.priority}")
            #print (f"1 sending from {msg.source_mac_address} ----> {msg.dest_mac_address}, the current time is: {timeline.current} and the event time  send is: {time} msg id {msg.ID}")
            #print(f"link empty the valid time is: {link_obj.valid_time[self.ID]}") if VALID_LINK_FLAG else None
                        
        return

    def StatisticHOL(self):
        percentages = []
        queue_labels = []

        for (index,Queue) in enumerate(self.switch_queue.values()):
            if ENABLE_CUT_TIME:
                percent = (Queue.total_Hol/cut_time) * 100   
            else:
                percent = (Queue.total_Hol/timeline.current) * 100

            print(f"{ORANGE} the HOL percentage of Queue ({Queue.src_port}, {Queue.dest_port}) is {percent} %\n") 
            print(f"max size queue {Queue.max_queue} now the queue size is: {len(Queue.queue)}")
            percentages.append(percent)
            queue_labels.append(f"Queue ({Queue.src_port}, {Queue.dest_port})")

        
        if SHOW_BAR_QUEUE:
            # Create the bar graph
            plt.figure(figsize=(12, 6))
            plt.bar(queue_labels, percentages, color='orange')

            # Add title and labels
            plt.title('Queue HOL Percentages')
            plt.xlabel('Queue')
            plt.ylabel('Percentage')
            plt.xticks(rotation=45, ha="right")

            # Show the plot
            plt.tight_layout()
            plt.show()       
                            
   
        
                    

def cut_time_func(time):
    if (time >= cut_time) and ENABLE_CUT_TIME:
            return False
    return True

# def generate_mac_address(): #return mac
#     # Generate six pairs of hexadecimal digits
#     mac = [random.randint(0x00, 0xFF) for _ in range(6)]
#     # Format as a MAC address
#     mac_address = ':'.join(f'{byte:02X}' for byte in mac)
#     return mac_address

def generate_mac_address(): #return mac
    # Generate six pairs of hexadecimal digits
    #mac = [random.randint(0x00, 0xFF) for _ in range(6)]
    mac = random.randint(0x00, 0xFF)
    # Format as a MAC address
    #mac_address = ':'.join(f'{byte:02X}' for byte in mac)
    mac_address = f"11:11:11:11:11:{mac:02X}"
    return mac_address
             






timeline = Timeline()
G = nx.Graph()


def show_topology():
    node_types = nx.get_node_attributes(G, 'type')
    node_lables = nx.get_node_attributes(G, 'name')
    edge_lables = nx.get_edge_attributes(G, 'lable')
    pos = nx.spring_layout(G)
    for node_type, shape in type_to_shape.items():
        nodes_of_type = [node for node, type_ in node_types.items() if type_ == node_type]
        nx.draw_networkx_nodes(G, pos, nodelist=nodes_of_type, node_shape=shape)
    nx.draw(G,pos, with_labels=True, labels=node_lables, node_color='lightblue', font_size=6)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_lables, font_color='red')
    plt.title('Netwok topology')
    plt.show() if SHOW_TOPOLOGY else None
    #plt.close()
metadata_connections = {}
num_host_1 = 1

lst_times = []


def plot_first_departure_times(departure_times):
    """
    Plots the first departure times for FIFO, Priority, and PGPS.

    Parameters:
    departure_times (list): A list of first departure times in the order [FIFO, Priority, PGPS].
    """
    if len(departure_times) != 3:
        raise ValueError("The departure_times list must have exactly three elements.")

    labels = ['FIFO', 'Priority', 'PGPS']

    # Create the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(labels, departure_times, color=['blue', 'green', 'red'])

    # Add titles and labels
    plt.title('First Departure Times')
    plt.xlabel('Scheduling Algorithm')
    plt.ylabel('Time')

    # Show the plot
    plt.show()



def plot_last_departure_times(departure_times):
    """
    Plots the first departure times for FIFO, Priority, and PGPS.

    Parameters:
    departure_times (list): A list of first departure times in the order [FIFO, Priority, PGPS].
    """
    if len(departure_times) != 3:
        raise ValueError("The departure_times list must have exactly three elements.")

    labels = ['FIFO', 'Priority', 'PGPS']

    # Create the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(labels, departure_times, color=['blue', 'green', 'red'])

    # Add titles and labels
    plt.title('Last Departure Times')
    plt.xlabel('Scheduling Algorithm')
    plt.ylabel('Time')

    # Show the plot
    plt.show()
   

def plot_algorithm_performance(data):
    """
    Plots a grouped bar chart for the given algorithm performance data.

    Parameters:
    data (dict): A dictionary where keys are algorithm names and values are dictionaries
                 with priority as keys and corresponding values as values.
    """
    # Extracting the priorities and the corresponding values
    priorities = list(next(iter(data.values())).keys())
    algorithms = list(data.keys())

    # Creating an array of the values for each priority
    values = {p: [data[alg][p] for alg in algorithms] for p in priorities}

    # Plotting
    x = np.arange(len(algorithms))  # the label locations
    width = 0.2  # the width of the bars

    fig, ax = plt.subplots()
    rects = []
    for i, p in enumerate(priorities):
        rects.append(ax.bar(x + (i - 1) * width, values[p], width, label=f'Priority {p}'))

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_xlabel('Algorithm')
    ax.set_ylabel('Values')
    ax.set_title('Algorithm Performance by Priority')
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms)
    ax.legend()

    # Add labels on top of the bars
    for i, rect in enumerate(rects):
        for bar in rect:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height, f'{height:.2f}', ha='center', va='bottom')

    fig.tight_layout()

    plt.show()

sched_firs_enter = []
sched_last_enter = []
finish_times_by_priority_lst = {alorithm.FIFO:0,alorithm.Priority:0,alorithm.PGPS:0}



def main():
    counrter_recieve = 0
    first_in_switch_val = 0
    last_in_switch_val = 0
    print_large_text()
    idna_of_times = []
    for i in range(3*num_of_packets):
        idna_of_times.append(Time(i//num_of_packets +1))
    index_time = 0

    

  

    algo = [alorithm.FIFO, alorithm.Priority, alorithm.PGPS]
    for ched in algo:
        index_time = 0
        # 2 switch LAN project 1
        # #     making hosts group    
        #     num_host_1 = random.randint(2,4)
        #     group_host1 = [Host(generate_mac_address())for i in range(num_host_1)]
        #     num_host_2 = random.randint(2,4)
        #     group_host2 = [Host(generate_mac_address())for i in range(num_host_2)]
            

        #     #making 2 switch
        #     switch1= Switch(10, num_host_2 + num_host_1-2, generate_mac_address())
        #     switch2= Switch(10, num_host_2 + num_host_1-2,generate_mac_address())
            
            
        #     #connecte links
        #     times=[]
        #     switch_Link= Link(switch1.ID,switch2.ID)
        #     switch1.ports[0]= switch_Link.ID
        #     switch2.ports[0]= switch_Link.ID
        #     for (index,host) in enumerate(group_host1):
        #         for i in range(num_of_packets):
        #             host.time.append( Time(host.ID))
        #         host.acumulate()
        #         times.append(host.time)    
        #         link = Link(host.ID,switch1.ID)
        #         host.nic = link.ID
        #         switch1.ports[index+1] = link.ID

        #     for (index,host) in enumerate(group_host2):
        #         for i in range(num_of_packets):
        #             host.time.append( Time(host.ID))
        #         times.append(host.time)
        #         host.acumulate()    
        #         link = Link(host.ID,switch2.ID)
        #         host.nic = link.ID
        #         switch2.ports[index+1] = link.ID    
            
        #     timeline.merge_lists(*times) #linst of order events


        # project 2 topology
        # #     making hosts group 
            
        num_host_1 = 4
        group_host1 = [Host(generate_mac_address())for i in range(num_host_1)]
            
            

        #     #making 2 switch
        switch1= Switch2(10,  num_host_1, generate_mac_address(),num_host_1, TYPE_QUEUE, SchedualAlg=ched)
        #    
            
            
        #     #connecte links
        times=[]
        #     
        

            
        for (index,host) in enumerate(group_host1):
            
            if index == 0 :
                print(f"Host mac is:{host.host_mac_address} is destination")
                link = Link(host.ID,switch1.ID,prop_delay=0)
                metadata_connections[host.host_mac_address] = link.ID
                host.nic = link.ID
                link.transmission_rate = RECIEVE_TRANS
                switch1.ports[index] = link.ID
                print(f"Link ID {link.ID} have propogation delay of {link.prop_delay}")
                #enter to swich mac table to disable flooding
                switch1.add_entry(host.host_mac_address,0)
                continue
            print(f"Host mac is:{host.host_mac_address}")
            for i in range(num_of_packets):
                #t = Time(host.ID)
                t = copy.deepcopy(idna_of_times[index_time])
                index_time += 1
                
                host.time.append(t)
                
            #host.make_random_set_dest() 
        
            host.dest_group = [0] #everyone send to host[0]
    
            host.acumulate()
            
            times.append(host.time)
            prop =0
        
            link = Link(host.ID,switch1.ID,prop_delay=prop)
            metadata_connections[host.host_mac_address] = link.ID
            print(f"Link ID {link.ID} have propogation delay of {link.prop_delay}")
            host.nic = link.ID
            switch1.ports[index] = link.ID


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
            #HOST to HOST scenario  need to open for test 1 and 2 Hosts up
            # link = Link(host1.ID,host2.ID)
            # host1.nic = link.ID
            # host2.nic = link.ID

        

            # for i in range(num_of_packets):
            #     host1.time.append( Time(host1.ID)) #t=
            #     host2.time.append( Time(host2.ID))#[0, 0.2, 0.4 , 0.5]
            #     host3.time.append( Time(host3.ID))

            # host1.acumulate()
            # host2.acumulate()
            # host3.acumulate() 

            # timeline.merge_lists(host1.time, host2.time) #for Test 1 Host Host    
            # timeline.merge_lists(host1.time, host2.time, host3.time) #linst of order events
        counter = 0
        show_topology()

        for t in timeline.order_timeline:
            timeline.event_timeline.append(Event(t.time, EventType.CREATE, Base.obj_list[t.ID].ID, Base.obj_list[t.ID].nic))
        timeline.event_timeline[-1].last_create =True
        for (index,event) in  enumerate(timeline.event_timeline):
            timeline.current = event.Schedule_time #TODO check
            if (timeline.current >= cut_time) and ENABLE_CUT_TIME:
                print("end simulation")
                break
            
            timeline.index = index
            
            #TODO making polling of queue each iteration
            

            if event.Event_type == EventType.CREATE  :
                Base.obj_list[event.Schedule_obj_ID].create_L2Message(event.Schedule_time, timeline, index)
                event.alive = False
                # if event.last_create:
                #     print("finish create!")
                #     switch1.StatisticHOL()
                #     exit(0)


            elif event.Event_type == EventType.SEND  :
                msg = Base.obj_list[event.message_ID]
                Base.obj_list[event.target_obj_ID].send_L2Message(msg, event.Schedule_obj_ID, index) 
                event.alive = False

            elif event.Event_type == EventType.RECIEVE :#deleted event.alive
                counrter_recieve += 1
                msg = Base.obj_list[event.message_ID]
                if msg.alive and event.alive:
                    Base.obj_list[event.target_obj_ID].recieve_L2Message(msg, event.Schedule_obj_ID, index) 
                    event.alive = False
                    counter += 1

            elif event.Event_type == EventType.OpenLink:
                    Base.obj_list[event.target_obj_ID].HandelQueue( event.Schedule_obj_ID,index)     
                    event.alive = False 
            
        print(f"{BackGround.BG_GREEN}================================================")    
        for host in Host.Host_list:
            #avg_recive = host.total_byte_recieved/(counter/NUM_OF_HOST)
            avg_recive = host.total_byte_recieved/(num_of_packets)
            print(f"{BackGround.BG_GREEN}host {host.ID} mac {host.host_mac_address} average is : {avg_recive}")
        print(f"{BackGround.BG_GREEN}================================================")

        print(f"{BackGround.BG_GREEN}================================================")    
        for tup in switch1.lst_times:
            print(f"{BackGround.BG_GREEN}msg, arrive: {tup[0]} departure : {tup[1]} priority {tup[2]}")
        print(f"{BackGround.BG_GREEN}================================================")


        switch1.StatisticHOL()
        print(f"{BackGround.BG_WHITE} check")
        #run on time line if it schedual
        sched_firs_enter.append(switch1.first_in_switch_val)
        sched_last_enter.append(switch1.last_in_switch_val)
        finish_times_by_priority_lst[ched] = switch1.finish_times_by_priority
        switch1.FIRST_IN_SWITCH = True
        switch1.first_in_switch_val = 0
        switch1.last_in_switch_val = 0
        Host.Host_list = []
        Host.priority = 0
        Base.ID_count = 0
        Base.obj_list = []
        Base.obj_list = []
        timeline.current = 0
        timeline.event_timeline = []
        timeline.order_timeline = []

        
    plot_first_departure_times(sched_firs_enter)
    plot_last_departure_times(sched_last_enter)
    plot_algorithm_performance(finish_times_by_priority_lst)
    






if __name__ == "__main__":
    main()