import socket
import pickle
#By Daniel Cordero and Julian Rangel
# Initialize client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'localhost'
port = 12000
client_socket.connect((host, port))

# Define users dictionary with initial data
users = {
    'A': {'password': 'A', 'balance': 0, 'txs': []},
    'B': {'password': 'B', 'balance': 0, 'txs': []},
    'C': {'password': 'C', 'balance': 0, 'txs': []},
    'D': {'password': 'D', 'balance': 0, 'txs': []}
}


def authenticate(username, password):
    data = {'type': 'authentication', 'username': username, 'password': password}
    client_socket.send(pickle.dumps(data))
    response = pickle.loads(client_socket.recv(1024))
    return response


def make_transaction(payer, amount, payee1, amount_payee1, payee2=None, amount_payee2=None):
    tx_id = len(users[payer]['txs']) + 100
    data = {
        'type': 'transaction',
        'id': tx_id,
        'payer': payer,
        'amount': amount,
        'payee1': payee1,
        'amount_payee1': amount_payee1
    }
    if payee2 and amount_payee2:
        data['payee2'] = payee2
        data['amount_payee2'] = amount_payee2
    client_socket.send(pickle.dumps(data))
    response = pickle.loads(client_socket.recv(1024))

    return response


def display_transactions(username):
    data = {'type': 'list', 'username': username}
    client_socket.send(pickle.dumps(data))
    response = pickle.loads(client_socket.recv(1024))
    print("Response received from server:", response)

    if response and username in response and 'txs' in response[username]:
        users[username]['balance'] = response[username]['balance']
        users[username]['txs'] = response[username]['txs']
        return response
    else:
        print("Error fetching transactions.")
        return None


def main():
    error_password_choice = ""
    while error_password_choice != "2":
        username = input("Enter username: ")
        password = input("Enter password: ")
        auth_response = authenticate(username, password)

        if auth_response['authenticated']:
            print(f"User {username} is authenticated")
            print(f"Current balance: {auth_response.get('balance', 'N/A')} BTC")
            print("Transactions:")
            for tx in auth_response['txs']:
                print(tx)

            choice = ""
            while choice != '3':
                print("\nMenu:")
                print("1. Make a transaction")
                print("2. Fetch and display the list of transactions")
                print("3. Quit")
                choice = input("Enter your choice: ")

                if choice == '1':
                    payer = username
                    amount = float(input("How much do you transfer? "))
                    payee1 = input("Who will be Payee1? (A, B, C, D) ")
                    amount_payee1 = float(input(f"How much {payee1} will receive? "))

                    if amount_payee1 > amount:
                        print("Amount exceeds transfer amount.")
                        continue

                    payee2 = None
                    amount_payee2 = None
                    # made changes here
                    if amount_payee1 < amount:
                        payee2 = input("Who will be Payee2? (A, B, C, D) ")
                        amount_payee2 = amount - amount_payee1

                    response = make_transaction(payer, amount, payee1, amount_payee1, payee2, amount_payee2)
                    if response['status'] == 'confirmed':
                        print("Transaction confirmed.")
                        print(f"Current balance: {response.get('balance', 'N/A')} BTC")
                    else:
                        print("Transaction rejected due to insufficient balance.")

                elif choice == '2':
                    response = display_transactions(username)
                    if response:
                        print(f"Current balance: {response.get('balance', 'N/A')} BTC")
                        print("Transactions:")
                        for tx in response['txs']:
                            print(tx)

                elif choice == '3':
                    print("Quitting program...")
                    break

                else:
                    print("Invalid choice. Please enter a valid option.")
        print(f"Authentication failed\n1.Try Again\n2. Quit")
        error_password_choice = input(f"Enter choice:")


if __name__ == "__main__":
    main()


