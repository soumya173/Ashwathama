from Backend import *
import tkinter as tk

# TODO : Clean up the data base. Delete rows which are not used much to prevent the data base to grow unnecessarily.
# TODO : Need a filter for abusive words. And prevent Ashwathama to learn those words.
# TODO : Train Ashwathama for basic support queries. Load a basic database entries.
# TODO : Add a default reply if the query reply is not found. Now it'll pick a random reply from database.
# TODO : Split process method into multiple methods. This will help to maintain the code.
# TODO : Implement logging for debugging purpose.
# TODO (FUTURE) : Add support for mails. Ashwathama will send a mail to support team if it's unable solve the query.
# TODO (FUTURE) : Take review after chat is over. Review will be important for improving Ashwathama.
# TODO : Add scrollbar to improve UI
# TODO : Delete older messages to clean up the UI
# TODO : Improve colors and fonts

class Frontend(object):
    """docstring for Frontend"""
    def __init__(self, title):

        # Root window config
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("350x200")

        # Messages wrapper frame config
        self.messageframe = tk.Frame(self.root)
        self.messageframe.pack(side=tk.TOP)

        self.bottext = tk.StringVar()
        self.usertext = tk.StringVar()
        self.botmsg = tk.Label(self.messageframe, textvariable=self.bottext, padx=5, pady=2, anchor='w', width=500)
        self.usermsg = tk.Label(self.messageframe, textvariable=self.usertext, padx=5, pady=2, anchor='e', width=500)

        # Input box wrapper frame config
        self.inputframe = tk.Frame(self.root)
        self.inputframe.pack(side=tk.BOTTOM, fill=tk.X)

        # Input box config
        self.userinputentry = tk.Entry(self.inputframe, justify=tk.CENTER)
        self.userinputentry.pack(fill=tk.X)

        # Submit button config
        self.submitbutton = tk.Button(self.inputframe, text="Send", command=self.getreply, padx=10, pady=5)
        self.submitbutton.pack()

        self.userinputentry.focus()
        self.root.bind('<Return>', self.getreply)
        self.root.mainloop()

    def on_configure(self, event):
        # update scrollregion after starting 'mainloop'
        # when all widgets are in canvas
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def printmessage(self, msg, alignment):
        # text = tk.StringVar()
        if alignment == 'right':
            # newmsg = tk.Label(self.messageframe, textvariable=text, padx=5, pady=2, anchor='e', width=500)
            self.usertext.set(msg)
            self.usermsg.pack(fill=tk.X)
        else:
            # newmsg = tk.Label(self.messageframe, textvariable=text, padx=5, pady=2, anchor='w', width=500)
            self.bottext.set(msg)
            self.botmsg.pack(fill=tk.X)
        # text.set(msg)
        # newmsg.pack(fill=tk.X)

    def getreply(self, event):
        usertextstr = self.userinputentry.get()
        self.printmessage(usertextstr, "right")

        backend = Backend()
        replytext = backend.process(usertextstr)

        self.userinputentry.delete(0, 'end')
        self.userinputentry.focus()

        self.printmessage(replytext, "left")

if __name__ == '__main__':
    fr = Frontend("Ashwathama")