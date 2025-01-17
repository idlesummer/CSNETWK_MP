from pathlib import Path


def run(interaction, commander):
    conn = interaction.conn
    session = interaction.session
    storage_path = Path(session.storage_path)
    
    # Get list of files in client's storage
    dir_paths = [file_path.name for file_path in storage_path.iterdir()]
    dir_paths = '\n'.join(dir_paths) if dir_paths else 'Empty'
    
    # Send list of files
    conn.send(f'DISPLAY \nServer Directory\n{dir_paths}\n'.encode())

data = {
    'name': 'dir',
    'run': run,
}
