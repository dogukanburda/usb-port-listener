from cysystemd.reader import JournalReader, JournalOpenMode


reader = JournalReader()
reader.open(JournalOpenMode.SYSTEM)
reader.seek_tail()

poll_timeout = 255

reader.wait(poll_timeout)
for record in reader:
    try:
        print(record.data['PID'])
    except KeyError:
        pass