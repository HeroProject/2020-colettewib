from social_interaction_cloud.abstract_connector import RobotType
from social_interaction_cloud.action import ActionRunner
from social_interaction_cloud.basic_connector import BasicSICConnector, BasicNaoPosture
from time import sleep
import random

class Example:

    def __init__(self, server_ip, robot, dialogflow_key_file, dialogflow_agent_id):
        self.sic = BasicSICConnector(server_ip, robot, dialogflow_key_file, dialogflow_agent_id)
        self.action_runner = ActionRunner(self.sic)

        self.user_model = {'move_number': 1,
                           'continue_move' : False,
                           'complete_dance': True}
        self.recognition_manager = {'attempt_success': False,
                                    'attempt_number': 0}

        self.action_runner = ActionRunner(self.sic)


    def practice(self):
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

        self.action_runner.run_waiting_action('rest')
        self.sic.stop()

    def on_name(self, intent_name, *args):
        if intent_name == 'answer_name' and len(args) > 0:
            self.user_model['name'] = args[0]
            self.recognition_manager['attempt_success'] = True
        elif intent_name == 'fail':
            self.recognition_manager['attempt_number'] += 1

    def reset_recognition_management(self):
        self.recognition_manager.update({'attempt_success': False,
                                         'attempt_number': 0})


main = Example('192.168.2.148',
            RobotType.NAO,
            'coco.json',
            'coco-mrjvwk')

main.practice()