from cysystemd import journal

journal.write("Hello w0rld")

# Or send structured data
journal.send(message="Daemon pid:{} ".format(str(os.getpid())),priority=journal.Priority.INFO, PID=str(os.getpid()))

