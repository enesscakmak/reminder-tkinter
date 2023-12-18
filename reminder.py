import smtplib
import sqlite3
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tkinter import *
from tkcalendar import Calendar


def create_gradient(canvas, color1, color2):
    width, height = canvas.winfo_reqwidth(), canvas.winfo_reqheight()
    for i in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * (i / height))
        g = int(color1[1] + (color2[1] - color1[1]) * (i / height))
        b = int(color1[2] + (color2[2] - color1[2]) * (i / height))
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(0, i, width, i, fill=color, width=1)


def open_calendar():
    date = cal.selection_get()  # Get the selected date
    date_str = date.strftime("%d-%m-%Y")
    date_button.config(text=date_str)
    cal.place_forget()  # Hide the calendar

    # Save the reminder to the database
    conn = sqlite3.connect('reminders.db')
    cursor = conn.cursor()

    title_val = titleText.get().strip("\n")
    message_val = message.get("1.0", END).strip("\n")

    # Get the selected reminder option
    reminder_option = radiosVariable.get()

    # Calculate the reminder date based on the selected option
    reminder_date = cal.selection_get()
    if reminder_option == 1:  # "Week"
        reminder_date -= timedelta(weeks=1)
    elif reminder_option == 2:  # "Date"
        reminder_date -= timedelta(days=1)
    elif reminder_option == 3:  # "Hour"
        reminder_date -= timedelta(hours=1)

    # Check which checkboxes are selected
    if saveToSystem.get() and sendEmail.get():
        # Save and send email
        send_email_reminder(reminder_date, title_val, message_val)
    elif sendEmail.get():
        # Save until the date comes, then send email and delete the data
        save_and_send_later(reminder_date, title_val, message_val)
    elif saveToSystem.get():
        # Only save to system
        cursor.execute('''
                INSERT INTO reminders (title, date, message)
                VALUES (?, ?, ?)
            ''', (title_val, date_str, message_val))

        conn.commit()
        conn.close()
        pass


def save_and_send_later(reminder_date, title, message_body):
    current_date = datetime.today().date()
    if current_date == reminder_date:
        send_email_reminder(reminder_date, title, message_body)
        delete_saved_data(title)
    else:
        save_data_to_system(reminder_date, title, message_body)


def save_data_to_system(reminder_date, title, message_body):
    conn = sqlite3.connect('reminders.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reminders (title, date, message)
        VALUES (?, ?, ?)
    ''', (title, reminder_date.strftime("%d-%m-%Y"), message_body))
    conn.commit()
    conn.close()


def delete_saved_data(title):
    conn = sqlite3.connect('reminders.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM reminders
        WHERE title = ?
    ''', (title,))
    conn.commit()
    conn.close()


def send_email_reminder(reminder_date, title, message_body):
    # Add your email configuration
    sender_email = 'example@mail.com' # Replace with your email
    sender_password = 'password' # Replace with your password

    print("Sending Email...")

    # Create the message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = 'example@mail.com'  # Replace with the recipient's email
    msg['Subject'] = f'Reminder for {title}'

    msg.attach(MIMEText(f"Date for the message: {cal.selection_get()}\n\nMessage:\n\n{message_body}", 'plain'))

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, msg['To'], msg.as_string())


def show_calendar():
    cal.place(x=458, y=79)
    cal.lift()


root = Tk()
root.geometry("720x350")
root.title("Reminder")
root.resizable(False, False)

gradientCanvas = Canvas(root, width=720, height=350)
gradientCanvas.place(relx=0, rely=0)

gradient_color1 = (255, 255, 255)
gradient_color2 = (153, 150, 145)
create_gradient(gradientCanvas, gradient_color1, gradient_color2)

topFrame = Frame(root, background="#7ea6e6", width=700, height=60)
topFrame.place(relx=0, rely=0, x=10)

Label(topFrame, text="Message Title:", font=("Helvetica", 12), background="#7ea6e6", foreground="black").place(x=30,
                                                                                                               y=15)

titleText = Entry(topFrame, font=("Helvetica", 12,), width=10,
                  foreground="black", background="white", state="normal")
titleText.place(x=150, y=18)

Label(topFrame, text="Reminder Date:", font=("Helvetica", 12), background="#7ea6e6", foreground="black").place(
    x=370, y=15)

date_button = Button(topFrame, text="Select Date", font=("Helvetica", 10), background="#7ea6e6", foreground="black",
                     command=show_calendar, width=8, height=1)
date_button.place(x=500, y=15)

cal = Calendar(root, selectmode="day",
               background="#7ea6e6", foreground="black",
               mindate=datetime.now())

cal.place(x=458, y=40)
cal.place_forget()

ok_button = Button(topFrame, text="OK", command=open_calendar, width=5, height=1, background="#7ea6e6",
                   foreground="black")
ok_button.place(x=590, y=17)

leftFrame = Frame(root, background="#7ea6e6", width=220, height=270)
leftFrame.place(relx=0, rely=0, x=10, y=70)

Label(leftFrame, text="Reminder Method:", font=("Helvetica", 12), background="#7ea6e6", foreground="black").place(
    x=10, y=10)

saveToSystem = IntVar()
sendEmail = IntVar()

saveToSystemCheckbox = Checkbutton(leftFrame, text="Save to System", font=("Helvetica", 10), background="#7ea6e6",
                                   foreground="black", variable=saveToSystem)
saveToSystemCheckbox.place(x=10, y=60)

sendEmailCheckbox = Checkbutton(leftFrame, text="Send E-Mail", font=("Helvetica", 10), background="#7ea6e6",
                                foreground="black", variable=sendEmail)
sendEmailCheckbox.place(x=10, y=95)

radiosVariable = IntVar()
Radiobutton(leftFrame, text="Week before", background="#7ea6e6", activebackground="#7ea6e6", foreground="black",
            value=1, variable=radiosVariable).place(x=30, y=140)
Radiobutton(leftFrame, text="Day before", background="#7ea6e6", activebackground="#7ea6e6", foreground="black",
            value=2, variable=radiosVariable).place(x=30, y=170)
Radiobutton(leftFrame, text="Hour before", background="#7ea6e6", activebackground="#7ea6e6", foreground="black",
            value=3, variable=radiosVariable).place(x=30, y=200)

rightFrame = Frame(root, background="#7ea6e6", width=470, height=270)
rightFrame.place(relx=0, rely=0, x=240, y=70)

Label(rightFrame, text="Message:", font=("Helvetica", 12), background="#7ea6e6", foreground="black").place(
    x=10, y=10)

message = Text(rightFrame, width=50, height=9, font=('Helvetica', 12), background="#f0efd1", foreground="black")
message.place(x=8, y=40)

sendButton = Button(rightFrame, text="Complete", font=("Helvetica", 12), background="#c9c9c1", foreground="black",
                    command=open_calendar)
sendButton.place(x=200, y=220)

root.mainloop()
