from threading import Thread

class DebugCommand(Thread):
    
    def __init__(self, data, conn, chan, chan_id, e):
        Thread.__init__(self)
        self.user = data
        self.connection = conn
        self.channel = chan
        self.channel_id = chan_id
        self.e = e
        
    def run(self):
        if self.user.is_broadcaster or self.user.is_mod:
            print(f'Recieved Debug command from {self.user.username}... Printing tags')
            self.send_message(f"I printed the tags to the console of the chatbot. "
                               "I hope you were asked to run this "
                               "or you wanted to debug something")
            print(f"User Tags:\n{self.e.tags}\n"
                  f"Recieved Message: {self.e.arguments[0]}\n"
                  f"Connected Channel: {self.channel}\n"
                  f"Channel ID: {self.channel_id}\n")
        else:
            self.send_message(f"You are not authorized to use the debug command, {self.user.username}. "
                               "Please ask the streamer for permission if you believe this is "
                               "an error.")
        return
    
    def send_message(self, msg):
        self.connection.privmsg(self.channel, msg)