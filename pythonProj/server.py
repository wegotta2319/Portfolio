import socket
import pickle
#By Daniel Cordero and Julian Rangel
# Initialize server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'localhost'
port = 12000
server_socket.bind((host, port))
server_socket.listen(5)
print("Server listening...")

# Define user database
users = {
    'A': {'password': 'A', 'balance': 100, 'txs': []},
    'B': {'password': 'B', 'balance': 200, 'txs': []},
    'C': {'password': 'C', 'balance': 300, 'txs': []},
    'D': {'password': 'D', 'balance': 400, 'txs': []}
}
# Define list of confirmed TXs
confirmed_TXs = []

def authenticate_user(username, password):
    if username in users and users[username]['password'] == password:
        return True
    else:
        return False

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        received_data = pickle.loads(data)
        if received_data['type'] == 'authentication':
            username = received_data['username']
            password = received_data['password']
            if authenticate_user(username, password):
                response = {
                    'authenticated': True,
                    'balance': users[username]['balance'],
                    'txs': users[username]['txs']
                }
            else:
                response = {'authenticated': False}
            client_socket.send(pickle.dumps(response))

        elif received_data['type'] == 'transaction':
            payer = received_data['payer']
            amount = received_data['amount']
            payee1 = received_data['payee1']
            amount_payee1 = received_data['amount_payee1']
            payee2 = received_data.get('payee2', None)
            amount_payee2 = received_data.get('amount_payee2', None)
            if users[payer]['balance'] < amount:
                response = {
                    'status': 'rejected',
                    'balance': users[payer]['balance']
                }
            else:
                users[payer]['balance'] -= amount
                #added 62 so it txs is saved to payer too
                users[payer]['txs'].append({'id': received_data['id'], 'status': 'confirmed'})
                users[payee1]['balance'] += amount_payee1
                users[payee1]['txs'].append({'id': received_data['id'], 'status': 'confirmed'})
                if payee2:
                    users[payee2]['balance'] += amount_payee2
                    users[payee2]['txs'].append({'id': received_data['id'], 'status': 'confirmed'})
                #confirmed_TXs.append(received_data)#removed temporarily
                response = {
                    'status': 'confirmed',
                    'balance': users[payer]['balance']
                }
            client_socket.send(pickle.dumps(response))
        elif received_data['type'] == 'list':
            # Sending only the authenticated user's data
            username = received_data['username']
            if username in users:#this part was added
                response = {
                    #username: {
                        'balance': users[username]['balance'],
                        'txs': users[username]['txs']
                    #}
                }
            else:#this part was added
                response = {'error': 'User not found'}
            client_socket.send(pickle.dumps(response))
    client_socket.close()

while True:
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr} has been established!")
    handle_client(client_socket)

