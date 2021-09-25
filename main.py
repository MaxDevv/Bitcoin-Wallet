import os, sys, json, base58, os.path, hashlib, binascii, requests, time, re, threading, signal
from bit import *
from os import path
from bit.network import *

def handler(signum, frame):
    print("\n========================\n  |    Goodbye :D    |\n========================");exit()
signal.signal(signal.SIGINT, handler)

class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False


if not path.exists("wallet.key"):
    with Spinner():
        print("|Generating New Wallet\n")
        key = Key()
        pemkey = key.to_pem().decode("utf-8")
        print(pemkey)
        f = open("wallet.key", "w")
        f.write(pemkey)
        f.close()
else:
    print("|Logging Into Wallet")
    f = open("wallet.key", "r")
    key = Key.from_pem(f.read().encode("utf-8"))
print("|Getting wallet Info")
address = key.address

with Spinner():
    print("Connecting to The BlockChain |", end = '')
    balance = key.balance_as('usd')
    balance = key.balance_as('eur')
    balance = key.get_balance('btc') 
    get_fee_fast = get_fee(fast=True)


def clear(): 
    if os.name == 'nt': 
        _ = os.system('cls') 
    else: 
        _ = os.system('clear') 


def validateaddress(Address):
    regex = re.compile("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz") 
    if(regex.search(Address) == None): 
        return False
    else:
        base58Decoder = base58.b58decode(Address).hex()
        prefixAndHash = base58Decoder[:len(base58Decoder)-8]
        checksum = base58Decoder[len(base58Decoder)-8:]
        hash = prefixAndHash
        for x in range(1,3):
            hash = hashlib.sha256(binascii.unhexlify(hash)).hexdigest()
        if(checksum == hash[:8]):
            return True
        else:
            return False


def number_sendbtc_input(string) -> float: 
    while True: 
        try: 
            x = input(string)
            if x == "exit()":
                menu()
            else:
                return float(x)
        except ValueError: 
            print("Input only accepts decimal numbers.")  


def number_input(string) -> float: 
    while True: 
        try: 
            return float(input(string)) 
        except ValueError: 
            print("Input only accepts decimal numbers.")  


def send_btc():
    print("""
======================================
Type exit() To leave
""")
    recieverBitcoinAddress = input("Enter Reciever Bitcoin Address: ")
    if recieverBitcoinAddress.lower() == "exit()":
        clear()
        recieverBitcoinAddress = None
        recieverBitcoinAmount = None
        confirmation = None
        Fee = None
        transactionID = None
        menu()

    if validateaddress(recieverBitcoinAddress):
        print("Reciever Bitcoin Address: ", recieverBitcoinAddress)
        recieverBitcoinAmount = number_sendbtc_input("How Much BTC Do You want To Send Ex: BTC 0.0001\nBTC:")
        if recieverBitcoinAmount+float('%g'%(float('{:.10f}'.format((180*get_fee_fast)/100000000)))) > float(balance):
            if recieverBitcoinAmount < float(balance):
                print("Sorry You Have Enough Bitcoin For The Transaction But Not For The Fee")
            print("Sorry You Don't Have Enough Bitcoin")
            time.sleep(2)
            clear()
            recieverBitcoinAddress = None
            recieverBitcoinAmount = None
            confirmation = None
            Fee = None
            transactionID = None
            menu()

        while True:
            confirmation = input("""
=====================
 Confirm Transaction
=====================
Recierver Address: """+str(recieverBitcoinAddress)+"""
Sending Amount: """+str('%g'%(float('{:.8f}'.format(recieverBitcoinAmount))))+"""
Estimated Fee: """+str('%g'%(float('{:.10f}'.format((180*get_fee_fast)/100000000))))+"""
=====================
Y or N: """)
            if confirmation.lower() not in ('y', 'n', 'exit()'):
                print("Invalid Option Please Answer With Either Y or N")
                continue
            else:
                break
        if confirmation.lower() in ('y', 'n', 'exit()'):
            if confirmation == 'y':
                with Spinner():
                    print("Making Transaction, this might take a while |", end = '')
                    transactionID = key.send([(recieverBitcoinAddress, float(recieverBitcoinAmount), 'btc')])
                    Fee = (float('%g'%(float('{:.10f}'.format(json.loads(requests.get("https://api.blockcypher.com/v1/btc/main/txs/"+str(transactionID)).text)["fees"]/100000000)))) + float(recieverBitcoinAmount))
                print("""
  ================
       Recipt
  ================
Sender Address: """+address+"""
Recierver Address: """+recieverBitcoinAddress+"""
Sent Amount: """+recieverBitcoinAmount+"""
Transaction Fee: """+Fee+"""
Transaction ID: """+transactionID+"""
====================
Total: """+str(float(Fee)+float(recieverBitcoinAmount))
)
            elif confirmation == 'n':
                recieverBitcoinAddress = None
                recieverBitcoinAmount = None
                confirmation = None
                Fee = None
                transactionID = None
                menu()

            elif confirmation == 'exit()':
                recieverBitcoinAddress = None
                recieverBitcoinAmount = None
                confirmation = None
                Fee = None
                transactionID = None
                menu()

    elif not validateaddress(recieverBitcoinAddress):
        print("Invalid Bitcoin Address: ", recieverBitcoinAddress)
        send_btc()

def recieve_btc():
    input("Your recieving Address Is: "+address+"\nPress Enter To Go To Meun: ")
    menu()

def manage_balance():
    input("""
==================
  Manage Balance
==================
฿TC Balance: """+key.balance_as('btc')+"""
USD Balance: """+key.balance_as('usd')+"""
EUR Balance: """+key.balance_as('eur')+"""
Press Enter To Go To Meun: """)
    menu()

def quit_btc():
    print("\n========================\n  |    Goodbye :D    |\n========================");exit()

def export_wallet():
    input("""
=================
  Export Wallet
=================
WIF Format: """+str(key.to_wif())+""+"""
HEX Format: """+str(key.to_hex())+""+"""
INT Format: """+str(key.to_int())+""+"""
PEM Format: """+str(key.to_pem())+""+"""
DER Format: """+str(key.to_der())+""+"""
Press Enter To Go To Meun: """)
    menu()



def menu():
    clear()
    print("""
          ____  _ __             _
         / __ )(_) /__________  (_)___
        / __  / / __/ ___/ __ \/ / __ \\
       / /_/ / / /_/ /__/ /_/ / / / / /
      /_____/_/\__/\___/\____/_/_/ /_/
    ======================================
    Main Address: """+address+"""
    BTC Balance: """+balance+"""฿
    =======================================
      Good Day. What Would You Like to do
    =======================================
    1. Send Bitcoin
    2. Recieve Bitcoin
    3. Manage Balance
    4. Export Wallet
    5. Quit
    Press Ctrl+C or Quit To Exit

    """)

    option = input("Select Option: ")
    loa = ['1', '2', '3', '4', '5']
    if option in loa:
        if option == '1':
            send_btc()
        elif option == '2':
            recieve_btc()
        elif option == '3':
            manage_balance()
        elif option == '4':
            export_wallet()
        elif option == '5':
            quit_btc()
    else:
        print("Invalid Option Please Pick an option Between 1 to "+str(len(loa)))
        time.sleep(1)
        menu()


menu()