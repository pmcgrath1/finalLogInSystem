
#   10% of final grade.
#   Due Wed. 4th March 2015 - end of the day.
#   All code in Python, GAE, and webapp2.
#   Deploy on GAE.

import re
import os
import cgi
import webapp2
import jinja2
import random
from google.appengine.api import mail
from google.appengine.api import users
from webapp2_extras import sessions
from google.appengine.ext import ndb
from gaesessions import get_current_session

errorList = []

class UserDetail(ndb.Model):
    userid = ndb.StringProperty()
    email = ndb.StringProperty()
    passwd = ndb.StringProperty() 
    passwd2 = ndb.StringProperty()


class confirmedAccounts(ndb.Model):
    userid = ndb.StringProperty()
    email = ndb.StringProperty()
    passwd = ndb.StringProperty() 
    #passwd2 = ndb.StringProperty()
    changeNumber = ndb.StringProperty()


JINJA = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
)

class ResetHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA.get_template('reset.html')
        self.response.write(template.render({ 'the_title': 'Reset Your Password'}) )


    def post(self):
        user_address = cgi.escape(self.request.get('email'))
        user_id = cgi.escape(self.request.get('userid'))
        number= random.randrange(1,10000000)
         
        if user_id == "":
            template = JINJA.get_template('reset.html')
            self.response.write(template.render({ 'the_title': 'Reset Your Password','emptyUserid': 'Please enter a valid username','email':user_address,}) )
        elif user_address== "":
            template = JINJA.get_template('reset.html')
            self.response.write(template.render({ 'the_title': 'Reset Your Password','emptyUserAddress': 'Please enter an email address','userid':user_id,}) )
        
        else:

        
            stringNum = str(number)
            sender_address = "pmcgrath2400@gmail.com>"
            subject = "Password reset"
            body = """                To reset your password, click the link below, \n
                    Enter the following number when prompted """+stringNum+"""

                     http://c00162196itcarlow.appspot.com/changepassword?type="""+user_id

            query=ndb.gql("SELECT * FROM confirmedAccounts where userid = :1 ",user_id)
            row=query.fetch()

            query1=ndb.gql("SELECT * FROM confirmedAccounts where userid = :1 AND email=:2  ",user_id, user_address)
            row2=query1.fetch()

            print "second query ",row2
            if row ==[]:
                template = JINJA.get_template('reset.html')
                self.response.write(template.render({ 'the_title': 'Reset Your Password','emptyUserid': 'Please enter a valid username','email':user_address}) )

           
            elif row2 == []:
                template = JINJA.get_template('reset.html')
                self.response.write(template.render({ 'the_title': 'Reset Your Password','wrongEmail': 'Email address not valid for this user','userid':user_id}) )





            else:
                for row in row:

                    row.changeNumber=stringNum
                    row.put()
                    mail.send_mail(sender_address, user_address, subject, body)
                    emailSentPage = JINJA.get_template('resetEmail.html')
                    self.response.write(emailSentPage.render({ 'the_email': user_address }) )

class ChangePassHandler(webapp2.RequestHandler):
    def get(self):
         
        
        userid =self.request.get('type')
       

        template = JINJA.get_template('changePass.html')
        self.response.write(template.render({ 'the_title': 'Change Your Password'}) )
        
    def post(self):
        userid =self.request.get('userid')
        newpasswd = self.request.get('newpasswd')
        newpasswd1 = self.request.get('newpasswd1')
        number = self.request.get('number')

        if newpasswd =="":
            template = JINJA.get_template('changePass.html')
            self.response.write(template.render({ 'the_title': 'Change Your Password','emptyPassword': 'Please enter a password','userid':userid,'number':number}) )

        
        elif len(newpasswd) <= 5:
            template = JINJA.get_template('changePass.html')
            self.response.write(template.render({ 'the_title': 'Change Your Password','passwordToShort': 'Password must be at least 5 characters long','userid':userid,'number':number}) )
        
        elif re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])',newpasswd) is None:
            #print "password failed"
            template = JINJA.get_template('changePass.html')
            self.response.write(template.render({ 'the_title': 'Change Your Password','invalidPassWordFormat': 'Password must contain at least 1 number, 1 Upper and  1 Lowercase letter','userid':userid,'number':number}) )
        
        elif newpasswd1 =="":
            template = JINJA.get_template('changePass.html')
            self.response.write(template.render({ 'the_title': 'Change Your Password','emptyPassword1': 'Please enter the password a second time','userid':userid,'number':number}) )


        elif newpasswd != newpasswd1:
            template = JINJA.get_template('changePass.html')
            self.response.write(template.render({ 'the_title': 'Change Your Password','passwordMismatch': 'The passwords do not match','userid':userid,'number':number}) )
        
        else:

            num = self.request.get('number')
            userid = self.request.get('userid')

            print(num ,"and", userid)
            query=ndb.gql("SELECT * FROM confirmedAccounts where userid=:1 AND changeNumber=:2",userid, num)
            row=query.fetch()
            print(row)



            

            if row == [] :
                template = JINJA.get_template('changePass.html')
                self.response.write(template.render({ 'the_title': 'Change Your Password','wrongUserName': 'The username or verification number was incorrect'}) )
                print("match")
            
            else:
                for row in row:
                    row.passwd= newpasswd
                    row.changeNumber = ""
                    row.put()
                    template = JINJA.get_template('changeSuccess.html')
                    self.response.write(template.render({ 'the_title': 'Password Successfully changed'}) )





class LoginHandler(webapp2.RequestHandler):
    def get(self):
        
        template = JINJA.get_template('login.html')
        self.response.write(template.render({ 'the_title': 'Login page'}) )
        
    def post(self):

        
        userid = self.request.get('userid')
        passwd = self.request.get('passwd')

        if userid =="" or passwd =="":
            template = JINJA.get_template('login.html')
            self.response.write(template.render({ 'the_title': 'Please Login','UserNameError': 'Please enter a Username or Password' }) )

        else:


            session = get_current_session()
            session['userid'] = userid

            queryCnames = ndb.gql("SELECT * FROM confirmedAccounts  WHERE userid = :1",  userid  )
            cNames = queryCnames.fetch()

            if cNames ==[]:
                template = JINJA.get_template('login.html')
                self.response.write(template.render({ 'the_title': 'Please Login','UserNameError': 'Please enter a valid username' }) )

            else:
                for i in cNames:
                   
                    if userid == i.userid and passwd == i.passwd :

                        session = get_current_session()
                        session['userid'] = self.request.get('userid')
                        self.redirect('/page1')

                    elif passwd != i.passwd:

                        template = JINJA.get_template('login.html')
                        self.response.write(template.render({ 'the_title': 'Please Login','wrongPassword': 'Your password was incorrect' }) )




                    
        # Check that a login and password arrived from the FORM.
        # Lookup login ID in "confirmed" datastore.
        # Check for password match.
        # Set the user as logged in and let them have access to /page1, /page2, and /page3.  SESSIONs.
        # What if the user has forgotten their password?  Provide a password-reset facility/form.
       

# We need to provide for LOGOUT.

class Page1Handler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        #session.clear()

        if session.get('userid') == None:
            template = JINJA.get_template('login.html')
            self.response.write(template.render({ 'the_title': 'Login page'}) )
        else:
            template = JINJA.get_template('page1.html')
            self.response.write(template.render({ 'the_title': ' Page 1'}) )

    
class Page2Handler(webapp2.RequestHandler):
    def get(self):
        session = get_current_session()
        if session.get('userid') == None:
            

            template = JINJA.get_template('login.html')
            self.response.write(template.render({ 'the_title': 'Login page'}) )
        else:
            template = JINJA.get_template('page2.html')
            self.response.write(template.render({ 'the_title': ' Page 2'}) )


class Page3Handler(webapp2.RequestHandler):
    def get(self):

        session = get_current_session()
        
        if session.get('userid') == None:
            template = JINJA.get_template('login.html')
            self.response.write(template.render({ 'the_title': 'Login page'}) )
        else:
            template = JINJA.get_template('page3.html')
            self.response.write(template.render({ 'the_title': ' Page 3'}) )

class LogoutHandler(webapp2.RequestHandler):

    def post(self):
        session = get_current_session()
        session.terminate()
        template = JINJA.get_template('login.html')
        self.response.write(template.render({ 'the_title': 'Login page'}) )
        




class confirmHandler(webapp2.RequestHandler):
    def get(self):
        userid = self.request.get('type')
        
        

        query = ndb.gql("SELECT * FROM UserDetail  WHERE userid = :1",  userid )
        ret = query.fetch()

        queryCnames = ndb.gql("SELECT * FROM confirmedAccounts  WHERE userid = :1",  userid )
        cNames = queryCnames.fetch()
        if cNames == []:
            for i in ret:
                person = confirmedAccounts()
                person.userid = userid
                person.email  = i.email
                person.passwd =i.passwd
                person.changeNumber =""
                person.put()
        self.redirect('/login')
       
class RegisterHandler(webapp2.RequestHandler):
    def get(self):
       
        template = JINJA.get_template('reg.html')
        self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page' }) )
        self.response.out.write(cgi.escape(self.request.get('userid')))

    def post(self):
        
        userid = cgi.escape(self.request.get('userid'))
        email = cgi.escape(self.request.get('email') )
        passwd = cgi.escape(self.request.get('passwd'))
        passwd2 = cgi.escape(self.request.get('passwd2'))
        user_address = cgi.escape(self.request.get('email'))

        query = ndb.gql("SELECT * FROM UserDetail  WHERE userid = :1",  userid )
        ret = query.fetch()
        
        
            

        if userid =="":
            template = JINJA.get_template('reg.html')
            self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','UserNameError': 'You must enter a Username', 'email': email }) )

        elif passwd =="":
            template = JINJA.get_template('reg.html')
            self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','emptyPassword': 'Please Enter a password','userid': userid, 'email': email}) )

        elif passwd2 =="":
            template = JINJA.get_template('reg.html')
            self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','emptyPassword2': 'Please enter your password a second time' }) )
                
        elif len(passwd) <5:
            template = JINJA.get_template('reg.html')
            self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','passwordToShort': 'Password must be at least 5 characters long','userid':userid, 'email': email }) )

        elif re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])',passwd) is None:
            template = JINJA.get_template('reg.html')
            self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','invalidPassWordFormat': 'Password must contain at least 1 number, 1 Upper and  1 Lowercase letter','userid':userid, 'email': email }) )

        elif passwd != passwd2:
            template = JINJA.get_template('reg.html')
            self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','passwordMismatch': 'The passwords do not match' }) )

        elif email=="":
            template = JINJA.get_template('reg.html')
            self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','invalidEmail': 'Please enter an email address' ,'userid': userid}) )

        elif len(ret) > 0:
            template = JINJA.get_template('reg.html')
            self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','userNameUsed': 'The username name is unavailable' ,'email': email}) )




        else:
            for i in userid:

                
                if ord(i) == 32:
                    template = JINJA.get_template('reg.html')
                    self.response.write(template.render({ 'the_title': 'Welcome to the Registration Page','userNameSpaceError': 'No Spaces allowed in user name', 'email': email }) )
                    break
            else:



                user_address = cgi.escape(self.request.get('email'))

                sender_address = "pmcgrath2400@gmail.com"
                subject = "Confirm your registration"
                body = """Thank you for creating an account! Please confirm your email address by \nclicking on the link below and logging into your account:

                  http://c00162196itcarlow.appspot.com/confirm?type="""+userid 

                mail.send_mail(sender_address, user_address, subject, body)

                print("Commit to Database")
                person = UserDetail()

                person.userid = cgi.escape(self.request.get('userid'))
                person.email = cgi.escape(self.request.get('email') )
                person.passwd = cgi.escape(self.request.get('passwd'))
                person.passwd2 = cgi.escape(self.request.get('passwd2'))
                person.put()


                emailSentPage = JINJA.get_template('emailSent.html')
                self.response.write(emailSentPage.render({ 'the_email': email }) )

        # Check if the data items from the POST are empty.
        # Check if passwd == passwd2.
        # Does the userid already exist in the "confirmed" datastore or in "pending"?
        # Is the password too simple?
        
        # Add registration details to "pending" datastore.
        # Send confirmation email.

        # Can GAE send email?
        # Can my GAE app receive email?

        # This code needs to move to the email confirmation handler.
       



        

app = webapp2.WSGIApplication([
    ('/register', RegisterHandler),
    ('/processreg', RegisterHandler),
    ('/confirm',confirmHandler),
    ('/', LoginHandler),
    ('/login', LoginHandler),
    ('/processlogin', LoginHandler),
    
    # Next three URLs are only available to logged-in users.
    ('/page1', Page1Handler),
    ('/page2', Page2Handler),
    ('/page3', Page3Handler),
    ('/logout',LogoutHandler),
    ('/resetpassword',ResetHandler),
    ('/changepassword',ChangePassHandler),

])
