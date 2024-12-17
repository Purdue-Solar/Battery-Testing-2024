import serial
import time
import csv
import smtplib
from email.message import EmailMessage


#testing mode flag
TEST_MODE = False

if not TEST_MODE:
    #ENTER THE HIOKI COM PORT HERE
    #
    #
    #
    #
    serial_port = 'COM3'
    #
    #
    #
    ###############################  
    baud_rate = 9600
    timeout = 1

    ser = serial.Serial(
        port=serial_port,
        baudrate=baud_rate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=timeout,
    )

if not TEST_MODE: 
    from kp184 import *

# Initialize a variable to store the CSV file path

        
def get_voltage_and_resistance():
    if TEST_MODE:
        # Simulate random voltage and resistance values for testing
        voltage = round(3.7 + (0.1 * time.time() % 1), 2)
        resistance = round(10 + (5 * time.time() % 1), 2)
        ohms = "Ohms"
        return voltage, resistance, ohms
    else:
        try:
            time.sleep(1)
            ser.write(b'MEAS:VOLT?\r\n')
            time.sleep(0.1)
            voltage_response = ser.readline().decode().strip()
            voltage_str = voltage_response.split(',')[0]
            voltage = float(voltage_str)

            ser.write(b'MEAS:RES?\r\n')
            time.sleep(0.1)
            resistance_response = ser.readline().decode().strip()
            resistance_str = resistance_response.split(',')[0]
            resistance = float(resistance_str)
            time.sleep(1)

            return voltage, resistance
        except ValueError:
            print("Value error: could not convert response to float")
            return None, None, None
        except Exception as e:
            print(f"Error: {e}")
            return None, None, None
    
def start_measurement(discharge_rate, kp_comport, kp_address, peak_voltage, stop_voltage, interval, csv_file_path):
    print("debug1")
    interval = float(interval)
    discharge_rate = float(discharge_rate) * 4.9
    
    kp = KP184(kp_comport, kp_address)
    kp.writeMode('CC')
    kp.writeCC(discharge_rate)
    kp.writeLoadOnOff(True)
    measurements = 0
    print("debug2")
    voltage, resistance = get_voltage_and_resistance()

    while ((float(voltage) < float(peak_voltage)) and (float(voltage) > float(stop_voltage)) or (float(voltage) > 1000000)):
        measurements += 1
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([(measurements * interval), voltage, resistance, discharge_rate, ((measurements * interval) + (measurements * 2.2))])
        kp.writeLoadOnOff(False)
        voltage, resistance = get_voltage_and_resistance()
        print(f"measurement number = {measurements}")
        print(f"voltage = {voltage}")
        print(f"resistance = {resistance}")
        
        kp.writeLoadOnOff(True)
        time.sleep(interval)

    kp.writeLoadOnOff(False)
      
    message = 'testing is complete after ' + str(measurements) + " Measurements"
    send_email_gmail(message)
    

def send_email_gmail(content):
    #ENTER EMAIL INFORMAION HERE
    #
    #
    sender_email = 'purduesolar8@gmail.com'
    sender_password = 'xygc feef itws phha' #enter the APP password
    recipient_email = 'vrschmal@gmail.com'
    #
    #
    #
    #################################
    
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = 'HIOKI alert'
    msg.set_content(content)    
    
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS because idk thats what the documentation said
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)
        print("Email sent successfully!")
  
  
        
def main():
    csv_file_path = 'realCSV.csv'
    with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Load Time (s)", "Voltage (V)", "Resistance (ohms)", "Current (Amps)", "Absolute time (s)"])
    discharge_rate = input("Discharge Rate (C): ")
    stop_voltage = input("Stop Voltage: ")
    start_voltage = input("Start/peak voltage: ")
    interval = input("Interval in between measurements (seconds) :")
    kp_comport = input("KP comport: ")
    kp_address = input("KP address: ")
    start_measurement(discharge_rate, kp_comport, kp_address, start_voltage, stop_voltage, interval, csv_file_path)
    
    
if __name__ == "__main__" :
    main()