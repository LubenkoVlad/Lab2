import re
import argparse
from typing import List, Tuple


class BankCardValidator:

    #Класс для проверки и поиска номеров банковских карт

    def __init__(self):
        # Регулярное выражение для поиска номеров банковских карт
        self.card_pattern = re.compile(r'''
            \b(?:4[0-9]{3}|5[1-5][0-9]{2}|6(?:011|5[0-9]{2})|3[47][0-9]{2})
            [- ]?[0-9]{4}
            [- ]?[0-9]{4}
            [- ]?[0-9]{4}
            \b
        ''', re.VERBOSE)

    def luhn_check(self, card_number: str) -> bool:

        #Проверка номера карты по алгоритму Луна

        digits = [int(d) for d in card_number if d.isdigit()]

        if len(digits) != 16:
            return False

        total = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit

        return total % 10 == 0

    def validate_card(self, card_number: str) -> Tuple[bool, str]:

        #Проверка номера карты на корректность

        clean_number = re.sub(r'[-\s]', '', card_number)

        if len(clean_number) != 16 or not clean_number.isdigit():
            return False, "Номер должен содержать 16 цифр"

        if not self.luhn_check(clean_number):
            return False, "Неверный номер карты (не проходит проверку Луна)"

        bin_number = clean_number[:4]
        card_type = self._identify_card_type(bin_number)

        return True, f"Корректный номер карты ({card_type})"

    def _identify_card_type(self, bin_number: str) -> str:

        #Определение типа карты по BIN

        first_digit = bin_number[0]
        first_two = bin_number[:2]

        if first_digit == '4':
            return "Visa"
        elif first_digit == '2':
            return "Мир"
        elif first_two in ['51', '52', '53', '54', '55']:
            return "MasterCard"
        elif first_two == '34' or first_two == '37':
            return "American Express"
        elif first_two in ['36', '38', '39']:
            return "Diners Club"
        elif first_two in ['60', '62', '64', '65']:
            return "Discover"
        elif first_two == '35':
            return "JCB"
        else:
            return "Неизвестный тип"

    def find_cards_in_text(self, text: str) -> List[Tuple[str, bool]]:

        #Поиск номеров карт в тексте

        found_cards = []
        matches = self.card_pattern.findall(text)

        for match in matches:
            clean_number = re.sub(r'[-\s]', '', match)
            is_valid = self.luhn_check(clean_number)
            found_cards.append((match, is_valid))

        return found_cards

    def find_cards_in_file(self, file_path: str) -> List[Tuple[str, bool, int]]:

        #Поиск номеров карт в файле

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                cards = self.find_cards_in_text(content)

                result = []
                for card, is_valid in cards:
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        if card in line:
                            result.append((card, is_valid, line_num))
                            break

                return result
        except FileNotFoundError:
            print(f"Файл {file_path} не найден")
            return []
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
            return []


def main():
    validator = BankCardValidator()

    parser = argparse.ArgumentParser(description='Поиск и проверка номеров банковских карт')
    parser.add_argument('--input', '-i', help='Проверить введенный номер карты')
    parser.add_argument('--file', '-f', help='Поиск карт в файле')

    args = parser.parse_args()

    if args.input:
        is_valid, message = validator.validate_card(args.input)
        print(f"Номер: {args.input}")
        print(f"Результат: {message}")

    elif args.file:
        print(f"Поиск номеров карт в файле: {args.file}")
        cards = validator.find_cards_in_file(args.file)

        if cards:
            print(f"Найдено {len(cards)} номер(ов) карт:")
            for card, is_valid, line_num in cards:
                status = "ВАЛИДНЫЙ" if is_valid else "НЕВАЛИДНЫЙ"
                print(f"  Строка {line_num}: {card} - {status}")
        else:
            print("Номера карт не найдены")

    else:
        print("Проверка номеров банковских карт \n")
        print("1. Проверить номер карты")
        print("2. Поиск в тексте")
        print("3. Поиск в файле")

        choice = input("Выберите опцию (1-3): ").strip()

        if choice == '1':
            card_number = input("Введите номер карты: ").strip()
            is_valid, message = validator.validate_card(card_number)
            print(f"Результат: {message}")

        elif choice == '2':
            text = input("Введите текст для поиска: ").strip()
            cards = validator.find_cards_in_text(text)

            if cards:
                print(f"Найдено {len(cards)} номер(ов) карт:")
                for card, is_valid in cards:
                    status = "ВАЛИДНЫЙ" if is_valid else "НЕВАЛИДНЫЙ"
                    print(f"  {card} - {status}")
            else:
                print("Номера карт не найдены")

        elif choice == '3':
            file_path = input("Введите путь к файлу: ").strip()
            cards = validator.find_cards_in_file(file_path)

            if cards:
                print(f"Найдено {len(cards)} номер(ов) карт:")
                for card, is_valid, line_num in cards:
                    status = "ВАЛИДНЫЙ" if is_valid else "НЕВАЛИДНЫЙ"
                    print(f"  Строка {line_num}: {card} - {status}")
            else:
                print("Номера карт не найдены")
        else:
            print("Неверный выбор")


if __name__ == "__main__":
    main()