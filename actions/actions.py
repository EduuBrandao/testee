import requests
import spacy
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
from typing import Text, Dict, Any, List
from flask import Flask
from flask_cors import CORS
from flask_cors import cross_origin


class ActionGetCEPInfo(Action):
    def name(self):
        return "action_get_cep_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        cep = tracker.get_slot("cep")

        if cep:
            dispatcher.utter_message(f"CEP {cep} foi digitado com sucesso!")
        else:
            dispatcher.utter_message("Desculpe, não foi possível identificar o CEP. Por favor, digite o CEP novamente.")

        return []

class ActionAffirm(Action):
    def name(self) -> Text:
        return "action_affirm"

    def run(self, dispatcher, tracker, domain):
        cep = "03967010"

        if cep:
            url = f"https://viacep.com.br/ws/{cep}/json/"
            response = requests.get(url)

            if response.status_code == 200:
                cep_info = response.json()
                dispatcher.utter_message(f"As informações para o CEP {cep} são: {cep_info}")
            else:
                dispatcher.utter_message("Não foi possível encontrar informações para este CEP.")
        else:
            dispatcher.utter_message("Por favor, forneça um CEP válido.")

        return [SlotSet("cep", cep)]

class ActionDeny(Action):
    def name(self) -> Text:
        return "action_deny"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[EventType]:
        dispatcher.utter_message("Entendi. Se você mudar de ideia, estou aqui para ajudar.")
        return []


class ActionCaptureCPF(Action):
    def name(self) -> Text:
        return "action_capture_cpf"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        text = tracker.latest_message.get("text")
        cpf_matches = re.findall(r'\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11}', text)

        if cpf_matches:
            captured_cpf = cpf_matches[0]
            dispatcher.utter_message(f"Você mencionou o CPF: {captured_cpf}")
        else:
            dispatcher.utter_message("Desculpe, não consegui identificar um CPF na sua mensagem.")

        return [SlotSet("captured_cpf", captured_cpf)]

class ActionCheckName(Action):
    def name(self) -> Text:
        return "action_check_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text")

        nlp = spacy.load("pt_core_news_sm")
        doc = nlp(user_message)

        name = None

        for ent in doc.ents:
            if ent.label_ == "PER":
                name = ent.text
                break

        if name:
            confirmation_message = f"Você digitou {name}, é isso mesmo?"
        else:
            confirmation_message = "Não consegui encontrar o seu nome."

        dispatcher.utter_message(text=confirmation_message)

        return []
