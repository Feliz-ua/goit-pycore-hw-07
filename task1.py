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
            raise ValueError("Невірний формат дати народження. Використовуйте формат DD.MM.YYYY")

# Клас для зберігання номера телефону із перевіркою (10 цифр)
class Phone(Field):
    def __init__(self, value):
        if not (isinstance(value, str) and value.isdigit() and len(value) == 10):
            raise ValueError("Номер телефону повинен складатися з 10 цифр.")
        super().__init__(value)
        
# Клас для зберігання інформації про контакт: ім'я, телефони, дата народження
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # Функція додавання номеру телефону до списку телефонів контакту
    def add_phone(self, phone):
        self.phones.append(Phone(phone))
    
    # Функція додавання дати народження, якщо вона ще не встановлена, інакше викликає помилку
    def add_birthday(self, birthday_str):
        if self.birthday is None:
            self.birthday = Birthday(birthday_str)
        else:
            raise ValueError("День народження вже встановлено для цього контакту")
        
    # Функція обчислення кількості днів до наступного дня народження
    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = date.today()
        # Заміна року на поточний для отримання дати наступного дня народження
        next_birthday = self.birthday.value.replace(year=today.year)
        # Якщо в цьому році день народження всже минув, додається ще 1 рік (тобто переносимо дату привітання на наступний рік)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    # Функція видалення вказаного номеру телефону зі списку, якщо такий номер телефону існує
    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                break

    # Функція зміни старого номеру телефона на новий
    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                break

    # Функція пошуку номеру телефону у списку телефонів контакту
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    # Функція виведення імені та номеру телефону контакту
    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        return f"Ім'я абонента: {self.name.value}, телефон: {phones_str}"        
    
# Клас для зберігання та управління записами контактів 
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
            return "Контакт не знайдено, перевірте ім'я."
        # Обробка помилки, коли недостатньо аршументів для імені та телефону
        except ValueError:
            return "Дайте мені ім'я та номер телефону, будь ласка."
        # Обробка помилки, коли відсутнє ім'я для пошуку
        except IndexError:
            return "Введіть ім'я користувача."
    return inner

def parse_input(user_input):
    
    parts =user_input.strip().split()
    if not parts:
        return "", []
    cmd = parts[0].lower ()
    
    if cmd == "change":
        if len(parts)<4:
            return cmd, []
        return cmd, parts[1:4]
    
    return cmd, parts[1:] 

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
    return "Контакт доданий"

@input_error
def change_contact(args, book):
    # якщо кількість аргументів не дорівнює 3 (ім'я, старий номер телефону, новий номер телефону) - 
    # буде повідомлення про невірну кількість аргументів для зміни номеру
    if len (args) !=3:
        return "Помилка: команда «change» вимагає 3 аргументи: ім'я, старий телефон, новий телефон."
    # Змінюємо номер телефону у існуючого контакту
    name, old_phone, new_phone = args
    if name not in book:
        # якщо немає такого контакту - виняток
        raise KeyError  
    book[name] = phone
    return "Контактна інформація змінена."

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
    # Додаємо дату народження для контакту.
    name, bday = args
    record = book.get(name)
    # Якщо контакту з таким іменем не існує, видає помилку.
    if not record:
        raise KeyError ("Контакт не знайдено")
    record.add_birthday(bday)
    return "Додано день народження."

@input_error
def show_birthday(args, book):
    # Виводимо дату народження заданого контакту.
    name = args[0]
    record = book.get(name)
    # Якщо контакт не знайдений — видає помилку.
    if not record:
        raise KeyError("Контакт не знайдено")
    if not record.birthday:
        return "День народження для цього контакту не встановлено."
    return record.birthday.value.strftime("%d.%m.%Y")

def birthdays (args, book):
    # Виводить список майбутніх дат народжень (привітань) для всіх контактів за наступний тиждень.
    result = book.get_upcoming_birthdays()
    # Якщо майбутніх дат за наступний тиждень не буде — повертає відповідне повідомлення.
    if not result:
        return "У наступному тижні немає запланованих днів народження."
    return "\n".join([f"{r['name']} дата привітання {r['congratulation_date']}" for r in result])


def show_all(book):
    # Показуємо всі контакти у списку
    if not book:
        return "Контакт не знайдено."
    result = []
    for record in book.values():
        result.append(str(record))
    return "\n".join(result)


def main():
    # Основна функція - цикл прийому команд і виклик функцій
    # словник для збереження контактів
    book = AddressBook ()  
    print("Ласкаво просимо до бота-помічника!")
    while True:
        user_input = input("Введіть команду: ").strip()
        if not user_input:
            # Якщо користувач не ввів команду
            print("Невірна команда.")
            continue
        # Обробка введеною команди
        command, args = parse_input(user_input)

        # Обробка команд бота
        if command in ["close", "exit"]:
            print("До побачення!")
            break
        elif command == "hello":
            print("Чим можу допомогти?")
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
            print("Невірна команда.")

if __name__ == "__main__":
    main()
