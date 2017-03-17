import time

gnc_parent = {'handle':'gnc', 'display':'Guidance<br/>&<br/>Control'}

def gps_test(mpstate, m, dynamic_gen = False):
    parent = gnc_parent
    child = {'handle':'gps', 'display':'GPS'}
    if dynamic_gen:
        return (parent,child)
    
    # here we run the test
    # we can use this code to access the latest variable that has been received in a msg type: self.mpstate.status.msgs['LOCAL_POSITION_NED'].x
    # we can use this code to check params: self.mpstate.mav_param['GLIDE_SLOPE_MIN']
    # self.all_msg_types = self.mpstate.status.msgs.keys()
    alert = 0
    
    type = m.get_type()
    if type == 'GPS_RAW_INT':
        if m.fix_type >=3 and m.satellites_visible >= 6:
            level = 'okay'
            text = 'good gps fix and sat count ('+str(m.fix_type)+'D & '+str(m.satellites_visible)+ ' sats)'
        elif m.fix_type >=3 and m.satellites_visible <= 6:
            level = 'warning'
            text = 'good gps fix with low sat count ('+str(m.fix_type)+'D & '+str(m.satellites_visible)+ ' sats)'
        else:
            level = 'danger'
            text = 'poor gps fix ('+str(m.fix_type)+'D & '+str(m.satellites_visible)+ ' sats)'
            
            
        return (parent['handle'], child['handle'], level, text, alert, m._timestamp)

def ekf_test(mpstate, m, dynamic_gen = False):
    parent = gnc_parent
    child = {'handle':'ekf', 'display':'EKF'}
    if dynamic_gen:
        return (parent,child)
    
    alert = 0
    
    type = m.get_type()
    if type == 'SYS_STATUS':

        vars = {'velocity_variance':0,
                'pos_horiz_variance':0,
                'pos_vert_variance':0,
                'compass_variance':0,
                'terrain_alt_variance':0}
        for key in vars.keys():
            vars[key] = getattr(m, key, 0)
        highest = max(vars.values())
        if highest >= 1.0:
            level = 'danger'
            text = 'critical EKF variance' 
        elif highest >= 0.5:
            level = 'warning'
            text = 'high EKF variance' 
        else:
            level = 'okay'
            text = 'EKF is stable' 
        
        return (parent['handle'], child['handle'], level, text, alert, m._timestamp)
    

def batt_test(mpstate, m, dynamic_gen = False):
    parent = {'handle':'power', 'display':'Power'}
    child = {'handle':'batt', 'display':'BATT'}
    if dynamic_gen:
        return (parent,child)
    
    cell_count = 6
    alert = 0
    
    type = m.get_type()
    if type == 'SYS_STATUS':
        #voltage_battery : 12587, current_battery : 0
        reported_voltage = m.voltage_battery/1000.0
        
        if reported_voltage >= 3.7*cell_count:
            level = 'okay'
            text = 'voltage good ('+str(reported_voltage)+'V)'
        elif reported_voltage >= 3.5*cell_count:
            level = 'warning'
            text = 'voltage low ('+str(reported_voltage)+'V)'
        else:
            level = 'danger'
            text = 'voltage critical ('+str(reported_voltage)+'V)'
        
        return (parent['handle'], child['handle'], level, text, alert, m._timestamp)
            
    
    
    