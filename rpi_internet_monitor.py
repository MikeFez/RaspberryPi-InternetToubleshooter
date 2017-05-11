import requests
from datetime import datetime
from time import sleep
import smtplib
from gpiozero import LED, Button

dont_send_email = True

notification_recipient = "your_email@example.com"
gmail_send_address = "sender_email@example.com"
gmail_send_password = "Hunter2"  # Whoa, does that appear as stars to you too??

power_pin = LED(14)
drawer_open = Button(15)
power_pin.off()

# sleep(60)


def main():
    current_internet_connection = True
    toggle_times = 0
    outage_data = {}
    while True:
        previous_internet_connection = current_internet_connection

        if check_connection() is True:
            print("Internet is connected")
            current_internet_connection = True
            sleep(30)
        else:
            print("Internet is not connected")

            current_internet_connection = False
            if drawer_currently_open() is False:
                print("Drawer is closed - proceeding")
                toggle_times += 1
                toggle_internet()
            else:
                print("Drawer is open - skipping reset")
            print("Waiting 60 seconds and then rechecking")
            sleep(60)

        if previous_internet_connection != current_internet_connection:
            if previous_internet_connection is True:
                # if internet was up and is now down
                outage_data['down'] = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
            else:
                # if internet was down and is now up
                outage_data['up'] = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
                outage_data['toggles'] = toggle_times
                notify_of_outage(outage_data)
                toggle_times = 0
    return


def drawer_currently_open():
    if drawer_open.is_pressed: return False
    else: return True


def check_connection():
    if navigate('https://www.google.com/') is True:
        internet_connection = True
    elif navigate('https://www.yahoo.com/') is True:
        internet_connection = True
    elif navigate('https://www.apple.com/') is True:
        internet_connection = True
    else:
        internet_connection = False

    return internet_connection


def navigate(url):
    try:
        requests.get(url)
        print("Established connection with " + url)
        connected = True
    except Exception:
        print("Could not establish connection with " + url)
        connected = False
    return connected


def toggle_internet():
    print("Disconnecting power for 30 seconds")
    power_pin.on()
    sleep(30)
    power_pin.off()
    print("Reconnecting power")
    return


def notify_of_outage(outage_data):
    msg = "Outage Detected:\n\n"
    msg += "Internet offline at: " + outage_data['down'] + "\n"
    msg += "Internet online at: " + outage_data['up'] + "\n"
    if outage_data['toggles'] == 1:
        msg += "Switch toggled " + str(outage_data['toggles']) + " time\n"
    else:
        msg += "Switch toggled " + str(outage_data['toggles']) + " times\n"

    email_send(notification_recipient, "", "Internet Outage Was Detected", msg)
    return


def email_send(to, cc, subject, body):
    if dont_send_email is False:
        gmail_user = gmail_send_address
        gmail_pwd = gmail_send_password
        FROM = gmail_user
        TO = to if type(to) is list else [to]
        CC = cc if type(cc) is list else [cc]
        SUBJECT = subject
        TEXT = body

        SEND = TO + CC

        # Prepare actual message
        message = """From: %s\nTo: %s\nCc: %s\nSubject: %s\n\n%s
        """ % (FROM, ", ".join(TO), ", ".join(CC), SUBJECT, TEXT)
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_pwd)
            server.sendmail(FROM, SEND, message)
            server.close()
            print("Mail Successfully Sent - To:" + to + ", CC:" + cc)
        except:
            print("Mail Failed To Send - To:" + to + ", CC:" + cc)
            print("Message Body:\n*****************\n" + body)
    else:
        print("Message Body:\n*****************\n" + body)
    return


if __name__ == "__main__":
    main()
