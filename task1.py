from datetime import datetime, date, timedelta
from collections import UserDict

# Базовий клас для будь-якого поля запису (ім'я, телефон тощо)
class Field:
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return str(self.value)

# Клас для зберігання імені контакту 
class Name (Field):
    pass

# Клас для зберігання дати народження
class Birthday(Field):
    def __init__(self, value):
        try:
            # Перевірка та конвертація у дату
            birthday_date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(birthday_date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

# Клас для зберігання номера телефону із валідацією (10 цифр)
class Phone(Field):
    def __init__(self, value):
        if not (isinstance(value, str) and value.isdigit() and len(value) == 10):
            raise ValueError("Phone must be a string of 10 digits.")
        super().__init__(value)
        
# Клас для зберігання інформації про контакт: ім'я, список телефонів та дату народження
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))
    
    def add_birthday(self, birthday_str):
        if self.birthday is None:
            self.birthday = Birthday(birthday_str)
        else:
            raise ValueError("Birthday already set for this contact")
        
    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = date.today()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_str}"        
    
# Клас для зберігання та управління записами
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            
    def get_upcoming_birthdays(self, days=7):
        today = date.today()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                bday = record.birthday.value
                birthday_this_year = bday.replace(year=today.year)
                # Якщо день народження вже був у цьому році — шукаємо наступний
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until = (birthday_this_year - today).days
                if 0 <= days_until <= days:
                    congrats_date = birthday_this_year
                    # Переносимо привітання на понеділок, якщо дата випадає на вихідний
                    if congrats_date.weekday() == 5:  # Субота
                        congrats_date += timedelta(days=2)
                    elif congrats_date.weekday() == 6:  # Неділя
                        congrats_date += timedelta(days=1)

                    upcoming.append({
                        "name": record.name.value,
                        "congratulation_date": congrats_date.strftime("%d.%m.%Y")
                    })
        return upcoming

# Створюємо декоратор для обробки помилок вводу
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        # Обробка помилки, коли контакт не знайдено
        except KeyError:
            return "Contact not found, please check the name."
        # Обробка помилки, коли недостатньо аршументів для імені та телефону
        except ValueError:
            return "Give me name and phone please."
        # Обробка помилки, коли відсутнє ім'я для пошуку
        except IndexError:
            return "Enter user name."
    return inner

def parse_input(user_input):
    # Розбиваємо рядок введення на команду та аргументи
    cmd, *args = user_input.split()
    # Приводимо команду до нижнього регістру для уніфікації
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_contact(args, book):
    # Додаємо контакт: потрібно два аргументи - ім'я та телефон
    # якщо аргументів менше 2 - буде ValueError
    name, phone = args  
    if name in book:
        book[name].add_phone(phone)
    else:
        record = Record(name)
        record.add_phone(phone)
        book[name] = record
    return "Contact added."

@input_error
def change_contact(args, book):
    # Змінюємо номер телефону у існуючого контакту
    name, phone = args
    if name not in book:
        # якщо немає такого контакту - виняток
        raise KeyError  
    book[name] = phone
    return "Contact updated."

@input_error
def show_phone(args, book):
    # Показуємо номер телефону по імені
    # якщо args пустий — буде IndexError
    name = args[0]  
    if name not in book:
        # якщо контакт не знайдено - виняток
        raise KeyError  
    return book[name]

@input_error
def add_birthday(args, book):
    name, bday = args
    record = book.get(name)
    if not record:
        raise KeyError ("Contact not found")
    record.add_birthday(bday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.get(name)
    if not record:
        raise KeyError("Contact not found")
    if not record.birthday:
        return "Birthday not set for this contact."
    return record.birthday.value.strftime("%d.%m.%Y")

def birthdays (args, book):
    result = book.get_upcoming_birthdays()
    if not result:
        return "No upcoming birthdays in the next week."
    return "\n".join([f"{r['name']} congratulation date {r['congratulation_date']}" for r in result])


def show_all(book):
    # Показуємо всі контакти у списку
    if not book:
        return "Contact list is empty."
    result = []
    for record in book.values():
        result.append(str(record))
    return "\n".join(result)


def main():
    # Основна функція - цикл прийому команд і виклик функцій
    # словник для збереження контактів
    book = AddressBook ()  
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            # Якщо користувач не ввів команду
            print("Invalid command.")
            continue
        # Обробка введеною команди
        command, args = parse_input(user_input)

        # Обробка команд бота
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book)) 
        elif command == "show-birthday":
            print(show_birthday(args, book))    
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
