from django.http import HttpResponse
from django.shortcuts import render
from datetime import date

characters = [
    {
        'id': 1,
        'name': 'Боско Даггерхэнд',
        'race': 'Человек',
        'class': 'Следопыт', 
        'description': 'Боско Даггерхэнд зовётся так, потому что он никогда не пожимает руку, если его другая рука не лежит угрожающе на рукояти кинжал в ножнах. Он держит полудикого дейнониха в качестве сторожевого животного, которым он управляет своим волшебным кольцом. Пираты кличут хищника Костяшкой, потому что у того, кто достаточно глуп, чтобы дать ему укусить руку, больше ничего не останется.',
        # 'short_description': 'Боско Даггерхэнд никогда не пожимает руку без кинжала наготове. Его сторожевой зверь — дейноних Костяшка, которого он контролирует волшебным кольцом, известен тем, что после него не остаётся костей.',
        'features': 'Кольцо влияния на животных, тактика стаи',
        'special_equipment': 'Кольцо влияния на животных',
        'skills': 'Тактика стаи',
        'hit_points': 32,
        'armor_class': 11,
        'strength': '15(+2)', 
        'dexterity': '11(+0)',
        'constitution': '14(+2)',
        'intelligence': '10(+0)',
        'wisdom': '10(+0)',
        'charisma': '11(+0)',
        'photo_url': 'http://localhost:9000/dungeonsanddragonsphotos/Brosco_Daggerhand.png' 
    },
    {
        'id': 2,
        'name': 'Бастиан Термандар',
        'race': 'Огненный дженази',
        'class': 'Заклинатель',  
        'description': 'Подобно многим в культе огня, Бастиан горит вну­тренним огнём, но его пламя питает скорее често­любие, а не желание увидеть выжженный дочиста мир. Бастиан замышляет свергнуть Вейнифер и присвоить Высекающий Искры себе. Бастиан практикует тайные искусства, причем многое о своей магии огня он узнал от самой Вей­нифер. В бою он полагается на свои заклинания: его прозвали «быстрый ожог», так как обычно он пытается нанести максимальный урон в начале схватки. Если Бастиан знает, что грядёт бой, но не может нанести упреждающий удар, он становит­ся более осторожным, вызывая стену огня, чтобы защитить себя, прежде чем использовать другие боевые заклинания.',
        # 'short_description': 'Бастиан Термандар — огненный дженази, который питает своё честолюбие внутренним огнём. Он стремится свергнуть Вейнифер и присвоить себе Высекающий Искры. Бастиан практикует тайные искусства, многое из которых он узнал от самой Вейнифер.',
        'features': 'Заклинатель 9 уровня',
        'special_equipment': 'Отсутствует',
        'skills': 'Заклинания до 5 уровня',
        'hit_points': 78,
        'armor_class': 15,
        'strength': '10(+0)',
        'dexterity': '14(+2)',
        'constitution': '16(+3)',
        'intelligence': '12(+1)',
        'wisdom': '10(+0)',
        'charisma': '18(+3)',
        'photo_url': 'http://localhost:9000/dungeonsanddragonsphotos/BastianTarmandr.png'
    },
    {
        'id': 3,
        'name': 'Дрэгонбэйт',
        'race': 'Сауриал',
        'class': 'Паладин', 
        'description': 'Дрэгонбэйт является чемпионом добра из расы сауриал, которая возникла на далёком мире, и представители которого имеют долгую жизнь. В Забытых Королевствах проживает очень мало сауриалов, и, как полагают, не существует никаких сельских сообществ в любой точке мира. Дрэгонбэйт ростом 4 фута 10 дюймов, весит 150 фунтов и имеет сухую морщинистую шкуру. Он владеет длинным мечом «Святой мститель» и носит сине-красно-белый щит. Хотя у него есть общие особенности с паладинами, Дрэгонбэйт не является членом какого-либо класса. Используя способность, известную как Шен-стейт, он может определить мировоззрение любого существа в пределах 60 футов от него.',
        # 'short_description': 'Дрэгонбэйт — чемпион добра из расы сауриал. Владеет длинным мечом «Святой мститель» и носит сине-красно-белый щит. Использует способность Шен-стейт для определения мировоззрения существ в радиусе 60 футов.',
        'features': 'Божественное здоровье, Аура сопротивления магии',
        'special_equipment': 'Длинный меч «Святой мститель», сине-красно-белый щит',
        'skills': 'Чувство мировоззрения',
        'hit_points': 120,
        'armor_class': 18,
        'strength': '18(+4)',
        'dexterity': '12(+1)',
        'constitution': '16(+3)',
        'intelligence': '10(+0)',
        'wisdom': '14(+2)',
        'charisma': '16(+3)',
        'photo_url': 'http://localhost:9000/dungeonsanddragonsphotos/DragonBait.png'
     } 
]

requests = [
    {
        'id': 1,
        'items': [1, 2, 3]
    },
    {
        'id': 2,
        'items': [1, 3]
    },
    {
        'id': 3,
        'items': [2]
    }
]

def count_characters(request_id):
    characters_in_request = []
    for req in requests:
        if req['id'] == request_id:
            for char_id in req['items']:
                for char in characters:
                    if char['id'] == char_id:
                        characters_in_request.append(char)
            break
    return len(characters_in_request)


def index(request):
    query = request.GET.get('search')
    if query:
        filtered_characters = [char for char in characters if query.lower() in char['name'].lower()]
    else:
        filtered_characters = characters
    request_id = 1
    count = count_characters(request_id)
    return render(request, 'index.html', {'characters': filtered_characters, 'count_characters': count, 'request_id': request_id})
    

def base(request):
    return render(request, 'base.html')

def detail(request, id):
    character = None
    for char in characters:
        if char['id'] == id:
            character = char
            break  
    return render(request, 'detail.html', {'character': character})

def request(request, id):
    characters_in_request = []
    for req in requests:
        if req['id'] == id:
            for char_id in req['items']:
                for char in characters:
                    if char['id'] == char_id:
                        characters_in_request.append(char)
            break
    return render(request, 'request.html', {'characters': characters_in_request})



