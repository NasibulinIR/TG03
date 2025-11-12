import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import sqlite3
import aiohttp
import logging
from config import TOKEN, WEATHER_API_KEY

bot = Bot(token=TOKEN)
dispatcher = Dispatcher()
logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

def init_db():
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      age INTEGER(4) NOT NULL,
                      grade VARCHAR(20) NOT NULL)
                   ''')
    conn.commit()
    conn.close()

init_db()

@dispatcher.message(Command('show'))
@dispatcher.message(Command('clean'))
async def handle_commands(message: Message, state: FSMContext):
    await state.clear()
    if message.text == '/show':
        await cmd_show(message)
    elif message.text == '/clean':
        await cmd_clean(message)

@dispatcher.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer('Привет, как тебя зовут?')
    await state.set_state(Form.name)

@dispatcher.message(Form.name)
async def cmd_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Сколько тебе лет?')
    await state.set_state(Form.age)

@dispatcher.message(Form.age)
async def cmd_name(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer('Из какого ты класса?')
    await state.set_state(Form.grade)

@dispatcher.message(Form.grade)
async def cmd_grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    user_data = await state.get_data()

    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO students (name, age, grade)
                          VALUES(?,?,?)''', (user_data['name'], user_data['age'], user_data['grade']))
    conn.commit()
    conn.close()

@dispatcher.message(Command('show'))
async def cmd_show(message: Message):
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM students''')
    students_list = cursor.fetchall()

    if not students_list:
        await message.answer("В базе данных пока нет студентов")
        return

    response = "Список студентов: \n\n"
    for student in students_list:
        response += f"Имя: {student[1]} | Возраст: {student[2]} | Класс {student[3]}\n"

    await message.answer(response)
    conn.close()

@dispatcher.message(Command('clean'))
async def cmd_clean(message: Message):
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students")
    conn.commit()
    conn.close()
    await message.answer("База данных успешно очищена")

async def main():
    await dispatcher.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
