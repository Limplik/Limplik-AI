import json
import os
import time
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

from openai import OpenAI


API_KEY = "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"

client = OpenAI(api_key=API_KEY)

HISTORY_FILE = "history.json"


KV = '''
BoxLayout:
    orientation: "vertical"

    BoxLayout:
        size_hint_y: None
        height: "50dp"

        Button:
            text: "☰"
            size_hint_x: .15
            on_press: app.show_history()

        Label:
            text: "Limplik AI"


    ScrollView:
        Label:
            id: chat
            text: app.chat_text
            size_hint_y: None
            height: self.texture_size[1]
            text_size: self.width, None


    BoxLayout:
        size_hint_y: None
        height: "55dp"

        TextInput:
            id: input_box
            multiline: False
            hint_text: "Сообщение..."

        Button:
            text: "Send"
            size_hint_x: .25
            on_press: app.send()


'''


class Limplik(App):

    chat_text = StringProperty("")

    def build(self):
        self.history = self.load_history()

        if self.history:
            self.chat_text = self.history[-1]["text"]

        return Builder.load_string(KV)


    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE,"r",encoding="utf-8") as f:
                return json.load(f)

        return []


    def save_history(self):
        with open(HISTORY_FILE,"w",encoding="utf-8") as f:
            json.dump(
                self.history,
                f,
                ensure_ascii=False,
                indent=2
            )


    def send(self):

        msg = self.root.ids.input_box.text

        if not msg:
            return

        self.root.ids.input_box.text = ""

        self.chat_text += "\n\nВы: " + msg + "\n\nИИ: "

        threading.Thread(
            target=self.ask_ai,
            args=(msg,)
        ).start()



    def ask_ai(self,msg):

        try:

            response = client.chat.completions.create(

                model="gpt-4.1",

                messages=[
                    {
                    "role":"user",
                    "content":msg
                    }
                ],

                max_tokens=16000
            )


            answer = response.choices[0].message.content


            for letter in answer:

                self.chat_text += letter
                time.sleep(0.03)


            self.history.append(
                {
                "text":self.chat_text
                }
            )

            self.save_history()


        except Exception as e:

            self.chat_text += "\nОшибка: "+str(e)



    def show_history(self):

        print("История:")

        for i,x in enumerate(self.history):

            print(i,x["text"][:50])


    def clear_chat(self):

        self.chat_text=""



if __name__=="__main__":
    Limplik().run()
