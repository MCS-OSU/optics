from core.utils     import optics_info

# scene status
IN_PROGRESS                     = 'IN_PROGRESS'
NOT_ATTEMPTED                   = 'ready'
IN_PROGRESS_SCENE_STARTED       = IN_PROGRESS + '_SCENE_STARTED'
IN_PROGRESS_CONTROLLER_LAUNCHED = IN_PROGRESS + '_CONTROLLER_LAUNCHED'
IN_PROGRESS_CONTROLLER_UP       = IN_PROGRESS + '_CONTROLLER_UP'
IN_PROGRESS_SCENE_RUNNING       = IN_PROGRESS + '_SCENE_RUNNING'
IN_PROGRESS_SCENE_ASSIGNED      = IN_PROGRESS + '_SCENE_ASSIGNED'
COMPLETED                       = 'COMPLETED'

# directives
RETRY_OTHER_TRUN_SESSION        = 'RETRY_OTHER_TRUN_SESSION'
RETRY_THIS_TRUN_SESSION         = 'RETRY_THIS_TRUN_SESSION'
RETRY_AFTER_PAUSE               = 'RETRY_AFTER_PAUSE'
SCENE_FATAL                     = 'SCENE_FATAL'
SESSION_FATAL                   = 'SESSION_FATAL'

CONTROLLER_FAILED_TO_LAUNCH     = 'CONTROLLER_FAILED_TO_LAUNCH__' + RETRY_OTHER_TRUN_SESSION
INITIALIZATION_ERROR            = 'INITIALIZATION_ERROR__'        + RETRY_OTHER_TRUN_SESSION
RUNTIME_ERROR                   = 'RUNTIME_ERROR__'               + RETRY_OTHER_TRUN_SESSION

FAILED_TIMEOUT                  = 'FAILED_TIMEOUT__'              + RETRY_THIS_TRUN_SESSION

FAILED_EXCEPTION                = 'EXCEPTION__'                   + SCENE_FATAL
UNKNOWN_SCENE_TYPE              = 'UNKNOWN_SCENE_TYPE__'          + SCENE_FATAL

FAILED_GPU_MEM                  = 'FAILED_GPU_MEM'
FAILED_GPU_MEM_FATAL            = FAILED_GPU_MEM + '__'           + SESSION_FATAL
FAILED_GPU_MEM_RETRY            = FAILED_GPU_MEM + '__'           + RETRY_AFTER_PAUSE 
ENVIRONMENT_BAD                 = 'ENVIRONMENT_BAD__'             + SESSION_FATAL


class OpticsRunState():
    def __init__(self, scene_path):
        self.scene_path = scene_path
        self.is_systest = False
        self.test_register = None
        self.state = NOT_ATTEMPTED
        self.retry_pause_time = 120

    def set_test_register(self, test_register):
        self.test_register = test_register
        self.is_systest = True
    
    def is_controller_timed_out(self):
        if self.state == FAILED_TIMEOUT:
            return True
        return False

    def is_session_pointless(self):
        if SESSION_FATAL in self.state:
            return True
        return False

    def should_retry_after_pause(self):
        if RETRY_AFTER_PAUSE in self.state:
            return True
        return False

    def needs_run_attempt(self):
        if self.state == NOT_ATTEMPTED:
            return True
        if RETRY_THIS_TRUN_SESSION in self.state:
            return True
        return False 

    def  is_optics_run(self):
        return self.is_systest

    def starting_scene(self):
        self.state = IN_PROGRESS_SCENE_STARTED
        if self.is_systest:
            self.test_register.note_scene_state(self.scene_path, self.state)
   
    def starting_controller(self):
        self.state = IN_PROGRESS_CONTROLLER_LAUNCHED
        if self.is_systest:
            self.test_register.note_scene_state(self.scene_path, self.state)
    
    def controller_up(self):
        self.state = IN_PROGRESS_CONTROLLER_UP
        if self.is_systest:
            self.test_register.note_scene_state(self.scene_path, self.state)

    def scene_running(self):
        self.state = IN_PROGRESS_SCENE_RUNNING
        if self.is_systest:
            self.test_register.note_scene_state(self.scene_path, self.state)
        
    def scene_completed(self):
        self.state = COMPLETED
        if self.is_systest:
            self.test_register.note_scene_state(self.scene_path, self.state)

    def bad_environment(self):
        self.state = ENVIRONMENT_BAD
        if self.is_systest:
            self.test_register.note_scene_state(self.scene_path, self.state)


    # EXCEPTIONS AND ERRORS:
    def initialization_error(self):
        self.state = INITIALIZATION_ERROR
        if self.is_systest:
            self.test_register.note_scene_state(self.scene_path, self.state)

    def error(self):
        self.state = FAILED_EXCEPTION
        if self.is_systest:
            self.test_register.note_scene_state(self.scene_path, self.state)
    

    def runtime_error(self):
        self.state = RUNTIME_ERROR
        if self.is_systest:
            self.test_register.note_scene_state(self.scene_path, self.state)

    def cuda_memory_error(self):
        self.state = FAILED_GPU_MEM_RETRY
        if self.is_systest:
            self.test_register.note_scene_state(self.scene_path, self.state)
    
    def controller_timed_out(self):
        self.state = FAILED_TIMEOUT
        if self.is_systest:
            self.test_register.note_scene_state(self.scene_path, self.state)

    def controller_failed_to_launch(self):
        self.state = CONTROLLER_FAILED_TO_LAUNCH
        if self.is_systest:
            self.test_register.note_scene_state(self.scene_path, self.state)

    def convert_exception_to_run_state(self, err, context):
        err_string = str(err)
        if 'CUDA' in err_string and 'out of memory' in err_string:
            self.cuda_memory_error()
        elif 'Time out' in err_string:
            self.controller_timed_out()   
        elif self.state == IN_PROGRESS_CONTROLLER_LAUNCHED:
            self.controller_failed_to_launch()
        elif err is RuntimeError:
            self.runtime_error()
        else:
            self.error()

    # SCENE RELATED

    def unknown_scene_type(self):
        self.state = FAILED_EXCEPTION
        if self.is_systest:
            self.test_register.note_scene_state(self.scene_path, self.state)

    def should_tman_assign_scene_in_state(self, run_state):
        #optics_info(f'{run_state} for {self.scene_path}')
        if run_state == NOT_ATTEMPTED:
            return True
        elif IN_PROGRESS in run_state:
            return False
        elif run_state == COMPLETED:
            return False
        elif RETRY_AFTER_PAUSE in run_state:
            return True 
        elif RETRY_OTHER_TRUN_SESSION in run_state:
            return True
        elif RETRY_THIS_TRUN_SESSION in run_state:   # that session wil be trying again on its own
            return False
        elif SCENE_FATAL in run_state:              #  no reason to think the scene will work on second try
            return False
        elif SESSION_FATAL in run_state:            # the trun session had to abort for some reason, try this scene elsewhere
            return True
        else:
            print(f'unknown state: {run_state}')
            return False


    def show_runs_summary(self, scene_state_histories):
        end_state_counts = {}
        end_state_counts[NOT_ATTEMPTED] = 0
        end_state_counts[IN_PROGRESS_SCENE_ASSIGNED] = 0
        end_state_counts[IN_PROGRESS_SCENE_RUNNING] = 0
        end_state_counts[IN_PROGRESS_SCENE_STARTED] = 0
        end_state_counts[IN_PROGRESS_CONTROLLER_LAUNCHED] = 0
        end_state_counts[IN_PROGRESS_CONTROLLER_UP] = 0
        end_state_counts[COMPLETED] = 0
        end_state_counts[CONTROLLER_FAILED_TO_LAUNCH] = 0
        end_state_counts[INITIALIZATION_ERROR] = 0
        end_state_counts[RUNTIME_ERROR] = 0
        end_state_counts[FAILED_TIMEOUT] = 0
        end_state_counts[FAILED_EXCEPTION] = 0
        end_state_counts[UNKNOWN_SCENE_TYPE] = 0
        end_state_counts[FAILED_GPU_MEM_FATAL] = 0
        end_state_counts[FAILED_GPU_MEM_RETRY] = 0
        end_state_counts[ENVIRONMENT_BAD] = 0
        for ssh in scene_state_histories:
            end_state_counts[ssh.end_state] += 1
        
        for end_state in end_state_counts:
            end_state_sans_directive = end_state.split('__')[0]
            print(f'{end_state_sans_directive.rjust(35)}: {end_state_counts[end_state]}')


    def get_scene_types_from_completed_scenes(self, scene_state_histories):
        scene_types = set()
        for ssh in scene_state_histories:
            if ssh.is_completed():
                scene_types.add(ssh.scene_type)
        return scene_types

    def get_completed_state_histories_for_scene_type(self, scene_state_histories, scene_type):
        completed_state_histories = []
        for ssh in scene_state_histories:
            if ssh.is_completed() and ssh.scene_type == scene_type:
                completed_state_histories.append(ssh)
        return completed_state_histories

    def show_scene_timings(self, scene_state_histories):
        scene_types = self.get_scene_types_from_completed_scenes(scene_state_histories)
        for type in scene_types:
            sshs = self.get_completed_state_histories_for_scene_type(scene_state_histories, type)
            print(f'{len(sshs)} {type} scene timings:')
            self.show_average_successful_run_time(sshs)
            #self.show_average_total_time(sshs)
       
    
    def show_average_successful_run_time(self, scene_state_histories):
        total_time = 0
        complete_count = 0
        for ssh in scene_state_histories:
            if ssh.is_completed():
                complete_count +=1
                total_time += ssh.completion_duration
        average = int(total_time / complete_count)
        mins    = int(average / 60)
        sec     = int(average % 60)
        print(f'    average succesful run time: {mins} mins {sec} sec')

    def show_average_total_time(self, scene_state_histories):
        total_time = 0
        complete_count = 0
        for ssh in scene_state_histories:
            if ssh.is_completed():
                complete_count +=1
                total_time += ssh.total_duration
        print(f'    average run time including retries: {int(total_time / complete_count)}')

    def show_gpu_mem_fail_retry_count(self, scene_state_histories):
        retry_count = 0
        for ssh in scene_state_histories:
            retry_count += ssh.get_gpu_mem_fail_count()
        print(f'\ngpu mem fatal pause count: {retry_count}')