import random
import simpy #for discrete event simulation purposes
import numpy as np
import pandas as pd
import math
import sys


LOT_SIZE = 25
HOTLOT_LIST = []
LAST_LOTID = 100000
RANDOM_SEED = 42

###random time generator to simulate real RPT in fab

def step1_rpt():
    step1_mu = 4.7154524194965735
    step1_sigma = 0.2708856718489293
    """Return actual processing time for a step 1 part."""
    temp_step1_rpt = random.gauss(step1_mu, step1_sigma)
    return round(temp_step1_rpt,1)

def step2_rpt():
    step2_mu = 12.00000000165694
    step2_sigma = 0.2704629164785816
    """Return actual processing time for a step 2 part."""
    temp_step2_rpt = random.gauss(step2_mu, step2_sigma)
    return round(temp_step2_rpt,1)

def step3_rpt():
    step3_alpha =  47.32123088479795
    step3_beta = 0.10460421057200772
    """Return actual processing time for a step 3 part."""
    temp_step3_rpt = random.gammavariate(step3_alpha, step3_beta)
    while temp_step3_rpt <4.95:
        temp_step3_rpt =random.gammavariate(step3_alpha, step3_beta)
    """Return actual processing time for a step 3 part."""
    return round(temp_step3_rpt,1)

def step4_rpt():
    step4_alpha =  22.9300065782288
    step4_beta = 0.09812469928099771
    """Return actual processing time for a step 4 part."""
    temp_step4_rpt = random.gammavariate(step4_alpha, step4_beta)
    return round(temp_step4_rpt,1)

def step5_rpt():
    step5_mu =  9.961013617537
    step5_sigma = 0.4507512987978413
    """Return actual processing time for a step 5 part."""
    temp_step5_rpt = random.gammavariate(step5_mu, step5_sigma)
    return round(temp_step5_rpt,1)

def amhs_time():
    amhs_alpha = 7
    amhs_beta = 0.6
    temp_amhs_time = random.gammavariate(amhs_alpha, amhs_beta)
    """Return actual processing time for amhs delivery."""
    return round(temp_amhs_time,1)

def SFF():
    pSFF = random.uniform(0, 1)
    return pSFF

# Class which takes the simpy enviroment and the capacity for each step to process each of the lots according to the
# processing time
class Fab(object):
    def __init__(self, env, CAPACITY1, CAPACITY2, CAPACITY3, CAPACITY4, CAPACITY5):
        self.env = env
        self.res_step1_tools =  simpy.PriorityResource(env, capacity = CAPACITY1) 
        self.res_step2_tools =  simpy.PriorityResource(env, capacity = CAPACITY2)
        self.res_step3_tools =  simpy.PriorityResource(env, capacity = CAPACITY3)
        self.res_step4_tools =  simpy.PriorityResource(env, capacity = CAPACITY4)
        self.res_step5_tools =  simpy.PriorityResource(env, capacity = CAPACITY5)

        
    def run_step1(self, lot_id): 
        step_1_done_in = step1_rpt()
        yield self.env.timeout(step_1_done_in * 60 * LOT_SIZE)                            
    def run_step2(self, lot_id):
        step_2_done_in = step2_rpt()
        yield self.env.timeout(step_2_done_in * 60 * LOT_SIZE)
    def run_step3(self, lot_id):
        step_3_done_in = step3_rpt()
        yield self.env.timeout(step_3_done_in * 60 * LOT_SIZE)
    def run_step4(self, lot_id):
        step_4_done_in = step4_rpt()
        yield self.env.timeout(step_4_done_in * 60 * LOT_SIZE)
    def run_step5(self, lot_id):
        step_5_done_in = step5_rpt()
        yield self.env.timeout(step_5_done_in * 60 * LOT_SIZE)
    def amhs_delivery(self, lot_id):
        amhs_done_in = amhs_time()
        yield self.env.timeout(amhs_done_in * 60 * LOT_SIZE)
        
# Function to determine the start step, lot delivery, lot procesinng and resource management
def Lot(env, lotid, fb, start_step, CAPACITY1, CAPACITY2, CAPACITY3, CAPACITY4, CAPACITY5, priority, verbose=False):
    if verbose:
        print('lotid: {} has been queued for step 1 process at {} minute'.format(lotid, env.now/60))
    if start_step <= 1:
        with fb.res_step1_tools.request(priority = priority) as req:
            yield req
            if verbose: 
                print('lotid: {} started step 1 process at {} minute'.format(lotid, env.now/60))
            resource_db.append([1, env.now/60, fb.res_step1_tools.count, len(fb.res_step1_tools.queue), CAPACITY1 - fb.res_step1_tools.count])
            time_in = env.now/60
            yield env.process(fb.amhs_delivery(lotid))
            yield env.process(fb.run_step1(lotid))
            if verbose:
                print('lotid: {} ended step 1 process at {} minute'.format(lotid, env.now/60))
            time_out = env.now/60
            operation_db.append([lotid, 1, time_in, time_out])
            resource_db.append([1, env.now/60, fb.res_step1_tools.count, len(fb.res_step1_tools.queue), CAPACITY1 - fb.res_step1_tools.count])
        
    if start_step <= 2:
        with fb.res_step2_tools.request(priority = priority) as req:
            yield req
            if verbose:
                print('lotid: {} started step 2 process at {} minute'.format(lotid, env.now/60))
            resource_db.append([2, env.now/60, fb.res_step2_tools.count, len(fb.res_step2_tools.queue), CAPACITY2 - fb.res_step2_tools.count])
            time_in = env.now/60
            try:
                if priority == 1:
                    qtime_db.append([lotid, 'HOT LOT', '1-2', time_in - time_out, STEP_1_2_QTIME_SPEC_HRS * 60])
                else:
                    qtime_db.append([lotid, 'NORMAL LOT', '1-2', time_in - time_out, STEP_1_2_QTIME_SPEC_HRS * 60])
            except:
                if priority == 1:
                    qtime_db.append([lotid, 'HOT LOT', '1-2', 0, STEP_1_2_QTIME_SPEC_HRS * 60])
                else:
                    qtime_db.append([lotid, 'NORMAL LOT', '1-2', 0, STEP_1_2_QTIME_SPEC_HRS * 60])
            yield env.process(fb.amhs_delivery(lotid))
            yield env.process(fb.run_step2(lotid))
            if verbose:
                print('lotid: {} ended step 2 process at {} minute'.format(lotid, env.now/60))
            time_out = env.now/60
            operation_db.append([lotid, 2, time_in, time_out])
            resource_db.append([2, env.now/60, fb.res_step2_tools.count, len(fb.res_step2_tools.queue), CAPACITY2 - fb.res_step2_tools.count])
    
    if start_step <= 3:
        with fb.res_step3_tools.request(priority = priority) as req:
            yield req
            if verbose:
                print('lotid: {} started step 3 process at {} minute'.format(lotid, env.now/60))
            resource_db.append([3, env.now/60, fb.res_step3_tools.count, len(fb.res_step3_tools.queue), CAPACITY3 - fb.res_step3_tools.count])
            time_in = env.now/60
            try:
                if priority == 1:
                    qtime_db.append([lotid, 'HOT LOT', '2-3', time_in - time_out, STEP_2_3_QTIME_SPEC_HRS * 60])
                else:
                    qtime_db.append([lotid, 'NORMAL LOT', '2-3', time_in - time_out, STEP_2_3_QTIME_SPEC_HRS * 60])
            except:
                if priority == 1:
                    qtime_db.append([lotid, 'HOT LOT', '2-3', 0, STEP_2_3_QTIME_SPEC_HRS * 60])
                else:
                    qtime_db.append([lotid, 'NORMAL LOT', '2-3', 0, STEP_2_3_QTIME_SPEC_HRS * 60])
            yield env.process(fb.amhs_delivery(lotid))
            yield env.process(fb.run_step3(lotid))
            if verbose:
                print('lotid: {} ended step 3 process at {} minute'.format(lotid, env.now/60))
            time_out = env.now/60
            operation_db.append([lotid, 3, time_in, time_out])
            resource_db.append([3, env.now/60, fb.res_step3_tools.count, len(fb.res_step3_tools.queue), CAPACITY3 - fb.res_step3_tools.count])
    
    if start_step <= 4:    
        with fb.res_step4_tools.request(priority = priority) as req:
            yield req
            if verbose:
                print('lotid: {} started step 4 process at {} minute'.format(lotid, env.now/60))
            resource_db.append([4, env.now/60, fb.res_step4_tools.count, len(fb.res_step4_tools.queue), CAPACITY4 - fb.res_step4_tools.count])
            time_in = env.now/60
            try:
                if priority == 1:
                    qtime_db.append([lotid, 'HOT LOT', '3-4', time_in - time_out, STEP_3_4_QTIME_SPEC_HRS * 60])
                else:
                    qtime_db.append([lotid, 'NORMAL LOT', '3-4', time_in - time_out, STEP_3_4_QTIME_SPEC_HRS * 60])
            except:
                if priority == 1:
                    qtime_db.append([lotid, 'HOT LOT', '3-4', 0, STEP_3_4_QTIME_SPEC_HRS * 60])
                else:
                    qtime_db.append([lotid, 'NORMAL LOT', '3-4', 0, STEP_3_4_QTIME_SPEC_HRS * 60])
            yield env.process(fb.amhs_delivery(lotid))
            yield env.process(fb.run_step4(lotid))
            if verbose:
                print('lotid: {} ended step 4 process at {} minute'.format(lotid, env.now/60))
            time_out = env.now/60
            operation_db.append([lotid, 4, time_in, time_out])
            resource_db.append([4, env.now/60, fb.res_step4_tools.count, len(fb.res_step4_tools.queue), CAPACITY4 - fb.res_step4_tools.count])
    
    if start_step <= 5:
        with fb.res_step5_tools.request(priority = priority) as req:
            yield req
            if verbose:
                print('lotid: {} started step 5 process at {} minute'.format(lotid, env.now/60))
            resource_db.append([5, env.now/60, fb.res_step5_tools.count, len(fb.res_step5_tools.queue), CAPACITY5 - fb.res_step5_tools.count])
            time_in = env.now/60
            try:
                if priority == 1:
                    qtime_db.append([lotid, 'HOT LOT', '4-5', time_in - time_out, STEP_4_5_QTIME_SPEC_HRS * 60])
                else:
                    qtime_db.append([lotid, 'NORMAL LOT', '4-5', time_in - time_out, STEP_4_5_QTIME_SPEC_HRS * 60])
            except:
                if priority == 1:
                    qtime_db.append([lotid, 'HOT LOT', '4-5', 0, STEP_4_5_QTIME_SPEC_HRS * 60])
                else:
                    qtime_db.append([lotid, 'NORMAL LOT', '4-5', 0, STEP_4_5_QTIME_SPEC_HRS * 60])
            yield env.process(fb.amhs_delivery(lotid))
            yield env.process(fb.run_step5(lotid))
            if verbose:
                print('lotid: {} ended step 5 process at {} minute'.format(lotid, env.now/60))
            time_out = env.now/60
            operation_db.append([lotid, 5, time_in, time_out])
            resource_db.append([5, env.now/60, fb.res_step5_tools.count, len(fb.res_step5_tools.queue), CAPACITY5 - fb.res_step5_tools.count])

# Function to setup initial lots and the subsequent lots during simulation
def Setup(env, CAPACITY1, CAPACITY2, CAPACITY3, CAPACITY4, CAPACITY5):
    fab = Fab(env, CAPACITY1, CAPACITY2, CAPACITY3, CAPACITY4, CAPACITY5)
 
    # Create initial lots
    global LAST_LOTID
    for i in range(STEP_1_INITIAL_LOTS):
        env.process(Lot(env, LAST_LOTID, fab, 1, CAPACITY1, CAPACITY2, CAPACITY3, CAPACITY4, CAPACITY5, 2))
        LAST_LOTID += 1
    
    for i in range(STEP_2_INITIAL_LOTS):
        env.process(Lot(env, LAST_LOTID, fab, 2, CAPACITY1, CAPACITY2, CAPACITY3, CAPACITY4, CAPACITY5, 2))
        LAST_LOTID += 1
        
    for i in range(STEP_3_INITIAL_LOTS):
        env.process(Lot(env, LAST_LOTID, fab, 3, CAPACITY1, CAPACITY2, CAPACITY3, CAPACITY4, CAPACITY5, 2))
        LAST_LOTID += 1
        
    for i in range(STEP_4_INITIAL_LOTS):
        env.process(Lot(env, LAST_LOTID, fab, 4, CAPACITY1, CAPACITY2, CAPACITY3, CAPACITY4, CAPACITY5, 2))
        LAST_LOTID += 1
        
    for i in range(STEP_5_INITIAL_LOTS):
        env.process(Lot(env, LAST_LOTID, fab, 5, CAPACITY1, CAPACITY2, CAPACITY3, CAPACITY4, CAPACITY5, 2))
        LAST_LOTID += 1
        
    # Create more lots while the simulation is running
    while True:
        pSFF = SFF()
        if pSFF < 0.98:
            yield env.timeout(random.randint(30 * 60, 90 * 60))
            env.process(Lot(env, LAST_LOTID, fab, 1, CAPACITY1, CAPACITY2, CAPACITY3, CAPACITY4, CAPACITY5,2))
            LAST_LOTID += 1
            pSFF = 0
        else:
            yield env.timeout(random.randint(30 * 60, 90 * 60))
            env.process(Lot(env, LAST_LOTID, fab, 1, CAPACITY1, CAPACITY2, CAPACITY3, CAPACITY4, CAPACITY5,1))
            HOTLOT_LIST.append(LAST_LOTID)
            LAST_LOTID += 1
            pSFF = 0
    


# In[10]:

#function to run the entire simulation for each of the gating ratio combination
def run_simulation():
    
    global progress_pct, operation_db, qtime_db, resource_db, hotlot_db, LAST_LOTID
    


    GATING_RATIO_1 = np.arange(0, 1.1, 0.2) # increment of 20%
    GATING_RATIO_2 = np.arange(0, 1.1, 0.2)
    GATING_RATIO_3 = np.arange(0, 1.1, 0.2)
    GATING_RATIO_4 = np.arange(0, 1.1, 0.2)
    GATING_RATIO_5 = np.arange(0, 1.1, 0.2)

    
    progress_pct = 0
    counter = 0
    database_gr = []
    database_qt = []
    database_res = []
    database_hot_qt = []
    
    for i1 in GATING_RATIO_1:
        for i2 in GATING_RATIO_2:
            for i3 in GATING_RATIO_3:
                for i4 in GATING_RATIO_4:
                    for i5 in GATING_RATIO_5:
                        counter += 1
                        progress_pct = counter * 100 / (len(GATING_RATIO_1) * len(GATING_RATIO_2) * len(GATING_RATIO_3) * len(GATING_RATIO_4) * len(GATING_RATIO_5))
                        operation_db = []
                        qtime_db = []
                        resource_db = []
                        hotlot_db =[]
                        HOTLOT_LIST = []
                        
                        try:
                            CAPACITY1 = math.floor(STEP_1_TOOLS * i1)
                            CAPACITY2 = math.floor(STEP_2_TOOLS * i2)
                            CAPACITY3 = math.floor(STEP_3_TOOLS * i3)
                            CAPACITY4 = math.floor(STEP_4_TOOLS * i4)
                            CAPACITY5 = math.floor(STEP_5_TOOLS * i5)
                            LAST_LOTID = 100000
                            env = simpy.Environment()
                            env.process(Setup(env, CAPACITY1, CAPACITY2, CAPACITY3, CAPACITY4, CAPACITY5))
                            env.run(until=60 * 60 * 24 * SIMULATION_DAYS) 
    
                            operation = pd.DataFrame(operation_db, columns=['lotid', 'step', 'track in time', 'track out time'])
                            qtime_db = pd.DataFrame(qtime_db, columns=['lotid', 'priority', 'step', 'Q-time actual', 'Q-time spec'])
                            qtime_db['Q-time breach flag'] = np.where(qtime_db['Q-time actual'] > qtime_db['Q-time spec'], 1, 0)
                            qtime_db['Q-time breach time'] = np.where(qtime_db['Q-time breach flag'] == True, qtime_db['Q-time actual'] - qtime_db['Q-time spec'], 0)
                            qtime_db['Gating Ratio 1'] = i1
                            qtime_db['Gating Ratio 2'] = i2
                            qtime_db['Gating Ratio 3'] = i3
                            qtime_db['Gating Ratio 4'] = i4
                            qtime_db['Gating Ratio 5'] = i5
                            t1 = [str(len(operation[operation.step == 5].lotid.unique()))]
                            t2 = qtime_db.groupby('step').sum()[['Q-time breach flag']].values.reshape(4).tolist()
                            t3 = [i1, i2, i3, i4, i5, *t1, *t2]
                            database_gr.append(t3)
    
                            hotlot_db = pd.DataFrame(hotlot_db, columns=['lotid', 'step', 'Q-time actual', 'Q-time spec'])
                            hotlot_db['Q-time breach flag'] = np.where(hotlot_db['Q-time actual'] > hotlot_db['Q-time spec'], 1, 0)
                            hotlot_db['Q-time breach time'] = np.where(hotlot_db['Q-time breach flag'] == True, hotlot_db['Q-time actual'] - hotlot_db['Q-time spec'], 0)
                            hotlot_db['Gating Ratio 1'] = i1
                            hotlot_db['Gating Ratio 2'] = i2
                            hotlot_db['Gating Ratio 3'] = i3
                            hotlot_db['Gating Ratio 4'] = i4
                            hotlot_db['Gating Ratio 5'] = i5
    
                            for _ in qtime_db.values.tolist():
                                database_qt.append(_)
    
                            for _ in hotlot_db.values.tolist():
                                database_hot_qt.append(_)
    
                            resource_db = pd.DataFrame(resource_db, columns=['step', 'time', 'mc_in_use', 'in_queue', 'remaining_mc'])
                            resource_db = resource_db.groupby(['step','time']).tail(1)
                            resource_db['Gating Ratio 1'] = i1
                            resource_db['Gating Ratio 2'] = i2
                            resource_db['Gating Ratio 3'] = i3
                            resource_db['Gating Ratio 4'] = i4
                            resource_db['Gating Ratio 5'] = i5
    
    
                            for _ in resource_db.values.tolist():
                                database_res.append(_)
    
                            del qtime_db, hotlot_db, operation, t1, t2, t3
                        
                        except:
                            pass
                        
                pd.DataFrame([progress_pct]).to_csv('progress.csv')

    database_gr = pd.DataFrame(database_gr, columns = ['GR1', 'GR2', 'GR3', 'GR4', 'GR5', 'TOTAL_LOTS_MOVED', 'S1_2_QTIME_BREACHED', 'S2_3_QTIME_BREACHED', 'S3_4_QTIME_BREACHED', 'S4_5_QTIME_BREACHED'])
    database_gr['CR'] = (database_gr.GR1 * database_gr.GR2 * database_gr.GR3 * database_gr.GR4 * database_gr.GR5).astype(float).round(3)
    
    database_qt = pd.DataFrame(database_qt, columns = ['lotid', 'priority', 'step', 'Q-time actual', 'Q-time spec', 'Q-time breach flag',
                                                       'Q-time breach time', 'Gating Ratio 1', 'Gating Ratio 2', 'Gating Ratio 3',
                                                       'Gating Ratio 4', 'Gating Ratio 5'])
    
    database_res = pd.DataFrame(database_res, columns = ['step', 'time', 'mc_in_use', 'in_queue', 'remaining_mc',
                                                         'Gating Ratio 1', 'Gating Ratio 2', 'Gating Ratio 3',
                                                       'Gating Ratio 4', 'Gating Ratio 5'])
    
  
    return database_gr.sort_values('CR'), database_qt, database_res, database_hot_qt
                        
# Main.py pass the argument here to run the simulation
if __name__ == "__main__":
    STEP_1_TOOLS = int(sys.argv[1])
    STEP_2_TOOLS = int(sys.argv[2])
    STEP_3_TOOLS = int(sys.argv[3])
    STEP_4_TOOLS = int(sys.argv[4])
    STEP_5_TOOLS = int(sys.argv[5])
    STEP_1_2_QTIME_SPEC_HRS = int(sys.argv[6])
    STEP_2_3_QTIME_SPEC_HRS = int(sys.argv[7])
    STEP_3_4_QTIME_SPEC_HRS = int(sys.argv[8])
    STEP_4_5_QTIME_SPEC_HRS = int(sys.argv[9])
    STEP_1_INITIAL_LOTS = int(sys.argv[10])
    STEP_2_INITIAL_LOTS = int(sys.argv[11])
    STEP_3_INITIAL_LOTS = int(sys.argv[12])
    STEP_4_INITIAL_LOTS = int(sys.argv[13])
    STEP_5_INITIAL_LOTS = int(sys.argv[14])
    SIMULATION_DAYS = int(sys.argv[15])

    
database_gr, database_qt, database_res, database_hot_qt= run_simulation()

database_gr.to_csv('database_gr.csv')
database_qt.to_csv('database_qt.csv')
database_res.to_csv('database_res.csv')







































































































