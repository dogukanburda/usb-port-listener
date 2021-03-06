from cysystemd.reader import JournalReader, JournalOpenMode, Rule

rules = (
   Rule("SYSLOG_IDENTIFIER", "python3"))
reader = JournalReader()
reader.open(JournalOpenMode.SYSTEM)
# reader.seek_tail()
# reader.previous(skip=100)
reader.seek_head()
reader.add_filter(rules)
for record in reader:
    print(record.data['MESSAGE'])