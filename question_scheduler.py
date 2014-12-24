
# coding: utf-8

# Import modules
import smtplib, time, sched, os
from email.mime.text import MIMEText

# Get the question data from a file
from questions import questions

def send_mail(recipient, subject, message, message_type = 'html'):
    msg = MIMEText(message, message_type)
    sender = env['ELF_EMAIL']
    passwd = env['ELF_PASSWORD']
    smtp_srv = "smtp.live.com"
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    # Send the message via the STMP server
    smtp = smtplib.SMTP(smtp_srv,587)
    smtp.ehlo()
    # Set up encryption
    smtp.starttls()
    smtp.ehlo()
    smtp.login(sender, passwd)
    smtp.sendmail(sender, [recipient], msg.as_string())
    smtp.quit()

def request_answers(question, question_id):
    subject = "Elf request"
    statuses = []
    for user in users:
        email = env.get(user + '_EMAIL', '')
        if email:
            posting_address = env.get(user + '_POSTING_ADDRESS', default_posting_address)
            message = '<strong>' + question + '</strong><br><br>Email your answers to <a href="mailto:' + posting_address + '?subject=Response%20to%20' + question_id + '." target="_top">' + posting_address + '</a><br><br>See answers at <a href="' + site_url + '">curiouself.com</a>.<br><br>xoxox'
            statuses.append(send_mail(email, subject, message, message_type='html'))
    return statuses

def post_question(question, question_id):
    subject = question
    message = "[title %s: %s]\n[tags question]" % (question_id, question)
    return send_mail(default_posting_address, subject, message, message_type='plain')

def post_and_request(question, question_id):
    return post_question(question, question_id), request_answers(question, question_id)

def print_question(question, question_id):
    "A test function to display information about a question and its recipients"
    print time.strftime('%Y-%m-%d %H:%M:%S')
    print "\n%s: %s" % (question_id, question)
    for user in users:
        email = env.get(user + '_EMAIL', '')
        if email:
            print user, email

### SETTINGS ###
send_emails = True
site_url = "http://curiouself.com"
users = ["BENJ","ELF","NOAH","SOPHIA","OLIVIA","JETHRO","CLAUDIA"]

# Get the settings from file or os.environ variables
if os.path.isfile('settings.py'):
    import settings
    env = settings.environ
else:
    env = os.environ
default_posting_address = env['DEFAULT_POSTING_ADDRESS']
print default_posting_address

##### SCRIPT EXECUTION ######
elf = sched.scheduler(time.time, time.sleep)

for question in questions:
    if question.get('id','') and question.get('text',''):
        params = (
            question['text'],
            "QuestionNumber"+question['id']
        )
        if question.get('datetime',''):
            use_time = time.mktime(time.strptime(question['datetime'],'%d/%m/%Y %H:%M:%S'))
            if send_emails:
                elf.enterabs(use_time, 1, post_and_request, params)
            elf.enterabs(use_time, 2, print_question, params)
            print "added", question['id']
        elif question.get('delay',''):
            if send_emails:
                elf.enter(float(question['delay']), 1, post_and_request, params)
            elf.enter(float(question['delay']), 2, print_question, params)
            print "added", question['id']

elf.run()
