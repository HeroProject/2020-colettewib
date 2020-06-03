from social_interaction_cloud.abstract_connector import RobotType
from social_interaction_cloud.action import ActionRunner
from social_interaction_cloud.basic_connector import BasicSICConnector
from time import sleep


class Main:

    def __init__(self, server_ip, robot, dialogflow_key_file, dialogflow_agent_id):
        self.sic = BasicSICConnector(server_ip, robot, dialogflow_key_file, dialogflow_agent_id)
        self.action_runner = ActionRunner(self.sic)

        self.user_model = {'move_number': 1,
                           'continue_move' : False,
                           'complete_dance': True}
        self.recognition_manager = {'attempt_success': False,
                                    'attempt_number': 0}
#MISSCHIEN JSON FILE?
        self.continue_phrases = {}

        self.action_runner = ActionRunner(self.sic)

        self.total_nr_moves = 10

    def run(self):
        self.sic.start()

        self.action_runner.load_waiting_action('set_language', 'nl-NL')
        self.action_runner.load_waiting_action('wake_up')
        self.action_runner.run_loaded_actions()

        while not self.recognition_manager['attempt_success'] and self.recognition_manager['attempt_number'] < 2:
            self.action_runner.run_waiting_action('say', 'Hoi Ik ben Nao. Hoe heet jij?')
            self.action_runner.run_waiting_action('speech_recognition', 'answer_name', 3, additional_callback=self.on_name)
        self.reset_recognition_management()

        if 'name' in self.user_model:
            self.action_runner.run_waiting_action('say', 'Leuk je te ontmoeten' + self.user_model['name'])
        else:
            self.action_runner.run_waiting_action('say', 'Leuk je te ontmoeten!')

        while not self.recognition_manager['attempt_success'] and self.recognition_manager['attempt_number'] < 2:
            self.action_runner.run_waiting_action('say', 'Heb je zin om een dans spel te spelen?')
            self.action_runner.run_waiting_action('speech_recognition', 'answer_yesno', 3, additional_callback=self.on_play_game)
        # say something if fail.
        self.reset_recognition_management()

        if self.user_model['play_game']:
            self.start_game()
        else:
            self.stop_game()

        # EVENTUEEL NOG DOOR MET ANDERE OPTIE (NAO LEERT DANS VAN KIND)

        self.action_runner.run_waiting_action('rest')
        self.sic.stop()

    def on_name(self, intent_name, *args):
        if intent_name == 'answer_name' and len(args) > 0:
            self.user_model['name'] = args[0]
            self.recognition_manager['attempt_success'] = True
        elif intent_name == 'fail':
            self.recognition_manager['attempt_number'] += 1

    def on_play_game(self, intent_name, *args):
        if intent_name == 'answer_yes':
            self.user_model['play_game'] = True
            self.recognition_manager['attempt_success'] = True
        elif intent_name == 'answer_no':
            self.user_model['play_game'] = False
            self.recognition_manager['attempt_success'] = True
        elif intent_name == 'fail':
            self.user_model['play_game'] = True
            self.recognition_manager['attempt_number'] += 1

    def on_continue_move(self, intent_name, *args):
        if intent_name == 'answer_yes':
            self.user_model['continue_move'] = False
            self.recognition_manager['attempt_success'] = True
        elif intent_name == 'answer_no':
            self.user_model['continue_move'] = True
            self.recognition_manager['attempt_success'] = True
        elif intent_name == 'fail':
            self.user_model['continue_move'] = True
            self.recognition_manager['attempt_number'] += 1

    def on_complete_dance(self, intent_name, *args):
        if intent_name == 'answer_yes':
            self.user_model['complete_dance'] = True
            self.recognition_manager['attempt_success'] = True
        elif intent_name == 'answer_no':
            self.user_model['complete_dance'] = False
            self.recognition_manager['attempt_success'] = True
        elif intent_name == 'fail':
            self.user_model['complete_dance'] = True
            self.recognition_manager['attempt_number'] += 1

    def reset_recognition_management(self):
        self.recognition_manager.update({'attempt_success': False,
                                         'attempt_number': 0})

    def start_game(self):
        if 'name' in self.user_model:
            self.action_runner.run_waiting_action('say', 'Top, laten we beginnen dan' + self.user_model['name'])
        else:
            self.action_runner.run_waiting_action('say', 'Top, laten we beginnen dan!')

#CAMERA NEEDED?
        self.action_runner.run_waiting_action('say', 'Ik ga je een dans leren, aan het einde kun je die zelf optreden en laten zien!')

#LATER OPTIE TOEVOEGEN MOGELIJK OM DANS AAN NAO TE LEREN TOEVOEGEN, DAN OOK VRAAG OM LEREN OF AANLEREN

        self.teach_dance()

    def stop_game(self):
        self.action_runner.run_waiting_action('say', 'Oke, tot de volgende keer dan!')

    def teach_dance(self):

        #self.sic.start()
        self.action_runner.load_waiting_action('wake_up')

        self.action_runner.run_waiting_action('say', 'Oke, ik zal beginnen met je de hele dans te laten zien.'
                                                     'Daarna leer ik je stap voor stap de pasjes. Belangrijk is dat je eerst kijkt hoe ik beweeg, en pas daarna zelf het pasje uitvoert.')
        self.action_runner.run_waiting_action('do_gesture', 'dances/behavior_1')
        self.action_runner.run_waiting_action('say', 'Dat was de complete dans, laten we beginnen!')
        self.action_runner.run_waiting_action('say', 'Ik start altijd met een goeie move, daarna begint de rest van de dans. Deze gaat zo ')
        self.action_runner.run_waiting_action('do_gesture', 'dances/openingMove')
        self.action_runner.run_waiting_action('say', 'Heb je m? Dan gaan we nu door naar de rest van de dans. Hier komt stap 1.')


        while self.user_model['move_number'] < self.total_nr_moves:
            self.action_runner.run_waiting_action('do_gesture', 'dances/Move' + str(self.user_model['move_number']))
#NA ELKE MOVE STILSTAAN?  self.action_runner.run_waiting_action('go_to_posture', BasicNaoPosture.Stand)
#databank maken van dingen om te zeggen elke keer.
            self.action_runner.run_waiting_action('say', 'Kun je die stap voor me herhalen?')
#LATEN ZIEN, NOG IETS DOEN MET BEELD? moet echt kijken naar de persoon
            sleep(5)
            self.action_runner.run_waiting_action('say', 'Heel goed! Wil je het pasje nog een keer zien?')
            self.action_runner.run_waiting_action('speech_recognition', 'answer_yesno', 3, additional_callback=self.on_continue_move)

            if self.user_model['continue_move'] == True:
                self.user_model['move_number'] += 1
                self.action_runner.run_waiting_action('say', 'Door naar het volgende pasje. Komt ie!')

        self.action_runner.run_waiting_action('say', 'Dat waren ze bijna allemaal. Maar een dans is een performance, dus je eindigt natuurlijk met een buiging')
        self.action_runner.run_waiting_action('do_gesture', 'dances/takeABow')

        self.action_runner.run_waiting_action('say', 'Nu is ie echt compleet. Ik ga m nog 1 keer helemaal laten zien en daarna is het aan jou de beurt!')

        while self.user_model['complete_dance'] == True:
            self.action_runner.run_waiting_action('do_gesture', 'dances/behavior_1')
            self.action_runner.run_waiting_action('say', 'Nu jij!')

            self.action_runner.run_waiting_action('play_audio', 'caravanPalace.wav')

# KIJKEN NAAR PERSOON
            self.action_runner.run_waiting_action('say', 'Wil je nog een keer de hele dans doen?')
            self.action_runner.run_waiting_action('speech_recognition', 'answer_yesno', 3,
                                                  additional_callback=self.on_complete_dance)

            if self.user_model['complete_dance'] == True:
                self.action_runner.run_waiting_action('say', 'Oke, ik ga weer eerst, daarna mag jij nog een keer!')
            if self.user_model['complete_dance'] == False:
                self.action_runner.run_waiting_action('say', 'Oke, dat was het dan. Goed gedaan! Tot de volgende keer.')

        #self.sic.stop()

main = Main('192.168.2.141',
            RobotType.NAO,
            'coco.json',
            'coco-mrjvwk')

main.teach_dance()
