from json import dumps


class TelegramKeyboard:
    def __init__(self, resize_keyboard=True, one_time_keyboard=True, selective=False):
        self.__line_count = 0

        self.__keyboard_markup = {
            'resize_keyboard': resize_keyboard,
            'one_time_keyboard': one_time_keyboard,
            'keyboard': [],
            'selective': selective
        }

    def add_line(self):
        self.__keyboard_markup['keyboard'].append([])
        self.__line_count += 1

    def add_button(self, text):
        self.__keyboard_markup['keyboard'][self.__line_count - 1].append({"text": text})

    def get_keyboard(self):
        return dumps(self.__keyboard_markup)


if __name__ == "__main__":
    kb = TelegramKeyboard()
    kb.add_line()
    kb.add_button("Расписание на сегодня")
    kb.add_button("Расписание на завтра")
    kb.add_line()
    kb.add_button("Расписание на другой день")
    kb.add_line()
    kb.add_button("Изменить группу")
    print(kb.get_keyboard())
    print(dumps({
        'resize_keyboard': True,
        'one_time_keyboard': True,
        'keyboard': [
            [
                {'text': 'Расписание на сегодня'},
                {'text': 'Расписание на завтра'}
            ], [
                {'text': 'Расписание на другой день'}
            ], [
                {'text': 'Изменить группу'}
            ]],
        'selective': False
    }))
    print(kb.get_keyboard() == dumps({
        'resize_keyboard': True,
        'one_time_keyboard': True,
        'keyboard': [
            [
                {'text': 'Расписание на сегодня'},
                {'text': 'Расписание на завтра'}
            ], [
                {'text': 'Расписание на другой день'}
            ], [
                {'text': 'Изменить группу'}
            ]],
        'selective': False
    }))
