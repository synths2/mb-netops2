class Action(object):
    def __init__(self, json_action):
        self.__json_action = json_action

    def is_private_message(self):
        return self.__json_action['channel'].startswith('D')

    @property
    def user_id(self):
        return self.__json_action.get('user', None)

    @property
    def response_url(self):
        return self.__json_action['response_url']

    @property
    def callback_id(self):
        return self.__json_action['callback_id']

    @property
    def action_name(self):
        return self.__json_action['actions'][0]['name']

    @property
    def original_message_text(self):
        return self.__json_action['original_message']['text']

    @property
    def action_value(self):
        return self.__json_action['actions'][0]['value']

    @property
    def type(self):
        return self.__json_action['type']

    @property
    def channel(self):
        return self.__json_action['channel']['id']
