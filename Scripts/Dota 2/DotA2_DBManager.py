
from pony.orm import *

import requests
from bs4 import BeautifulSoup


########################################################################################################################
#Criação do Schema do DB

db = Database("sqlite", 'botbd.db', create_db=True)


class Personagem(db.Entity):
    nome = PrimaryKey(str)
    origem = Required(str)
    clips = Set('Clip')


class Clip(db.Entity):
    id = PrimaryKey(int, auto=True)
    texto = Required(str)
    url = Required(str)
    personagem = Required(Personagem)


db.generate_mapping(create_tables=True)

########################################################################################################################
#Download e formatação da página de audios da wiki de dota 2 para extração dos audios

BASE_URL = 'http://dota2.gamepedia.com/'
API_URL = 'api.php?action=query&list=categorymembers&cmlimit=max' +  \
                                                   '&cmprop=title' + \
                                                   '&format=json' +  \
                                                   '&cmtitle=Category:'
END_URL = 'Lists_of_responses'

def fetch_response_pages():
    """Fetches all available response pages from the Dota Wiki"""
    response_pages = []
    category_json = requests.get(BASE_URL + API_URL + END_URL).json()
    for category in category_json["query"]["categorymembers"]:
        if not 'Announcer' in category["title"]: # Exclude announcer packs
            response_pages.append(BASE_URL + category["title"].replace(" ", "_"))
    return response_pages

def parse_page(page):
    """Returns a page object parsed with BeautifulSoup"""
    return BeautifulSoup(requests.get(page).text, 'html.parser')

def parse_html(html):
    """Returns a html object parsed with BeautifulSoup"""
    return BeautifulSoup(html, 'html.parser')

########################################################################################################################
#Popular o DB e funções auxiliares
@db_session
def get_id():  #pega o último id de fala adicionado
    num = Clip.get(id=max(d.id for d in Clip))
    if num is None:
        id_pos = 0
    else:
        id_pos = num.id

    print(id_pos)
    return id_pos

@db_session
def check_double(hero):
    hlist = select(p.nome for p in Personagem)
    for nome in hlist:
        if nome == hero:
            return True
        else:
            continue
    return False


@db_session
def populate_response_bd(response_pages, id_atual):
    """Popula um banco de dados previamente criado com os heróis e as falas dos heróis de dota 2
        no seguinte formato:
        table PERSONAGEM:                             table CLIP:
        nome  | origem                                id  | texto   | url  | personagem
        --------------                              --------------------------------------
        heroi1 | dota 2                               1   | 'fala1' | url  | heroi1
        heroi2 | dota 2                               2   | 'fala2' | url  | heroi1
    """
    html_strip = ['r ', 'u ', '120 ', 'Play ', '300 ', '150 ', '60 ', ' u ', ' r ', '25 ', ]   #lixo que costuma vir em algumas transcrições do audio

    #busca por heroi
    for page in response_pages:
        hero = page.split("/")[-2]
        page_es_check = page.split("/")[-1]
        if (page_es_check == 'es') or (hero == 'Responses'):
            continue

        if check_double(hero):
            continue
        print (hero)
        charac = Personagem(nome=hero, origem='dota 2')
        commit()
        num = 1

        soup = parse_page(page) # BeautifulSoup object, holding a parsed page

        #busca por fala do heroi atual
        for li_obj in soup.find_all("li"): # Return all <li> in the page
            if li_obj.a and li_obj.a.has_attr("class") and li_obj.a["class"][0] == "sm2_button":
                id_atual += 1

                response_url = li_obj.a.get('href')                 #guarda a url do audio
                li_obj.a.extract()
                response_text = li_obj.text.strip()                 #guarda o texto do audio

                #remove os lixos que vem no inicio de alguns textos
                for strip in html_strip:
                    if strip in response_text:
                       response_text = response_text.lstrip(strip)

                #se o heroi não tiver falas, cria texto padrão pra fala
                if response_text == '':
                    response_text = '{}_{}'.format(hero, num)
                    num += 1

                clip = Clip(id=id_atual, texto=response_text, url=response_url, personagem=hero)
                commit()


    return


@db_session
def main():
    print('START\n')

    PAGES = fetch_response_pages()
    ID = get_id()

    populate_response_bd(PAGES, ID)
    print('\nEND')


    #Clip.select().show()
    #Personagem.select().show()
    #delete(p for p in Clip)
    #delete(p for p in Personagem)



if __name__ == '__main__':
    main()


