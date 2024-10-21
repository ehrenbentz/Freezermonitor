#! /usr/bin/python3

########################################################################
#	     This script was written by E. Bentz: ejb345@cornell.edu       #
########################################################################
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any
# later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# Author: Ehren Bentz
# Project: Freezermonitor
# License: GNU General Public License v3.0

# Purpose:
# This script will monitor temperatures and upload them to a web dashboard using Initial State.
# If temperatures exceed user specified thresholds it will send warning emails to specified addresses.
##

# freezermonitor.py is intended to be run on a Raspberry Pi (or equvalent SBC) with internet connection
# and an installed MAX31865 circuit board with an attached platinum RTD temperature sensor.
#
# Configuration requires installation of Adafruit Blinka and adafruit-circuitpython-max31865
# Hardware, software, and basic tutorials for these components may be found at: https://www.adafruit.com/
#
# Settings for temperature thresholds, network and email parameters, Initialstate settings etc. are configured by editing the file "config.ini"
# config.ini must be properly formatted and located in the same directory as freezermonitor.py
#
#########################################################################

## Import libraries
import os
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import netifaces
import configparser
import inspect
import board
import digitalio
import adafruit_max31865
from ISStreamer.Streamer import Streamer

expected_params = {
    'DeviceSettings': ['HOSTNAME','DEVICE_LOCATION_NAME'],
    'NetworkSettings': ['WirelessInterface'],
    'EmailSettings': ['admin_email_list', 'email_list', 'gmail_account', 'gmail_password'],
    'EmailCustomText': [
        'CUSTOM_BOOT_MESSAGE_LINE_1','CUSTOM_BOOT_MESSAGE_LINE_2','CUSTOM_BOOT_MESSAGE_LINE_3',
        'CUSTOM_WEEKLY_MESSAGE_LINE_1','CUSTOM_WEEKLY_MESSAGE_LINE_2','CUSTOM_WEEKLY_MESSAGE_LINE_3',
        'CUSTOM_WARNING_MESSAGE_LINE_1','CUSTOM_WARNING_MESSAGE_LINE_2','CUSTOM_WARNING_MESSAGE_LINE_3',
        'CUSTOM_ALERT_MESSAGE_LINE_1','CUSTOM_ALERT_MESSAGE_LINE_2','CUSTOM_ALERT_MESSAGE_LINE_3',
        'CUSTOM_PANIC_MESSAGE_LINE_1','CUSTOM_PANIC_MESSAGE_LINE_2','CUSTOM_PANIC_MESSAGE_LINE_3'
    ],
    'AlarmThresholds': ['WARNING_TEMP', 'ALERT_TEMP', 'PANIC_TEMP', 'RESET_TEMP', 'SECONDS_BETWEEN_READINGS'],
    'RTDSetup': ['CSBoardLocation', 'SensorWires'],
    'InitialState': ['SENSOR_LOCATION_NAME', 'BUCKET_NAME', 'BUCKET_KEY', 'ACCESS_KEY', 'SHARE_LINK'],
}

### ----- Get settings from config.ini ----- ###

# Check that all parameters are present in config.ini
def validate_config_params():
    for section, params in expected_params.items():
        for param in params:
            if param not in config[section]:
                raise ValueError(f"Missing parameter '{param}' in section '{section}' of config.ini")

config = configparser.ConfigParser()
config.read('config.ini')
validate_config_params()

# Get device location from config.ini
HOSTNAME = config.get('DeviceSettings', 'HOSTNAME')
DEVICE_LOCATION_NAME = config.get('DeviceSettings', 'DEVICE_LOCATION_NAME')

# Get network settings from config.ini
WIRELESS_INTERFACE = config.get('NetworkSettings', 'WirelessInterface')

# Get email settings from config.ini
admin_email_list = config.get('EmailSettings', 'admin_email_list').split(',')
email_list = config.get('EmailSettings', 'email_list').split(',')
gmail_account = config.get('EmailSettings', 'gmail_account')
gmail_password = config.get('EmailSettings', 'gmail_password')

# Get custom message text from config.ini (up to 3 lines each)
CUSTOM_BOOT_MESSAGE_LINE_1 = config.get('EmailCustomText', 'CUSTOM_BOOT_MESSAGE_LINE_1')
CUSTOM_BOOT_MESSAGE_LINE_2 = config.get('EmailCustomText', 'CUSTOM_BOOT_MESSAGE_LINE_2')
CUSTOM_BOOT_MESSAGE_LINE_3 = config.get('EmailCustomText', 'CUSTOM_BOOT_MESSAGE_LINE_3')

CUSTOM_WEEKLY_MESSAGE_LINE_1 = config.get('EmailCustomText', 'CUSTOM_WEEKLY_MESSAGE_LINE_1')
CUSTOM_WEEKLY_MESSAGE_LINE_2 = config.get('EmailCustomText', 'CUSTOM_WEEKLY_MESSAGE_LINE_2')
CUSTOM_WEEKLY_MESSAGE_LINE_3 = config.get('EmailCustomText', 'CUSTOM_WEEKLY_MESSAGE_LINE_3')

CUSTOM_WARNING_MESSAGE_LINE_1 = config.get('EmailCustomText', 'CUSTOM_WARNING_MESSAGE_LINE_1')
CUSTOM_WARNING_MESSAGE_LINE_2 = config.get('EmailCustomText', 'CUSTOM_WARNING_MESSAGE_LINE_2')
CUSTOM_WARNING_MESSAGE_LINE_3 = config.get('EmailCustomText', 'CUSTOM_WARNING_MESSAGE_LINE_3')

CUSTOM_ALERT_MESSAGE_LINE_1 = config.get('EmailCustomText', 'CUSTOM_ALERT_MESSAGE_LINE_1')
CUSTOM_ALERT_MESSAGE_LINE_2 = config.get('EmailCustomText', 'CUSTOM_ALERT_MESSAGE_LINE_2')
CUSTOM_ALERT_MESSAGE_LINE_3 = config.get('EmailCustomText', 'CUSTOM_ALERT_MESSAGE_LINE_3')

CUSTOM_PANIC_MESSAGE_LINE_1 = config.get('EmailCustomText', 'CUSTOM_PANIC_MESSAGE_LINE_1')
CUSTOM_PANIC_MESSAGE_LINE_2 = config.get('EmailCustomText', 'CUSTOM_PANIC_MESSAGE_LINE_2')
CUSTOM_PANIC_MESSAGE_LINE_3 = config.get('EmailCustomText', 'CUSTOM_PANIC_MESSAGE_LINE_3')

# Get temperature thresholds from config.ini
WARNING_TEMP = config.getfloat('AlarmThresholds', 'WARNING_TEMP')
ALERT_TEMP = config.getfloat('AlarmThresholds', 'ALERT_TEMP')
PANIC_TEMP = config.getfloat('AlarmThresholds', 'PANIC_TEMP')
RESET_TEMP = config.getfloat('AlarmThresholds', 'RESET_TEMP')
SECONDS_BETWEEN_READINGS = config.getint('AlarmThresholds', 'SECONDS_BETWEEN_READINGS')

# Get RTD sensor settings from config.ini
CSBoardLocation = config.get('RTDSetup', 'CSBoardLocation')
SensorWires = config.getint('RTDSetup', 'SensorWires')
spi = board.SPI()
cs = digitalio.DigitalInOut(getattr(board, CSBoardLocation))
sensor = adafruit_max31865.MAX31865(spi, cs, wires=SensorWires)

# Get InitialState settings from config.ini
SENSOR_LOCATION_NAME = config.get('InitialState', 'SENSOR_LOCATION_NAME')
BUCKET_NAME = config.get('InitialState', 'BUCKET_NAME')
BUCKET_KEY = config.get('InitialState', 'BUCKET_KEY')
ACCESS_KEY = config.get('InitialState', 'ACCESS_KEY')
streamer = Streamer(bucket_name=BUCKET_NAME, bucket_key=BUCKET_KEY, access_key=ACCESS_KEY)
SHARE_LINK = config.get('InitialState', 'SHARE_LINK')

# Create error_logs directory if it does not yet exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Get current ip address
def get_wireless_ip_address(retries=10, delay=3):
    interface = WIRELESS_INTERFACE
    for i in range(retries):
        try:
            if interface in netifaces.interfaces():
                addr_list = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addr_list:
                    return addr_list[netifaces.AF_INET][0]['addr']
        except Exception as e:
            if i == retries - 1:
                with open('logs/ip_address_errors.txt', 'a') as log_file:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    log_file.write(f"{timestamp}: Failed to acquire ip address after {retries} tries\n")
        time.sleep(delay)
    return None

## ------ Code for emails notifications ------ ##

def retry_email(send_func):
    retries = 10
    delay = 30

    # Get the name of the function called when an error was logged
    caller_name = inspect.stack()[1].function

    for i in range(retries):
        try:
            send_func()
            break
        except Exception as e:
            if i < retries - 1:
                time.sleep(delay)
            else:
                # Log the reason for this failure along with the calling function's name
                with open('logs/email_errors.txt', 'a') as log_file:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    log_file.write(f"{timestamp}: Failed to send email using '{caller_name}' after {retries} attempts. Error: {e}\n")
                print(f"Failed to send email using '{caller_name}' after {retries} attempts. Error: {e}")

def send_boot_message():
    temperature = f'{sensor.temperature:.2f}'
    ip_address = get_wireless_ip_address()
    subject = f"{DEVICE_LOCATION_NAME} is online\r\n"
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = gmail_account
    msg['To'] = ', '.join(admin_email_list)
    msg['Reply-To'] = ', '.join(admin_email_list)
    body = f"""
    <html>
    <body>
        <p>{DEVICE_LOCATION_NAME} was just powered on, and monitoring software is running</p>
        <p>{CUSTOM_BOOT_MESSAGE_LINE_1}</p>
        <p>{CUSTOM_BOOT_MESSAGE_LINE_2}</p>
        <p>{CUSTOM_BOOT_MESSAGE_LINE_3}</p>
        <p>...</p>
        <p>The temperature at the time of this notification was:</p>
        <div style="margin-left: 30px;">
            <p>{temperature}&deg;C<p>
        </div>
        <p><a href="{SHARE_LINK}">CLICK HERE TO VIEW CURRENT TEMPERTURE</a></p>
        <p></p>
        <p>...</p>
        <p></p>
        <p>Notification thresholds are set to:<p>
        <div style="margin-left: 30px;">
            <p>Warning temp: {WARNING_TEMP}&deg;C<p>
            <p>Alert temp: {ALERT_TEMP}&deg;C<p>
            <p>Panic temp: {PANIC_TEMP}&deg;C<p>
            <p>Reset temp: {RESET_TEMP}&deg;C<p>
        </div>
        <p>...</p>
        <p>Access this device via ssh at: {HOSTNAME}@{ip_address}</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))
    def actual_send():
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(gmail_account, gmail_password)
        server.sendmail(gmail_account, admin_email_list, msg.as_string())
        server.close()
    retry_email(actual_send)

def send_weekly_update():
    temperature = f'{sensor.temperature:.2f}'
    ip_address = get_wireless_ip_address()
    subject = f"{DEVICE_LOCATION_NAME} is running normally\r\n"
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = gmail_account
    msg['To'] = ', '.join(email_list)
    msg['Reply-To'] = ', '.join(email_list)
    body = f"""
    <html>
    <body>
        <p>This is your weekly update for {DEVICE_LOCATION_NAME}. The device and software are running normally</p>
        <p>{CUSTOM_BOOT_MESSAGE_LINE_1}</p>
        <p>{CUSTOM_BOOT_MESSAGE_LINE_2}</p>
        <p>{CUSTOM_BOOT_MESSAGE_LINE_3}</p>
        <p>...</p>
        <p>The temperature at the time of this notification was:</p>
        <div style="margin-left: 30px;">
            <p>{temperature}&deg;C<p>
        </div>
        <p><a href="{SHARE_LINK}">CLICK HERE TO VIEW CURRENT TEMPERTURE</a></p>
        <p>...</p>
        <p>Notification thresholds are set to:<p>
        <div style="margin-left: 40px;">
            <p>Warning temp: {WARNING_TEMP}&deg;C<p>
            <p>Alert temp: {ALERT_TEMP}&deg;C<p>
            <p>Panic temp: {PANIC_TEMP}&deg;C<p>
        </div>
        <p>...</p>
        <p>Access this device via ssh at: {HOSTNAME}@{ip_address}</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))
    def actual_send():
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(gmail_account, gmail_password)
        server.sendmail(gmail_account, email_list, msg.as_string())
        server.close()
    retry_email(actual_send)

def send_warning():
    temperature = f'{sensor.temperature:.2f}'
    ip_address = get_wireless_ip_address()
    subject = f"WARNING: {DEVICE_LOCATION_NAME} temperature has exceeded {WARNING_TEMP}°C!\r\n"
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = gmail_account
    msg['To'] = ', '.join(email_list)
    msg['Reply-To'] = ', '.join(email_list)
    body = f"""
    <html>
    <body>
        <p>The temperature for {DEVICE_LOCATION_NAME} has exceeded {WARNING_TEMP}&deg;C!</p>
        <p>{CUSTOM_WARNING_MESSAGE_LINE_1}</p>
        <p>{CUSTOM_WARNING_MESSAGE_LINE_2}</p>
        <p>{CUSTOM_WARNING_MESSAGE_LINE_3}</p>
        <p>...</p>
        <p>The temperature at the time of this notification was:</p>
        <div style="margin-left: 30px;">
            <p>{temperature}&deg;C<p>
        </div>
        <p><a href="{SHARE_LINK}">CLICK HERE TO VIEW CURRENT TEMPERTURE</a></p>
        <p>...</p>
        <p>Access this device via ssh at: {HOSTNAME}@{ip_address}</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))
    def actual_send():
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(gmail_account, gmail_password)
        server.sendmail(gmail_account, email_list, msg.as_string())
        server.close()
    retry_email(actual_send)

def send_alert():
    temperature = f'{sensor.temperature:.2f}'
    ip_address = get_wireless_ip_address()
    subject = f"ALERT: {DEVICE_LOCATION_NAME} temperature has exceeded {ALERT_TEMP}°C!\r\n"
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = gmail_account
    msg['To'] = ', '.join(email_list)
    msg['Reply-To'] = ', '.join(email_list)
    body = f"""
    <html>
    <body>
        <p>The temperature for {DEVICE_LOCATION_NAME} has exceeded {ALERT_TEMP}&deg;C!</p>
        <p>{CUSTOM_ALERT_MESSAGE_LINE_1}</p>
        <p>{CUSTOM_ALERT_MESSAGE_LINE_2}</p>
        <p>{CUSTOM_ALERT_MESSAGE_LINE_3}</p>
        <p>...</p>
        <p>The temperature at the time of this notification was:</p>
        <div style="margin-left: 30px;">
            <p>{temperature}&deg;C<p>
        </div>
        <p><a href="{SHARE_LINK}">CLICK HERE TO VIEW CURRENT TEMPERTURE</a></p>
        <p>...</p>
        <p>Access this device via ssh at: {HOSTNAME}@{ip_address}</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))
    def actual_send():
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(gmail_account, gmail_password)
        server.sendmail(gmail_account, email_list, msg.as_string())
        server.close()
    retry_email(actual_send)

def send_panic():
    temperature = f'{sensor.temperature:.2f}'
    ip_address = get_wireless_ip_address()
    subject = f"PANIC: {DEVICE_LOCATION_NAME} temperature has exceeded {PANIC_TEMP}°C!\r\n"
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = gmail_account
    msg['To'] = ', '.join(email_list)
    msg['Reply-To'] = ', '.join(email_list)
    body = f"""
    <html>
    <body>
        <p>The temperature for {DEVICE_LOCATION_NAME} has exceeded {PANIC_TEMP}&deg;C!!!</p>
        <p>{CUSTOM_PANIC_MESSAGE_LINE_1}</p>
        <p>{CUSTOM_PANIC_MESSAGE_LINE_2}</p>
        <p>{CUSTOM_PANIC_MESSAGE_LINE_3}</p>
        <p>...</p>
        <p>The temperature at the time of this notification was:</p>
        <div style="margin-left: 30px;">
            <p>{temperature}&deg;C<p>
        </div>
        <p><a href="{SHARE_LINK}">CLICK HERE TO VIEW CURRENT TEMPERTURE</a></p>
        <p>...</p>
        <p>Access this device via ssh at: {HOSTNAME}@{ip_address}</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))
    def actual_send():
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(gmail_account, gmail_password)
        server.sendmail(gmail_account, email_list, msg.as_string())
        server.close()
    retry_email(actual_send)


## ----- Code for measuring temperatures and sending them to initialstate ----- ##


# Check that temps are below WARNING_TEMP. If temps are high, send notification
# Initialize global flags
def reset_temperature_alerts():
    global warning_sent, alert_sent, panic_sent
    warning_sent = False
    alert_sent = False
    panic_sent = False

def check_temperature_alerts(temperature):
    global warning_sent, alert_sent, panic_sent
    if WARNING_TEMP <= temperature < ALERT_TEMP and not warning_sent:
        log_temperature_threshold_exceeded(temperature, "WARNING_TEMP")
        retry_email(send_warning)
        warning_sent = True
    elif ALERT_TEMP <= temperature < PANIC_TEMP and not alert_sent:
        log_temperature_threshold_exceeded(temperature, "ALERT_TEMP")
        retry_email(send_alert)
        alert_sent = True
    elif PANIC_TEMP <= temperature < 100 and not panic_sent:
        log_temperature_threshold_exceeded(temperature, "PANIC_TEMP")
        retry_email(send_panic)
        panic_sent = True

# Log temperature, and send data to initialstate
def log_temperature():
    try:
        temperature = float('{0:0.2f}'.format(sensor.temperature))
    # Log an error if temperature cannot be read
    except Exception as e:
        with open("logs/sensor_errors.txt", "a") as log_file:
            log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Error reading sensor temperature - {str(e)}\n")
        temperature = None
    if temperature is not None:
        retries = 3
        for _ in range(retries):
            try:
                streamer.log(SENSOR_LOCATION_NAME + " Temperature", temperature)
                streamer.flush()
                break
            except Exception as e:
                time.sleep(10)
        else:  # Log an error if data cannot be sent to initialstate and all retries failed
            with open("logs/initialstate_errors.txt", "a") as log_file:
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Failed to send sensor data to InitialState after {retries} retries\n")
    return temperature

# save a log every time a temperature threshold is exceeded
def log_temperature_threshold_exceeded(temperature, threshold_type):
    with open("logs/temperature_thresholds_exceeded.txt", "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {threshold_type} exceeded with a sensor temperature of {temperature}°C\n")

# Logic for weekly update timing (8am mondays)
def check_weekly_updates(last_email_sent_date):
    current_time = datetime.now()
    current_date = current_time.date()
    day_of_week = current_time.weekday()
    if day_of_week == 0 and current_time.hour == 8 and 0 <= current_time.minute <= 10:
        if last_email_sent_date is None or (current_date - last_email_sent_date).days >= 6:
            send_weekly_update()
            last_email_sent_date = current_date
    return last_email_sent_date

## ------ Main program ------ ##

# Run main loop
def main():
    last_email_sent_date = None
    last_log_time = datetime.now()
    INTERVAL = SECONDS_BETWEEN_READINGS - 1
    while True:
        current_time = datetime.now()
        time_since_last_log = (current_time - last_log_time).total_seconds()
        if time_since_last_log >= INTERVAL:
            last_email_sent_date = check_weekly_updates(last_email_sent_date)
            try:
                temperature = log_temperature()
                last_log_time = datetime.now()
                if temperature >= WARNING_TEMP:
                    check_temperature_alerts(temperature)
                elif temperature < RESET_TEMP:
                    reset_temperature_alerts()
            except Exception as e:
                with open("logs/unexpected_errors.txt", "a") as log_file:
                    log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Unexpected error: {str(e)}\n")
        # pause script to limit cpu usage (without this, it runs the while loop at 100% cpu)
        time.sleep(5)

# Log startup
with open("logs/startup_logs.txt", "a") as f:
    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} freezermonitor service started\n")

# Send boot message to admin_email_list
send_boot_message()

# Run main()
main()
