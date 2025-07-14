import streamlit as st
import pywhatkit
import pyautogui
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from instagrapi import Client
import datetime
import time
from twilio.rest import Client as TwilioClient
import base64
import os

# Custom CSS for modern styling
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTextInput>div>input, .stTextArea>div>textarea {
        border-radius: 8px;
        border: 1px solid #d1d5db;
    }
    .sidebar .stSelectbox {
        background-color: #ffffff;
        border-radius: 8px;
    }
    .stSpinner {
        color: #4CAF50;
    }
    .help-expander {
        background-color: #e5e7eb;
        border-radius: 8px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Page configuration
st.set_page_config(page_title="All-in-One Automation Tool", layout="wide", initial_sidebar_state="expanded")

# Title and theme toggle
col1, col2 = st.columns([3, 1])
with col1:
    st.title("All-in-One Automation Dashboard")
with col2:
    theme = st.selectbox("Theme", ["Light", "Dark"], key="theme")
    if theme == "Dark":
        st.markdown("""
            <style>
            .main { background-color: #1e293b; color: #f3f4f6; }
            .stTextInput>div>input, .stTextArea>div>textarea { background-color: #334155; color: #f3f4f6; }
            .sidebar .stSelectbox { background-color: #334155; }
            .help-expander { background-color: #475569; }
            </style>
        """, unsafe_allow_html=True)

# Sidebar menu
menu = st.sidebar.selectbox(
    "Choose an action:",
    ("Send WhatsApp Message", "Send Email", "Post to Instagram", "Send SMS", "Send Text Message", "Make Phone Call", "Exit"),
    help="Select an automation task to perform."
)

if menu == "Send WhatsApp Message":
    st.header("📱 Send WhatsApp Message")
    with st.form("whatsapp_form"):
        col1, col2 = st.columns(2)
        with col1:
            phone = st.text_input("Phone Number", placeholder="+91XXXXXXXXXX", help="Enter phone number with country code.")
        with col2:
            now = datetime.datetime.now()
            send_hour = st.number_input("Hour (24-hr)", min_value=0, max_value=23, value=now.hour, step=1)
            send_minute = st.number_input("Minute", min_value=0, max_value=59, value=(now.minute + 2) % 60, step=1)
        message = st.text_area("Message", placeholder="Type your message here...", height=100)
        submit = st.form_submit_button("Schedule & Send Message")

        with st.expander("Help"):
            st.markdown("Enter a valid phone number with country code (e.g., +919876543210). The message will be scheduled for the specified time.")

        if submit:
            if not phone.startswith("+"):
                st.error("Phone number must include country code (e.g., +91).")
            else:
                with st.spinner("Scheduling WhatsApp message..."):
                    try:
                        pywhatkit.sendwhatmsg(phone, message, send_hour, send_minute, wait_time=10)
                        st.success(f"Message scheduled at {send_hour}:{send_minute:02d}!")
                    except Exception as e:
                        st.error(f"Failed to send message: {e}")

elif menu == "Send Email":
    st.header("Send Email using Gmail")
    with st.form("email_form"):
        col1, col2 = st.columns(2)
        with col1:
            sender_email = st.text_input("Sender Email", placeholder="your.email@gmail.com")
            app_password = st.text_input("App Password", type="password", placeholder="16-character app password")
        with col2:
            receiver_email = st.text_input("Receiver Email", placeholder="recipient@example.com")
            subject = st.text_input("Subject", placeholder="Enter email subject")
        body = st.text_area("Email Body", placeholder="Type your email content here...", height=150)
        submit = st.form_submit_button("Send Email")

        with st.expander("Help"):
            st.markdown("Generate a 16-character app password from your Gmail account under security settings.")

        if submit:
            if not sender_email or not receiver_email or not subject or not body:
                st.error("All fields are required.")
            else:
                with st.spinner("Sending email..."):
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = sender_email
                        msg['To'] = receiver_email
                        msg['Subject'] = subject
                        msg.attach(MIMEText(body, 'plain'))

                        with smtplib.SMTP('smtp.gmail.com', 587) as server:
                            server.starttls()
                            server.login(sender_email, app_password)
                            server.sendmail(sender_email, receiver_email, msg.as_string())

                        st.success("Email sent successfully!")
                    except Exception as e:
                        st.error(f"Failed to send email: {e}")

elif menu == "Post to Instagram":
    st.header("📸 Post to Instagram")
    with st.form("instagram_form"):
        col1, col2 = st.columns(2)
        with col1:
            insta_user = st.text_input("Instagram Username", placeholder="your_username")
            insta_pass = st.text_input("Instagram Password", type="password", placeholder="Your password")
        with col2:
            photo = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        caption = st.text_area("Caption", placeholder="Write your post caption...", height=100)
        submit = st.form_submit_button("Post to Instagram")

        with st.expander("Help"):
            st.markdown("Upload a JPG or PNG image and ensure your Instagram credentials are correct.")

        if submit:
            if not photo or not insta_user or not insta_pass:
                st.error("All fields are required.")
            else:
                with st.spinner("Posting to Instagram..."):
                    try:
                        # Save uploaded file temporarily
                        photo_path = f"temp_{photo.name}"
                        with open(photo_path, "wb") as f:
                            f.write(photo.read())
                        cl = Client()
                        cl.login(insta_user, insta_pass)
                        cl.photo_upload(photo_path, caption)
                        os.remove(photo_path)  # Clean up
                        st.success("Posted successfully to Instagram!")
                    except Exception as e:
                        st.error(f"Failed to post: {e}")

elif menu == "Send SMS":
    st.header("Send SMS using Twilio")
    with st.form("sms_form"):
        col1, col2 = st.columns(2)
        with col1:
            account_sid = st.text_input("Twilio Account SID", placeholder="Your Twilio Account SID")
            auth_token = st.text_input("Twilio Auth Token", type="password", placeholder="Your Twilio Auth Token")
        with col2:
            from_number = st.text_input("Twilio Phone Number", placeholder="+91XXXXXXXXXX")
            to_number = st.text_input("Receiver Phone Number", placeholder="+91XXXXXXXXXX")
        sms_message = st.text_area("SMS Message", placeholder="Type your SMS here...", height=100)
        submit = st.form_submit_button("Send SMS")

        with st.expander("Help"):
            st.markdown("Obtain Twilio credentials from your Twilio dashboard. Use phone numbers in E.164 format (e.g., +919876543210).")

        if submit:
            if not all([account_sid, auth_token, from_number, to_number, sms_message]):
                st.error("All fields are required.")
            else:
                with st.spinner("Sending SMS..."):
                    try:
                        client = TwilioClient(account_sid, auth_token)
                        message = client.messages.create(
                            body=sms_message,
                            from_=from_number,
                            to=to_number
                        )
                        st.success(f"SMS sent! SID: {message.sid}")
                    except Exception as e:
                        st.error(f"Failed to send SMS: {e}")

elif menu == "Send Text Message":
    st.header("Send Text Message (via pywhatkit)")
    with st.form("text_message_form"):
        col1, col2 = st.columns(2)
        with col1:
            phone = st.text_input("Phone Number", placeholder="+91XXXXXXXXXX")
        with col2:
            hour = st.number_input("Hour (24-hr)", min_value=0, max_value=23, step=1)
            minute = st.number_input("Minute", min_value=0, max_value=59, step=1)
        message = st.text_area("Message", placeholder="Type your text message here...", height=100)
        submit = st.form_submit_button("Send Scheduled Text")

        with st.expander("Help"):
            st.markdown("Schedule a text message via WhatsApp. Ensure the phone number includes the country code.")

        if submit:
            if not phone.startswith("+"):
                st.error("Phone number must include country code (e.g., +91).")
            else:
                with st.spinner("Scheduling text message..."):
                    try:
                        pywhatkit.sendwhatmsg(phone, message, int(hour), int(minute))
                        st.success("Text message scheduled!")
                    except Exception as e:
                        st.error(f"Failed to schedule message: {e}")

elif menu == "Make Phone Call":
    st.header("Make a Phone Call using Twilio")
    with st.form("call_form"):
        col1, col2 = st.columns(2)
        with col1:
            account_sid = st.text_input("Twilio Account SID", placeholder="Your Twilio Account SID")
            auth_token = st.text_input("Twilio Auth Token", type="password", placeholder="Your Twilio Auth Token")
        with col2:
            from_number = st.text_input("Twilio Phone Number", placeholder="+91XXXXXXXXXX")
            to_number = st.text_input("Receiver Phone Number", placeholder="+91XXXXXXXXXX")
        call_message = st.text_input("Message to Speak", placeholder="Message for Twilio's voice API")
        submit = st.form_submit_button("Make Call")

        with st.expander("Help"):
            st.markdown("Enter a message for Twilio's text-to-speech. Use phone numbers in E.164 format.")

        if submit:
            if not all([account_sid, auth_token, from_number, to_number, call_message]):
                st.error("All fields are required.")
            else:
                with st.spinner("Initiating call..."):
                    try:
                        client = TwilioClient(account_sid, auth_token)
                        call = client.calls.create(
                            twiml=f'<Response><Say>{call_message}</Say></Response>',
                            to=to_number,
                            from_=from_number
                        )
                        st.success(f"Call initiated! Call SID: {call.sid}")
                    except Exception as e:
                        st.error(f"Failed to make call: {e}")

else:
    st.info("Thank you for using the Automation Dashboard! Select an action from the sidebar to get started.")
