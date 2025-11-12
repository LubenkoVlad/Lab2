import unittest
import tempfile
import os
import sys
import io
from contextlib import redirect_stdout

# Добавляем путь к текущей директории для импорта
sys.path.append('.')

from bank_card_validator import BankCardValidator


class TestBankCardValidator(unittest.TestCase):

    def setUp(self):
        #Настройка перед каждым тестом
        self.validator = BankCardValidator()

    def test_valid_visa_card(self):
        #Тест валидного номера Visa карты
        valid_visa = "4111-1111-1111-1111"
        is_valid, message = self.validator.validate_card(valid_visa)
        self.assertTrue(is_valid)
        self.assertIn("Visa", message)

    def test_valid_mastercard(self):
        #Тест валидного номера MasterCard
        valid_mastercard = "5555-5555-5555-4444"
        is_valid, message = self.validator.validate_card(valid_mastercard)
        self.assertTrue(is_valid)
        self.assertIn("MasterCard", message)

    def test_invalid_card_length(self):
        #Тест номера неправильной длины
        invalid_card = "4111-1111-1111-111"
        is_valid, message = self.validator.validate_card(invalid_card)
        self.assertFalse(is_valid)
        self.assertIn("16 цифр", message)

    def test_invalid_luhn_check(self):
        #Тест номера, не проходящего проверку Луна
        invalid_luhn = "4111-1111-1111-1112"
        is_valid, message = self.validator.validate_card(invalid_luhn)
        self.assertFalse(is_valid)
        self.assertIn("Луна", message)

    def test_card_with_spaces(self):
        #Тест номера с пробелами
        card_with_spaces = "4111 1111 1111 1111"
        is_valid, message = self.validator.validate_card(card_with_spaces)
        self.assertTrue(is_valid)

    def test_card_without_separators(self):
        #Тест номера без разделителей
        card_no_separators = "4111111111111111"
        is_valid, message = self.validator.validate_card(card_no_separators)
        self.assertTrue(is_valid)

    def test_find_cards_in_text(self):
        #Тест поиска карт в тексте
        text = """
        Вот некоторые номера карт для теста:
        Visa: 4111-1111-1111-1111
        MasterCard: 5555-5555-5555-4444
        Невалидный: 4111-1111-1111-1112
        """

        cards = self.validator.find_cards_in_text(text)

        self.assertEqual(len(cards), 3)

        found_numbers = [card[0] for card in cards]
        self.assertIn("4111-1111-1111-1111", found_numbers)
        self.assertIn("5555-5555-5555-4444", found_numbers)
        self.assertIn("4111-1111-1111-1112", found_numbers)

        valid_status = {card[0]: card[1] for card in cards}
        self.assertTrue(valid_status["4111-1111-1111-1111"])
        self.assertTrue(valid_status["5555-5555-5555-4444"])
        self.assertFalse(valid_status["4111-1111-1111-1112"])

    def test_find_cards_in_file(self):
        #Тест поиска карт в файле
        test_content = "Номер карты: 4111-1111-1111-1111\nЕще номер: 5555-5555-5555-4444"

        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.txt') as f:
            f.write(test_content)
            temp_file = f.name

        try:
            cards = self.validator.find_cards_in_file(temp_file)
            self.assertEqual(len(cards), 2)

            for card, is_valid, line_num in cards:
                self.assertTrue(is_valid)
        finally:
            os.unlink(temp_file)

    def test_real_test_card_numbers(self):
        #Тест реальных тестовых номеров карт
        test_cards = [
            "4242424242424242",  # Visa
            "4000056655665556",  # Visa (debit)
            "5555555555554444",  # MasterCard
        ]

        for card in test_cards:
            is_valid, message = self.validator.validate_card(card)
            self.assertTrue(is_valid, f"Card {card} should be valid: {message}")

    def test_invalid_characters(self):
        #Тест номера с недопустимыми символами
        invalid_cards = [
            "4111-1111-1111-11a1",
            "4111.1111.1111.1111",
        ]

        for card in invalid_cards:
            is_valid, message = self.validator.validate_card(card)
            self.assertFalse(is_valid)


class TestBankCardValidatorIntegration(unittest.TestCase):

    def setUp(self):
        self.validator = BankCardValidator()

    def test_main_program_input(self):
        #Тест работы основной программы с вводом
        from bank_card_validator import main
        import sys

        # Тестируем с аргументом --input
        test_args = ["bank_card_validator.py", "--input", "4111-1111-1111-1111"]

        with redirect_stdout(io.StringIO()) as f:
            try:
                sys.argv = test_args
                main()
                output = f.getvalue()
                self.assertIn("Корректный", output)
            except SystemExit:
                pass


if __name__ == '__main__':
    # Запуск тестов
    unittest.main(verbosity=2)