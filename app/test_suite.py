import time, sys, json

import inspect
import tests

all_functions = inspect.getmembers(tests, inspect.isfunction)


def generate_dynamic_test_dict():
    # import test
    # use the tests to make a dict and write it to file
    status_dict = {'parents':[]}
    
    for (fn_name, fn_method) in all_functions:
        (current_parent, current_child) = fn_method(None, None, dynamic_gen = True)
         
        if current_parent['handle'] in [x['handle'] for x in status_dict['parents']]:
            # the parent exists
            for parent in status_dict['parents']:
                if parent['handle'] == current_parent['handle']:
                    existing_children = parent['children']
                    
                    if current_child['handle'] not in [c['handle'] for c in existing_children]: #check the children
                        #add the child
                        parent['children'].append(current_child)
                    else:
                        print 'ERROR: Duplicate found for '+current_parent['handle']+' : '+current_child['handle']+' pair.'
        
        else: #the parent is not yet in status_dict
            current_parent['children'] = [current_child] #add the child to the parent
            status_dict['parents'].append(current_parent) #put the lot in the dict
            
    print status_dict       
                
    with open('status.txt', "w") as f:
        f.write(json.dumps(status_dict))
        f.flush()
    f.close()

class child_base_test:
    def __init__(self, parent = '', child = '', test_fn = None):
        self.level = ''
        self.timestamp = -1
        self.console = 0
        self.text = ''
        self.parent = parent
        self.child = child
        self.handle = ''
        self.display_name = ''
        self.test_fn = test_fn
    
    def run_test(self, mpstate, m):
        test_result = self.test_fn(mpstate, m)
        
        if test_result is not None:
            (self.parent, self.child, self.result_level, self.result_text, self.result_console, self.result_time) = test_result
            return self.generate_dict()
        
    def generate_dict(self):
        result_dict = {}
        result_dict[self.parent] = {}
        result_dict[self.parent]['level'] = ''
        result_dict[self.parent]['children'] = {}
        result_dict[self.parent]['children'][self.child] = {'level':self.result_level, 'timestamp':self.result_time, 'text':self.result_text, 'console':self.result_console}
        return result_dict


class tests:
    def __init__(self, mpstate):
        self.status_update_dict = {}
        self.status_dict = {}
        self.mpstate = mpstate
        self.level_enum = {'danger':3, 'warning':2, 'okay':1, '':-1}
        self.rev_level_enum = dict((v,k) for k,v in self.level_enum.iteritems())
        
        self.test_list = [child_base_test(test_fn = fn_method) for (fn_name, fn_method) in all_functions]
        self.bad_status_report_interval = 5
    def run_tests(self, m):
        self.status_update_dict = {}
        # run all of the tests
        for test in self.test_list:
            self.last_test_result = test.run_test(self.mpstate, m)
            if self.last_test_result is not None:
                self.update_status_dict() # needs to be ran after every test
                
        if self.status_update_dict != {}:
            # we need to keep track of the changes and make sure the user is alerted to
            # changes in the UAV state...
            self.update_persistent_dict()
            return self.status_update_dict
    
    def update_persistent_dict(self):
        for parent in self.status_update_dict.keys():
            if parent not in self.status_dict: #if the parent does not exist then add it
                self.status_dict[parent] = self.status_update_dict[parent]
            
            for child in self.status_update_dict[parent]['children'].keys():
                if child not in self.status_dict[parent]['children']: #if the child does not exist then add it
                    self.status_dict[parent]['children'][child] = self.status_update_dict[parent]['children'][child]
                    self.status_dict[parent]['children'][child]['console_time'] = time.time() # also add a console start time
                    if self.status_dict[parent]['children'][child]['level'] in ['warning', 'danger']:
                        # if the child is new and is reporting a bad level then display it in the console
                        self.status_dict[parent]['children'][child]['console'] = 1
                        self.status_dict[parent]['children'][child]['console_time'] = time.time() # add a timestamp for the last console report
                        self.status_update_dict[parent]['children'][child]['console'] = 1
                else: # the child already exists
                    # check to see if the level has changed
                    if self.status_dict[parent]['children'][child]['level'] != self.status_update_dict[parent]['children'][child]['level']:
                        # it has changed, so make sure it is reported...
                        self.status_dict[parent]['children'][child]['console'] = 1
                        self.status_dict[parent]['children'][child]['console_time'] = time.time() # add a timestamp for the last console report
                        self.status_update_dict[parent]['children'][child]['console'] = 1
                        
                    if 'console_time' not in self.status_dict[parent]['children'][child].keys():
                        # the child might have been added with the parent
                        self.status_dict[parent]['children'][child]['console_time'] = time.time() # also add a console start time
                        if self.status_dict[parent]['children'][child]['level'] in ['warning', 'danger']:
                            # if the child is reporting a bad level then display it in the console
                            self.status_dict[parent]['children'][child]['console'] = 1
                            self.status_dict[parent]['children'][child]['console_time'] = time.time() # add a timestamp for the last console report
                            self.status_update_dict[parent]['children'][child]['console'] = 1
                        
                    # write the new child data
                    for key in self.status_update_dict[parent]['children'][child].keys():
                        self.status_dict[parent]['children'][child][key] = self.status_update_dict[parent]['children'][child][key]
            
            for child in self.status_update_dict[parent]['children'].keys():
                if self.status_dict[parent]['children'][child]['level'] in ['warning', 'danger']:
                    if self.status_dict[parent]['children'][child]['console_time'] + self.bad_status_report_interval <= time.time():
                        self.status_dict[parent]['children'][child]['console'] = 1
                        self.status_dict[parent]['children'][child]['console_time'] = time.time() # add a timestamp for the last console report
                        self.status_update_dict[parent]['children'][child]['console'] = 1

    
    def update_status_dict(self):
        for parent in self.last_test_result.keys():
            if parent not in self.status_update_dict:
                self.status_update_dict[parent] = self.last_test_result[parent]
                
            else: # the parent key already exists...
#                 # check to see the parent warning level has not increased
#                 if self.level_enum[self.status_update_dict[parent]['level']] < self.level_enum[self.last_test_result[parent]['level']]:
#                     # the new data is a higher warning level. Update it.
#                     self.status_update_dict[parent]['level'] = self.last_test_result[parent]['level']
                    
                # add the child to the parent dict
                for child in self.last_test_result[parent]['children'].keys():
                    self.status_update_dict[parent]['children'][child] = self.last_test_result[parent]['children'][child]
            
            
            # check the parent level against the existing children
            highest_level = -1
            if parent in self.status_update_dict.keys():
                # the parent exists in the persistent dict
                for child in self.status_update_dict[parent]['children'].keys():
                    child_level = self.level_enum[self.status_dict[parent]['children'][child]['level']]
                    if child_level > highest_level:
                        highest_level = child_level
            
            for child in self.last_test_result[parent]['children'].keys():
                child_level = self.level_enum[self.last_test_result[parent]['children'][child]['level']]
                if child_level > highest_level:
                    highest_level = child_level
                
            self.status_update_dict[parent]['level'] = self.rev_level_enum[highest_level]
            
            
                

if __name__ == '__main__':
    generate_dynamic_test_dict()
        
        