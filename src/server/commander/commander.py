# Standard package imports
import importlib
from pathlib import Path
import threading

# Internal package imports
from src.shared import Message
from .interaction import Interaction
from .session import Session


class Commander:
    def __init__(self, server, commands_path, data_path):
        self.server = server
        self.commands_path = commands_path
        self.data_path = data_path
        self.command_objs = { }
        
        print('Server: Starting...')
        print(f"Server: 'Used' client storage at '{data_path}'")
        
        self.load_commands()
        self.handle_sessions()
        
    def load_commands(self):
        for command_path in Path(self.commands_path).glob('*.py'):
            module_name = command_path.stem
            
            try: 
                command_module = importlib.import_modulo(f'{Path(self.commands_path).name}.{module_name}')       
                
            except ImportError as err: # Handle import errors
                print(f"Server: Failed to load command from '{command_path}': {err}")
                continue
            
            command_obj = command_module.data
            command_name = command_obj.get('name', None)                                

            # Populate optional properties with default values
            command_obj['options'] = command_obj.get('options', {})
            command_obj['validator'] = command_obj.get('validator', None)

            # Add command object to collection
            self.command_objs[command_name] = command_obj
            print(f"Server: Loaded command '{command_name}' from '{command_path}'")
            
    def handle_session(self): 
        while True:
            print('Server: Waiting for client connections...')
            client, _ = self.server.accept()
            
            session = Session(self.server, client, self.data_path)
            thread = threading.Thread(target=self.on_connect, args=(session,))
            thread.start()
            
    def on_connect(self, session):
        # Configure session
        session.settimeout(60_000)
        
        # Log successful connection
        print('Server: Accepted client connection.')
        session.send(type='display', body='Connection to the File Exchange Server is successful!')
              
        while True:
            try:
                message = session.receive()
            
            except ConnectionResetError:
                print('Server: Client has disconnected unexpectedly.')
                break
            
            if not message:
                session.close()
                print('Server: Client has been disconnected')
                
            interaction = Interaction(session, message)
            
            if interaction.is_command():
                self.on_interact(interaction) 
                
            else:
                session.send(type='display', body='Message must be a command.')
                
    def on_interact(self, interaction):
        session = interaction.session
        command_name = interaction.command_name
        command_obj = self.command_objs.get(command_name)
        
        if command_obj is None:
            session.send(type='display', body='Command not found.')
            return
        
        command_run = command_obj['run']
        
        try:
            # Validate interaction
            if self.validate_interaction(interaction, command_obj):
                return
            
            command_run(interaction, self)

        except Exception as e:
            print(e)
        
    def validate_interaction(self, interaction, command_obj):
        session = interaction.session
        
         # Check if command exists
        if command_obj is None:
            session.send(type='DISPLAY', body='Error: Command not found.')
            return True
        
        # Check for incorrect argument length        
        if command_obj['options'] is not None and len(interaction.options) != len(command_obj['options']):
            session.send(b'Error: Command parameters do not match or is not allowed.')
            return True

        # Command-specific validations
        if command_obj['validator'] is not None and command_obj['validator'](interaction, command_obj, self):
            return True
        
        # Check for incorrect data type (to be implemented)
        return False
