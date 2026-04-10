import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

BOT_TOKEN = os.getenv("8717809394:AAFP5U65HBRkDdWF8O77S2pBNsETG87EIUU")
OWNER_ID = 8409147278

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class OrderForm(StatesGroup):
    name = State()
    phone = State()
    address = State()
    window_type = State()
    date = State()
    comment = State()

phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Отправить номер", request_contact=True)]],
    resize_keyboard=True
)

window_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Пластиковые"), KeyboardButton(text="Деревянные")],
        [KeyboardButton(text="Алюминиевые"), KeyboardButton(text="Энергосберегающие")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("🪟 Окна Большой Страны КБР\n\nКак вас зовут?")
    await state.set_state(OrderForm.name)

@dp.message(OrderForm.name, F.text)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(OrderForm.phone)
    await message.answer("📞 Номер телефона:", reply_markup=phone_keyboard)

@dp.message(OrderForm.phone, F.contact | F.text)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text.strip()
    await state.update_data(phone=phone)
    await state.set_state(OrderForm.address)
    await message.answer("📍 Адрес (город, улица, дом):", reply_markup=ReplyKeyboardRemove())

@dp.message(OrderForm.address, F.text)
async def get_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text.strip())
    await state.set_state(OrderForm.window_type)
    await message.answer("🪟 Тип окон:", reply_markup=window_keyboard)

@dp.message(OrderForm.window_type, F.text)
async def get_window_type(message: types.Message, state: FSMContext):
    await state.update_data(window_type=message.text.strip())
    await state.set_state(OrderForm.date)
    await message.answer("📅 Желаемая дата замера:", reply_markup=ReplyKeyboardRemove())

@dp.message(OrderForm.date, F.text)
async def get_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text.strip())
    await state.set_state(OrderForm.comment)
    await message.answer("📝 Пожелания (или «Нет»):")

@dp.message(OrderForm.comment, F.text)
async def get_comment(message: types.Message, state: FSMContext):
    comment = message.text.strip()
    if comment.lower() == "нет":
        comment = "—"
    data = await state.get_data()
    order_text = (
        f"🪟 НОВЫЙ ЗАКАЗ\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {data['address']}\n"
        f"Тип окон: {data['window_type']}\n"
        f"Дата замера: {data['date']}\n"
        f"Комментарий: {comment}\n"
        f"Клиент: @{message.from_user.username or 'нет'} ({message.from_user.id})"
    )
    await bot.send_message(OWNER_ID, order_text)
    await message.answer("✅ Заявка принята! Специалист свяжется с вами.\n\n/start – новый заказ", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@dp.message()
async def unknown(message: types.Message):
    if message.text != "/start":
        await message.answer("Нажмите /start, чтобы оформить заказ.")

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
