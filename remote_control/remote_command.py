


class RemoteCommand():
    def __init__(self, string):
        parts = string.split(':')
        self.type = parts[0]
        self.command = parts[1]
        if self.type in ['control', 'query', 'system']:
            self.command_valid = True
        else:
            self.command_valid = False
        self.result = 'Not yet run'

    def execute(self):
        if self.type == 'control':
            self.result = self.execute_control_command()
        elif self.type == 'query':
            self.result = self.execute_query_command()
        elif self.type == 'system':
            self.result = self.execute_system_command()
        else:
            self.result = f'command type {self.type} not recognized'

    def execute_control_command(self):
        if self.command == 'stop':
            return self.execute_stop_command()
        elif self.command == 'run':
            return self.execute_run_command()
        elif self.command == 'load':
            return self.execute_load_command()
        elif self.command == 'clean':
            return self.execute_clean_command()
        else:
            return f'control command {self.command} not recognized'

    def execute_query_command(self):
        if self.command == 'status':
            return self.execute_status_command()
        else:
            return f'query command {self.command} not recognized'

    def execute_system_command(self):
        
