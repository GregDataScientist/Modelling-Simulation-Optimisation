# -*- coding: utf-8 -*-
"""

Modelling, Simulation and Optimisation


The Context
A high-speed train as planned for the HS2 line from London to Birmingham has an acceleration
of 0.72m/s2, about the same as a commuter train. While the trains can brake in an emergency
at 2.5m/s2, the energy optimal deceleration (using regenerative braking) is 0.36m/s2.
The maximum travelling speed of the train is about 300km/h (83.3m/s). Accelerating from 0
to the maximum speed takes therefore 115.7s during which time the train travels about
4,820m. Slow decelerating takes 231.4s and the distance travelled is 9,640m.
A railway line consists of a sequence of signaling blocks. A train is only allowed to enter a
block, when there is no other train in the block and the entry signal is green. When a train
enters a block the entry signal switches to red. The entrance signal switches back to green 5
seconds after the end of the train has left the block.
Depending on the intended maximum traveling speed there is an optimal distance for setting
a pre-signal. At a maximum travelling speed of the train of 300km/h (83.3m/s) the slow
deceleration takes 231.4s and the train travels 9,640m during this time. In this case the presignal would be 10km before the actual signal at the end of one block and the entry to the
next. The length of a block should therefore be at least 10km, but to allow a train to achieve
and run as long as possible at full speed, the block length should be at least 1.5x this length.
The control problem is to keep the trains moving at maximum possible speed. If there is a
slight delay in one train it may cause the train in the following block to decelerate, potentially
down to a stop, and then to reaccelerate. This in turn will delay the train thereafter. Just like
the “traffic jam” effect you know from the motorway. A train can run constantly at full speed
if there is always at least one free block ahead. With a block length of 15km that means that
the distance between two trains should be about 30km, at full speed a travelling time of about
6min. This would indicate that one could achieve a maximum schedule of 10 trains per hour.
The new government under Boris Johnson is pushing the development of HS2. The economic
argument is based on a schedule time of 9 trains per hour.Part 1: Simulation
Create a simulation for the London-Birmingham section of the high-speed line under
assumption of a number k of signalling blocks. A decision on the number of signaling blocks is
required, as the track laying is supposed to start soon. Also a decision on the number of trains
running per hour has to be made.
Depending on the number of signalling blocks simulate the throughput of trains.
Take into account that between Birmingham Interchange and Birmingham Curzon street as
well as between London Old Oak Common and London Euston there will be a practical speed
limit and the traveling times are 5 min between London Euston and London Old Oak Common
(one signalling block) and 9 min between Birhigham Interchange and Birmingham Curzon
Street station (two signalling blocks). Take into account the variability of achievable speeds
due to wind and weather conditions on the stretch between London Old Oak Common and
Birmingham Interchange. Take into account the variability in stop times, i.e. minor delays due
to passenger movements.
London Euston
5 min
London Old Oak Common
31 min
Birmingham Interchange
9 min
Birmingham Curzon Street
The distance between London Old Oak Common Station and Birmingham Interchange Station
is 145km. This could be broken down in up-to 14 blocks. If there are less but longer blocks the
trains could achieve in theory a higher average speed, however the throughput in trains per
hour is smaller.
Part 2: Optimisation
For the project you need to create a simulation of the train network which would give for a
given train schedule (numbers of trains per hour n ∈ {1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20}) and a
given break-down of the line in signalling blocks k ∈ {1, ..., 15} a distribution of average
overall travelling time. The simulation results are fed into an optimisation problem to
determine (nopt, kopt) to achieve an optimal results.
Using the simulation described above solve the following optimisation problems:
(1) Minimise the overall average traveling time.
The overall traveling time consist of the waiting time for the next train and the
actual traveling time until arrival of the train. The problem can be simplified by
assuming a fixed average waiting time (0.5*60/n).
(2) Maximise the throughput of passengers in peak hours.
The trains can be configured to run at a length of 200m (short train, 420 passengers)or 300m (max train, 630 passengers). While longer trains carry potentially more
passengers, you need to consider the walking times at the train station. The walking
speed of a train passenger carrying luggage is between 1.0 and 1.2m/s, which
impacts on the stop times at the station. Also more passengers disembarking and
embarking may lengthen the stop times.
For a more realistic simulation assume a Poisson-Distribution for passengers arriving
at the train station at an average rate of m passengers per hour and how they can
be served by n trains per hour. As the trains are on a tight schedule, we cannot
assume that everyone gets on board during the short stopping time. Assume that
the trains are only filled to 70% of nominal capacity. A backlog of passengers on the
departing station will impact on the average travelling time.
"""


import pandas as pd
import numpy as np
import simpy
import time
import random
import matplotlib.pyplot as plt



lines = ['London','London','London']
destination = ['Birmingham','Birmingham','Birmingham']
stations_from = ['London Euston', 'London Old Oak', 'Birmingham Interchange']
stations_to = ['London Old Oak', 'Birmingham Interchange', 'Birmingham Curzon St']
distance = [15000,145000,30000]
acceleration = [.72,.72,.72]
edbrake = [2.5,2.5,2.5]
deceleration = [.36,.36,.36]
max_speed =[83.3,83.3,83.3]
dwell_time = [10,10,10]
signal = [1,10,2]

data = pd.DataFrame()
data['Lines'] = lines
data['Destination'] = destination
data['From']= stations_from
data['To'] = stations_to
data['Distance']= distance
data['Accel'] = acceleration
data['ED Brake'] = edbrake
data['Decel']= deceleration
data['Max Speed']= max_speed
data['Dwell Time']= dwell_time
data['Signal Block'] = signal

print(data)

#Create function timeTo , to create Drive Time to each station
def timeTo(A, maxV, d, dc):
    """
    A       constant acceleration, m/s²
    maxV    maximumum velocity, m/s
    d       distance, km
    return  time in seconds required to travel
    dc      deceleration, m/s - adding deceleration as it is half the time of acceleration
    """
    tA = maxV/A                 # time to accelerate to maxV
    tD = maxV/dc                # time to decelarate from maxV
    dA = (A*tA)+(dc*tD)               # distance traveled during acceleration from 0 to maxV and back to 0
    
    if (d < dA):                # train never reaches full speed?
        return np.sqrt((2.0*d/A)+(2.0*d/dc))     # time needed to accelerate to half-way point then decelerate to destination
    else:
        return tA + (d-dA)/maxV + tD  # time to accelerate to maxV plus travel at maxV plus decelerate to destination
    

#Create Drive Time
for i in range(len(data)):
    data.at[i, 'Drive Time']=int(timeTo(data.at[i, 'Accel'],data.at[i, 'Max Speed'], data.at[i, 'Distance'],data.at[i, 'Decel'] ))
print(data)     

#Create a dataframe and lists to store simulation results
results = pd.DataFrame()
train=[]
location=[]
times=[]
action =[]

#Create class Train which takes in arguments enviroment,resource,name,direction and number of passengers
class Train(object):  
    def __init__(self,env,res, name, direction,passengers): 
        max_pass = None #Create max pass variable which equal 0
        if name %2: #Create a statement that if the train number is an even number it is a large train holding 620 passengers, otherwise normal train holding 420 passengers.
            max_pass = 620
        else:
            max_pass = 420
        self.max_pass = max_pass
        self.name = "Train " +f'{name}' #Set train name to be "Train + No:"
        self.direction = direction
        self.passengers = passengers
        self.env = env
        self.res = res
        

    
    def run(self):
        here = self.direction[0]  # starting location
        name = self.name
        global train,location,times, action, T1,T2 ,T3#set global variables for sending data to results later
        
        for dest in self.direction[1:]: #Run for every item in direction
            traindata=data[data['From']==here] #set location as here
            num_on = random.randint(1,400) #Set Random variable for passengers getting on the train
            num_off = random.randint(1,400) #set Random variable for passengers getting off the train
            drivetime=traindata.iloc[0].at['Drive Time'] #drive time for the current location
            dwelltime=traindata.iloc[0].at['Dwell Time']  #dwell time for the current location

            #Train Starts at first Station
            yield env.timeout(dwelltime)  # Stops at the each station for dwelltime for location
            if (here =='London Euston'): #If station is London Euston run the following:
                with res.request() as request: #request resource
                    yield request #wait for resource
                    
                    #Start loading passengers
                    print(self.name + ' Loading Passengers at %s at %s' % (here,time.strftime('%H:%M:%S', time.gmtime(env.now))))         
                    #collect Data
                    train.append(name)
                    location.append(here)
                    times.append(time.strftime('%H:%M:%S', time.gmtime(env.now)))
                    action.append('Loading Passengers')
                    #Set conditions for passengers , passengers getting on or off wait 1 sec per passenger
                    #first allow passengers off if(ANY)
                    if (self.passengers >= num_off):   
                        yield env.timeout(num_off*1)                                
                        print(f"{num_off} passengers got off %s : Time is Now: %s" % (self.name ,time.strftime('%H:%M:%S', time.gmtime(env.now))))
                        self.passengers -= num_off                               
                    else:    
                        yield env.timeout(self.passengers*1)
                        print(f"Train {name} is empty - all {self.passengers} passengers got off")
                        self.passengers  = 0                    
                    #Second let passengers getting on the train 
                    if (self.max_pass is None) or (self.passengers + num_on <= self.max_pass):   
                        yield env.timeout(num_on*1)
                        print(f"{num_on} passengers got on %s : Time is Now: %s" % (self.name ,time.strftime('%H:%M:%S', time.gmtime(env.now))))
                        self.passengers += num_on                    
                    else:
                        num_on = self.max_pass - self.passengers
                        yield env.timeout(num_on*1)
                        print(f"Train is now full {num_on} passenger got on %s : Time is Now: %s" % (self.name ,time.strftime('%H:%M:%S', time.gmtime(env.now))))
                        self.passengers = self.max_pass   
                    #Train finished loading and leaving the station    
                    print(f"A total of {self.passengers} passengers are on %s : Time is Now: %s" % (self.name ,time.strftime('%H:%M:%S', time.gmtime(env.now))))
                    print("%s In Transit.....to %s" % (self.name ,dest)) 
                    #Collect Data
                    T1 = (env.now)
                    train.append(name)
                    location.append(here)
                    times.append(time.strftime('%H:%M:%S', time.gmtime(env.now)))              
                    action.append('Leaving Station')
                    res.release(request)
                #Call Block of track    
                yield env.process(Block(env,res2,1,here,name).run()) 
                res2.release(request)
                
                #Create condition to ensure Drive time is the minimum time to next station
                if (((env.now) - T1) <drivetime):
                    print(f"{name} is On Time!!!!")
                    yield env.timeout(drivetime-((env.now)-T1))
                else:
                    print(f"{name} Running behind schedule!!!")
            #Train now arriving at next location
            here = dest #set next location to here
            print(self.name + ' Arriving at %s at %s' % (dest,time.strftime('%H:%M:%S', time.gmtime(env.now))))
            
            if (here =='London Old Oak'): #if location is London Old Oak perform the same functions as it did at London Euston
                with res3.request() as request:
                    yield request
                    print(self.name + ' Loading Passengers at %s at %s' % (here,time.strftime('%H:%M:%S', time.gmtime(env.now))))         
                    train.append(name)
                    location.append(here)
                    times.append(time.strftime('%H:%M:%S', time.gmtime(env.now)))
                    action.append('Loading Passengers')
    
                    if (self.passengers >= num_off):   
                        yield env.timeout(num_off*1)                                
                        print(f"{num_off} passengers got off %s : Time is Now: %s" % (self.name ,time.strftime('%H:%M:%S', time.gmtime(env.now))))
                        self.passengers -= num_off                               
                    else:    
                        yield env.timeout(self.passengers*1)
                        print(f"Train {name} is empty - all {self.passengers} passengers got off")
                        self.passengers  = 0                    
                        #passengers getting on the train 
                    if (self.max_pass is None) or (self.passengers + num_on <= self.max_pass):   
                        yield env.timeout(num_on*1)
                        print(f"{num_on} passengers got on %s : Time is Now: %s" % (self.name ,time.strftime('%H:%M:%S', time.gmtime(env.now))))
                        self.passengers += num_on                    
                    else:
                        num_on = self.max_pass - self.passengers
                        yield env.timeout(num_on*1)
                        print(f"Train is now full {num_on} passenger got on %s : Time is Now: %s" % (self.name ,time.strftime('%H:%M:%S', time.gmtime(env.now))))
                        self.passengers = self.max_pass                
                    print(f"A total of {self.passengers} passengers are on %s : Time is Now: %s" % (self.name ,time.strftime('%H:%M:%S', time.gmtime(env.now))))
                    print("%s In Transit.....to %s" % (self.name ,dest))  
                    #Collect Data
                    T2 = (env.now)
                    train.append(name)
                    location.append(here)
                    times.append(time.strftime('%H:%M:%S', time.gmtime(env.now)))              
                    action.append('Leaving Station')
                    res3.release(request)
                    
                #Call Blocks of track between here and next station
                #Calls are for 3 Blocks, 3 Blocks, 4 Blocks to avoid trains over taking/crashing
                    yield env.process(Block(env,res4,1,here,name).run()) 
                    res4.release(request)
                    yield env.process(Block(env,res5,2,here,name).run()) 
                    res5.release(request)
                    yield env.process(Block(env,res6,3,here,name).run()) 
                    res6.release(request)   
                    yield env.process(Block(env,res7,4,here,name).run()) 
                    res7.release(request) 
                    yield env.process(Block(env,res8,5,here,name).run()) 
                    res8.release(request) 
                    yield env.process(Block(env,res9,6,here,name).run()) 
                    res9.release(request)
                    yield env.process(Block(env,res10,7,here,name).run()) 
                    res10.release(request)
                    yield env.process(Block(env,res11,8,here,name).run()) 
                    res11.release(request)
                    yield env.process(Block(env,res12,9,here,name).run()) 
                    res12.release(request)
                    yield env.process(Block(env,res13,10,here,name).run())
                    res13.release(request)
                    
                #Create condition to ensure Drive time is the minimum time to next station
                if (((env.now) - T2) <drivetime):
                    print(f"{name} is On Time!!!!")
                    yield env.timeout(drivetime-((env.now)-T2))
                else:
                    print(f"{name} Running behind schedule!!!")    
              
                
            #Train now arriving at next location
            here = dest #set next location to here
            print(self.name + ' Arriving at %s at %s' % (dest,time.strftime('%H:%M:%S', time.gmtime(env.now))))
            if (here =='Birmingham Interchange'):
                with res14.request() as request: #If here is Birmingham Interchange perform the same functions as it did at London Euston
                    yield request
                    print(self.name + ' Loading Passengers at %s at %s' % (here,time.strftime('%H:%M:%S', time.gmtime(env.now))))         
                    train.append(name)
                    location.append(here)
                    times.append(time.strftime('%H:%M:%S', time.gmtime(env.now)))
                    action.append('Loading Passengers')
    
                    if (self.passengers >= num_off):   
                        yield env.timeout(num_off*1)                                
                        print(f"{num_off} passengers got off %s : Time is Now: %s" % (self.name ,time.strftime('%H:%M:%S', time.gmtime(env.now))))
                        self.passengers -= num_off                               
                    else:    
                        yield env.timeout(self.passengers*1)
                        print(f"Train {name} is empty - all {self.passengers} passengers got off")
                        self.passengers  = 0                    
                        #passengers getting on the train 
                    if (self.max_pass is None) or (self.passengers + num_on <= self.max_pass):   
                        yield env.timeout(num_on*1)
                        print(f"{num_on} passengers got on %s : Time is Now: %s" % (self.name ,time.strftime('%H:%M:%S', time.gmtime(env.now))))
                        self.passengers += num_on                    
                    else:
                        num_on = self.max_pass - self.passengers
                        yield env.timeout(num_on*1)
                        print(f"Train is now full {num_on} passenger got on %s : Time is Now: %s" % (self.name ,time.strftime('%H:%M:%S', time.gmtime(env.now))))
                        self.passengers = self.max_pass                
                    print(f"A total of {self.passengers} passengers are on %s : Time is Now: %s" % (self.name ,time.strftime('%H:%M:%S', time.gmtime(env.now))))
                    print("%s In Transit.....to %s" % (self.name ,dest)) 
                    #Collect Data
                    T3 = (env.now)
                    train.append(name)
                    location.append(here)
                    times.append(time.strftime('%H:%M:%S', time.gmtime(env.now)))              
                    action.append('Leaving Station')
                    res14.release(request)
                #Call Blocks of track between here and next station    
                    yield env.process(Block(env,res15,1,here,name).run()) 
                    res15.release(request)
                    yield env.process(Block(env,res16,2,here,name).run()) 
                    res16.release(request)
                if (((env.now) - T3) <drivetime):
                    print(f"{name} is On Time!!!!")
                    yield env.timeout(drivetime-((env.now)-T3))
                else:
                    print(f"{name} Running behind schedule!!!")
               
            #Train now arriving at next location
            here = dest #set next location to here
            print(self.name + ' Arriving at %s at %s' % (dest,time.strftime('%H:%M:%S', time.gmtime(env.now))))
            if (here =='Birmingham Curzon St'): #If station is Birmingham Curzon St, only allow passengers off and return to depot
                with res17.request() as request:
                    yield request
                    print(self.name + ' is the last stop at %s at %s' % (here,time.strftime('%H:%M:%S', time.gmtime(env.now))))         
                    train.append(name)
                    location.append(here)
                    times.append(time.strftime('%H:%M:%S', time.gmtime(env.now)))
                    action.append('Loading Passengers')                 
                    print(f"LAST STOP all {self.passengers} passengers got off %s : Time is Now: %s" % (self.name ,time.strftime('%H:%M:%S', time.gmtime(env.now))))
                    yield env.timeout(self.passengers)  
                    self.passengers = 0
                                                

                    print("%s In Transit.....to the depot." % (self.name))                  
                    train.append(name)
                    location.append(here)
                    times.append(time.strftime('%H:%M:%S', time.gmtime(env.now)))              
                    action.append('Leaving Station')
                    res17.release(request)
                    yield env.timeout(160) 
                    here = 'Depot'
                    print(f"{self.name} has arrived at the Depot at %s" % (time.strftime('%H:%M:%S', time.gmtime(env.now))))
                    train.append(name)
                    location.append(here)
                    times.append(time.strftime('%H:%M:%S', time.gmtime(env.now)))              
                    action.append('Arriving at')
                

                     
          
      
#Create the block class
class Block(object): 
    def __init__(self,env,resblock,no,loc,name): #Initialise and take in args environment, resource, block number, location and train.
        self.env = env
        self.no = no
        self.loc = loc
        self.name = name
        self.resblock = resblock
        
    def run(self): #run process
        resblock = self.resblock
        with resblock.request() as request:
            yield request
            loc = self.loc
            no = self.no
            name = self.name
            print('%s has entered block %s after %s at %s' %(name,no,loc,time.strftime('%H:%M:%S', time.gmtime(env.now))))
            train.append(name)
            location.append(f"{loc} Block {no}")
            times.append(time.strftime('%H:%M:%S', time.gmtime(env.now)))              
            action.append('Entering Block')
            randnum = random.randint(1,1001)
            if (randnum < 751): # 75% chance no issues on  the block
                print(f'{name}: No issues in block %s were on schedule' %(no))
                yield env.timeout(300)
            if (randnum in range (752,761)): #1% chance of animals on the track / time to clear 1 to 10 mins
                print(f'{name}: DELAY!!! Sorry folk animals are on the track!!! we are working to move them')
                yield env.timeout(random.randint(60,600))
                yield env.timeout(300)
            if (randnum in range(762,951)): # 19% chance of bad weather slowing down the train on the block / 15 to 100 secs
                print(f'{name}: DELAY!!! Runnning a little slower folks due to the bad weather')
                yield env.timeout(random.randint(15,100))
                yield env.timeout(300)
            else: #5% chance of random ticket inspection / 2 to 3 min delay
                print(f'{name}: DELAY!!! Ticket inspection!!!! in block %s' % (no))
                yield env.timeout(random.randint(120,180))
                yield env.timeout(300)
            train.append(name)
            location.append(f"{loc} Block {no}")
            times.append(time.strftime('%H:%M:%S', time.gmtime(env.now)))              
            action.append('Leaving Block')













                
env = simpy.Environment()            
res = simpy.Resource(env, capacity = 1)
res2 = simpy.Resource(env, capacity = 1)
res3 = simpy.Resource(env, capacity = 1)
res4 = simpy.Resource(env, capacity = 1)
res5 = simpy.Resource(env, capacity = 1)
res6 = simpy.Resource(env, capacity = 1)
res7 = simpy.Resource(env, capacity = 1)
res8 = simpy.Resource(env, capacity = 1)
res9 = simpy.Resource(env, capacity = 1)
res10 = simpy.Resource(env, capacity = 1)
res11 = simpy.Resource(env, capacity = 1)
res12 = simpy.Resource(env, capacity = 1)
res13 = simpy.Resource(env, capacity = 1)
res14 = simpy.Resource(env, capacity = 1)
res15 = simpy.Resource(env, capacity = 1)
res16 = simpy.Resource(env, capacity = 1)
res17 = simpy.Resource(env, capacity = 1)

def line(env,res,start =21600, stop = 25200, timing=300): # Start lines at 6 o clock for 1 hour and with 8 trains per hour
    stations=data['From'].to_list() # The the list of stations on the line
    stations+=[data['To'].to_list()[-1]]
    yield env.timeout(start-env.now) # Start the lines at 6 am
    for i in range(int((stop-start)/timing)): # For each 450 seconds(timing) between the start and stop time run a train
        t=Train(env,res,i+1, stations,0)
        env.process(t.run())
        yield env.timeout(timing)       
        




np.random.seed(0)

env.process(line(env,res))

env.run()
results['Trains'] = train
results['Action'] = action
results['location'] = location
results['Time'] = times
results.to_csv('results.csv')

print(results)  

resultsdata = pd.read_csv('results.csv')

analysis = pd.DataFrame(resultsdata)
print (analysis)

trains = analysis['Trains'].unique()
print(trains)

def get_sec(time_str):
    """Get Seconds from time."""
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)




train1 = analysis.loc[analysis['Trains'] == "Train 1"]

train1s = []
train1s2 =[]
for i in train1['Time']:
    j = get_sec(i)
    train1s.append(j-21600)
    train1s2.append(j-21600)
    
train1['Time in sec'] = train1s
train1['Time in sec normalised'] = train1s2

train2 = analysis.loc[analysis['Trains'] == "Train 2"]
train2s = []
train2s2 = []
for i in train2['Time']:
    j = get_sec(i)
    train2s.append(j-21600)
    train2s2.append(j-21600-360)
    
train2['Time in sec'] = train2s
train2['Time in sec normalised'] = train2s2

train3 = analysis.loc[analysis['Trains'] == "Train 3"]
train3s = []
train3s2 = []
for i in train3['Time']:
    j = get_sec(i)
    train3s.append(j-21600)
    train3s2.append(j-21600-720)
    
train3['Time in sec'] = train3s
train3['Time in sec normalised'] = train3s2

train4 = analysis.loc[analysis['Trains'] == "Train 4"]
train4s = []
train4s2 = []
for i in train4['Time']:
    j = get_sec(i)
    train4s.append(j-21600)
    train4s2.append(j-21600-1080)
    
train4['Time in sec'] = train4s
train4['Time in sec normalised'] = train4s2


train5 = analysis.loc[analysis['Trains'] == "Train 5"]

train5s = []
train5s2 = []
for i in train5['Time']:
    j = get_sec(i)
    train5s.append(j-21600)
    train5s2.append(j-21600-1440)
    
train5['Time in sec'] = train5s
train5['Time in sec normalised'] = train5s2

train6 = analysis.loc[analysis['Trains'] == "Train 6"]

train6s = []
train6s2 = []
for i in train6['Time']:
    j = get_sec(i)
    train6s.append(j-21600)
    train6s2.append(j-21600-1800)
train6['Time in sec'] = train6s
train6['Time in sec normalised'] = train6s2

train7 = analysis.loc[analysis['Trains'] == "Train 7"]

train7s = []
train7s2 = []
for i in train7['Time']:
    j = get_sec(i)
    train7s.append(j-21600)
    train7s2.append(j-21600-2160)
train7['Time in sec'] = train7s
train7['Time in sec normalised'] = train7s2

train8 = analysis.loc[analysis['Trains'] == "Train 8"]

train8s = []
train8s2 = []
for i in train8['Time']:
    j = get_sec(i)
    train8s.append(j-21600)
    train8s2.append(j-21600-2520)
train8['Time in sec'] = train8s
train8['Time in sec normalised'] = train8s2

train9 = analysis.loc[analysis['Trains'] == "Train 9"]

train9s = []
train9s2 = []

for i in train9['Time']:
    j = get_sec(i)
    train9s.append(j-21600)
    train9s2.append(j-21600-2880)
train9['Time in sec'] = train9s
train9['Time in sec normalised'] = train9s2

train10 = analysis.loc[analysis['Trains'] == "Train 10"]

train10s = []
train10s2 = []
for i in train10['Time']:
    j = get_sec(i)
    train10s.append(j-21600)
    train10s2.append(j-21600-3240)
train10['Time in sec'] = train10s
train10['Time in sec normalised'] = train10s2

line1 = plt.plot(train1['Time in sec'],train1['location'], label = "Train 1")
line2 = plt.plot(train2['Time in sec'],train2['location'], label = "Train 2")
line3 = plt.plot(train3['Time in sec'],train3['location'], label = "Train 3")
line4 = plt.plot(train4['Time in sec'],train4['location'], label = "Train 4")
line5 = plt.plot(train5['Time in sec'],train5['location'], label = "Train 5")
line6 = plt.plot(train6['Time in sec'],train6['location'], label = "Train 6")
line7 = plt.plot(train7['Time in sec'],train7['location'], label = "Train 7")
line8 = plt.plot(train8['Time in sec'],train8['location'], label = "Train 8")
line9 = plt.plot(train9['Time in sec'],train9['location'], label = "Train 9")
line10 = plt.plot(train10['Time in sec'],train10['location'], label = "Train 10")

plt.xlabel('Time in Seconds')
plt.ylabel('Location')
plt.title('Fig 1: Train time in each location')
plt.legend()
plt.show()

line1 = plt.plot(train1['Time in sec normalised'],train1['location'], label = "Train 1")
line2 = plt.plot(train2['Time in sec normalised'],train2['location'], label = "Train 2")
line3 = plt.plot(train3['Time in sec normalised'],train3['location'], label = "Train 3")
line4 = plt.plot(train4['Time in sec normalised'],train4['location'], label = "Train 4")
line5 = plt.plot(train5['Time in sec normalised'],train5['location'], label = "Train 5")
line6 = plt.plot(train6['Time in sec normalised'],train6['location'], label = "Train 6")
line7 = plt.plot(train7['Time in sec normalised'],train7['location'], label = "Train 7")
line8 = plt.plot(train8['Time in sec normalised'],train8['location'], label = "Train 8")
line9 = plt.plot(train9['Time in sec normalised'],train9['location'], label = "Train 9")
line10 = plt.plot(train10['Time in sec normalised'],train10['location'], label = "Train 10")

plt.xlabel('Time in Seconds ')
plt.ylabel('Location')
plt.title('Fig 2: Train time in each location with same start time')
plt.legend()
plt.show()