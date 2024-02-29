from aiogram import Router, filters, types
from aiogram.fsm.context import FSMContext
from aiogram_ui import KB, B, OpenURL

from database import SessionMakerType

router = Router()


@router.message(filters.state.StateFilter(None))
async def menu_layout(
    message: types.Message,
    state: FSMContext,
    sessionmaker: SessionMakerType,
):
    await state.clear()
    return await message.answer("Hello", reply_markup=KB(B("Yandex", OpenURL('https://ya.ru'))))
