import os

import google.generativeai as palm

bard = os.getenv("PALM_API_KEY")
palm.configure(api_key=bard)

mes = palm.chat(messages="hello")
print(mes.last)
while True:
    question = str(input("Enter a question: "))
    mes = mes.reply(question)
    print(mes.last)
