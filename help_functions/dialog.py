import pprint
import requests
import os
from pathlib import Path
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import User, CallbackQuery, Message, ContentType
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Row, ScrollingGroup, Select
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.media import DynamicMedia

from help_functions.settings import SetEnv


setting = SetEnv()

token = setting.str_token



def get_products(token):
    url = 'http://localhost:1337/api/products'
    header = {
        'Authorization': f'Bearer {token}',
        }
    response = requests.get(url, headers=header)
    products_data = response.json()
    products_info = products_data['data']

    products = [(product['attributes']['title'], str(product['id'])) for product in products_info]

    return products


def get_info(token, id):
    url = f'http://localhost:1337/api/products/{id}'
    payload = {'populate': '*'}
    header = {
        'Authorization': f'Bearer {token}',
        }

    response = requests.get(url, headers=header, params=payload)
    products_data = response.json()
    products_info = products_data['data']['attributes']
    product_img = products_info['image']['data']['attributes']['formats']['small']
    # pprint.pprint(product_img)
    product = [products_info['title'], products_info['price'], products_info['description'], product_img['url']]
    return product


class FishSG(StatesGroup):
    start = State()
    select = State()


#геттеры
async def get_data(event_from_user: User, **kwargs):
    products_list = get_products(token=token)
    
    return {
        "products": products_list,
        'name': event_from_user.username,
    }


async def product_selection(dialog_manager: DialogManager, **kwargs):
    print(dialog_manager.dialog_data['id'])
    fish = get_info(token=token, id=dialog_manager.dialog_data['id'])
    # img_url = f'http://localhost:1337{fish[3]}'
    # print(img_url)
    # image = MediaAttachment(ContentType.PHOTO, url=img_url)
    return {
        'title': fish[0],
        'price': fish[1],
        'description': fish[2],
        # 'photo' : image,
    }
    


    
# #хендлеры
async def go_next(callback: CallbackQuery, 
                            widget: Select, 
                            dialog_manager: DialogManager, 
                            item_id: str):
    dialog_manager.dialog_data['id'] = item_id
    await dialog_manager.next()
    

async def go_back(callback: CallbackQuery, 
                  button: Button, 
                  dialog_manager: DialogManager):
    await dialog_manager.back()


async def buy_fish(callback: CallbackQuery, 
                   button: Button, 
                   dialog_manager: DialogManager):
    pass

start_dialog = Dialog(
    Window(
        Format('{name}, пожалуйста, выбирай!'),
        ScrollingGroup(
            Select(
                Format('{item[0]}'),
                id='choose_fish',
                item_id_getter=lambda x: x[1],
                items='products',
                on_click=go_next,
            ),
            id='fish',
            width=1,
            height=2,
        ),
        getter=get_data,
        state=FishSG.start,
    ),
    Window(
        # DynamicMedia('photo'),
        Format('{title} ({price}руб за кг)\n{description}'),
        Row(
            Button(
                text=Const('Назад'),
                id='back',
                on_click=go_back,
            ),
            Button(
                text=Const('Купить'),
                id='buy',
                on_click=buy_fish,
            ),
        ),
        getter=product_selection,
        state=FishSG.select,
    )
)