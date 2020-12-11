import discord, requests, discord_token, random
from urllib.parse import unquote
from discord.ext import commands
from bs4 import BeautifulSoup
from discord_token import TOKEN
from constants import *

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('MSC is here!!')

@client.command()
async def tower(ctx, *, floor):
    await ctx.send(f'https://monster-strike-enjp.fandom.com/wiki/Tower_of_Champions_-_{floor}F')

@client.command()
async def unit(ctx, *, number):
    await evo(ctx, number=number, allForms=False)

@client.command()
async def superbias(ctx):
    await ctx.send('https://cdn.discordapp.com/attachments/771907951023357972/774011193001377812/unknown.png')

@client.command()
async def supertype(ctx):
    await superbias(ctx)

@client.command()
async def berries(ctx):
    await ctx.send('https://cdn.discordapp.com/attachments/741188547251273799/774004284927901746/berries2.png')

@client.command()
async def collab(ctx):
    await ctx.send('https://twitter.com/EngMonst/status/1327139304204886019/photo/1')

@client.command()
async def div(ctx):
    await ctx.send('https://cdn.discordapp.com/attachments/771907951023357972/786648082141413417/unknown.png')

@client.command()
async def berry(ctx):
    await superbias(ctx)

@client.command()
async def msnews(ctx):
    #Not in the mood to setup youtube apis, and youtube itself seems pretty parse-resistant, so I am going through a google search.
    youtubeSearch = 'https://www.google.com/search?q=%E3%83%A2%E3%83%B3%E3%82%B9%E3%83%88%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9+site:youtube.com&tbs=qdr:w'
    youtube = requests.get(youtubeSearch)
    soup = BeautifulSoup(youtube.content, 'html.parser')
    for link in soup.find_all('a'):
        href = unquote(link['href'])
        youtubePos = href.find('https://www.youtube.com/watch')
        if (youtubePos != -1):
            andPos = href.find('&')
            await ctx.send(f'{href[youtubePos:andPos]}')
            return

@client.command()
async def pedia(ctx):
    baseUrl = 'https://xn--eckwa2aa3a9c8j8bve9d.gamewith.jp/db/monster/index'
    postData = {'attribute_type_id': 1, 'hit_type_id': 1, 'rarity_type_id': 3, 'take_type_id': 1, 'ability_id': {10, 119, 141, 9, 123, 155}}
    #, 'ability_id': {10, 119, 141}, 'ability_id': {9, 123, 155}

    MSpedia = requests.post(baseUrl, data = postData)
    soup = BeautifulSoup(MSpedia.content, 'html.parser')
    print(soup)

    await ctx.send(f'OK')

def isInRange(number, requests):
    page = requests.get(WIKI_PEDIA_PAGE)
    soup = BeautifulSoup(page.content, 'html.parser')

    linkTable = soup.select(f'table[class$="article-table"]')
    links = linkTable[0].find_all('a')

    lastPediaNumer = int(links[-1].get_text().split("-")[1])

    if (int(number) > lastPediaNumer):
        return False
    else:
        return True

@client.command()
async def page(ctx, number):
    page = await getUnitPage(number, True)
    await ctx.send(f'wiki: {page[URL_FIELD]}')

async def getUnitPage(number, JPFallback=False):
    
    returnHTML = dict()
    
    #Empty string means we haven't looked for the wiki page html, "None" is when we found there wasn't any
    returnHTML[SOUP_FIELD] = ""
    #No url for the monster, by default
    returnHTML[URL_FIELD] = URL_VALUE_NO_URL
    returnHTML[SUCCESS_FIELD] = False
    
    #Why you gotta be asking for a monster number that is higher than the most recent in the wiki?
    if not isInRange(number, requests):
        returnHTML[SOUP_FIELD] = None
        returnHTML[URL_FIELD] = URL_VALUE_NO_URL
        return returnHTML

    pageStart = int(number) - int(number)%100 + 1
    pageEnd = int(number) - int(number)%100 + 100
    mainPage = f'https://monster-strike-enjp.fandom.com/wiki/Monsterpedia_({pageStart}-{pageEnd})'

    page = requests.get(mainPage)
    soup = BeautifulSoup(page.content, 'html.parser')

    #We are looking for an image with the monster number, and it's associated href (the wiki page)
    imageHTML = soup.select(f'img[alt$="{number}.jpg"]')
    
    #It's possible there is no entry at all, even though we are on the right page for this monster (ex: 214)
    if (len(imageHTML) > 0):
        image = imageHTML[0]
    else:
        #No entry for that number
        returnHTML[SOUP_FIELD] = None

    if (returnHTML[SOUP_FIELD] is not None):
        link = image.find_parent("a")
        linkHref = link['href']
        newLink = link.find_next_sibling()
        #There is a link, but it's to create the wiki entry, so no result for our purpose
        if (str(newLink).find(CREATE_WIKI_PAGE_HREF) == -1):
            returnHTML[URL_FIELD] = f'https://monster-strike-enjp.fandom.com{linkHref}'
            
            #Some links go nowhere so we're testing this one
            returnHTML[SOUP_FIELD] = requests.get(returnHTML[URL_FIELD])
            if (returnHTML[SOUP_FIELD].status_code >= 400):
                returnHTML[SOUP_FIELD] = None
            else:
                #We ran out of ways to fail. This time we got a wiki page!!
                returnHTML[SUCCESS_FIELD] = True
        else:
            returnHTML[SOUP_FIELD] = None
            
    #At this stage if detailPage is Empty we need to check JP wiki if desired
    if returnHTML[SOUP_FIELD] is None and JPFallback:
        returnHTML[URL_FIELD] = f'https://monst.appbank.net/monster/{number}.html'
        returnHTML[SOUP_FIELD] = requests.get(returnHTML[URL_FIELD])
        
        if (returnHTML[SOUP_FIELD].status_code >= 400):
            returnHTML[SOUP_FIELD] = None

    #Let's reset the url value if all failed, before returning no result
    if (returnHTML[SOUP_FIELD] == None):
        returnHTML[URL_FIELD] = URL_VALUE_NO_URL

    return returnHTML

@client.command()
async def name(ctx, *, number, needHatcher=False):
    unitPage = await getUnitPage(number, True)
    if (unitPage[SOUP_FIELD] is not None):
        await ctx.send(f'{unitPage[URL_FIELD]}')
    else:
        await noWiki(ctx, unitPage[URL_FIELD])

@client.command()
async def debug(ctx, *, number, allForms=True):
    await evo(ctx=ctx, number=number, silent=True)

async def isHatcher(number):
    detailpage = await getUnitPage(number)
    
    if (detailpage[SOUP_FIELD] is not None):
        soup = BeautifulSoup(detailpage[SOUP_FIELD].content, 'html.parser')

        forms = soup.select(f'table[border$="1"]')
    
        lines = forms[0].select('tr')

        cells = lines[5].select('td')
        if len(cells) == 0:
            cells = lines[6].select('td')

        msObtain = parseObtain(str(cells[1]))
        return msObtain is not UNKNOWN
    else:
        return False

@client.command()
async def yolo(ctx):
    lastKnownUnit = 5164
    hatcherFound = False
    number = random.randrange(FIRST_HATCHER_MONSTER, lastKnownUnit)
    while (hatcherFound is False):
        number = random.randrange(FIRST_HATCHER_MONSTER, lastKnownUnit)
        hatcherFound = await isHatcher(number)
    await name(ctx, number=number, needHatcher=True)

def parseObtain(obtainHTML):
    if obtainHTML.find(MAIN_HATCHER_SEARCH) != -1:
        return MAIN_HATCHER
    elif obtainHTML.find(LEGENDS_HATCHER_SEARCH) != -1:
        return LEGENDS_HATCHER
    elif obtainHTML.find(GUARDIANS_HATCHER_SEARCH) != -1:
        return GUARDIANS_HATCHER
    elif obtainHTML.find(RED_STARS_SEARCH) != -1:
        return RED_STARS_HATCHER
    elif obtainHTML.find(AQUA_BANQUET_SEARCH) != -1:
        return AQUA_BANQUET_HATCHER
    elif obtainHTML.find(GREEN_FANTASY_SEARCH) != -1:
        return GREEN_FANTASY_HATCHER
    elif obtainHTML.find(STARLIGHT_MIRAGE_SEARCH) != -1:
        return STARLIGHT_MIRAGE_HATCHER
    elif obtainHTML.find(MIDNIGHT_PARTY_SEARCH) != -1:
        return MIDNIGHT_PARTY_HATCHER
    elif obtainHTML.find(MONSTER_DX_SEARCH) != -1:
        return MONSTER_DX_HATCHER
    return UNKNOWN

async def noWiki(ctx, url):
    if (url is not None):
        await ctx.send("Wiki doesn't have it :(")
        await ctx.send("Here's a link to a different database:")
        await ctx.send(f'{url}')
    else:
        await ctx.send("This unit can't be found in the game anymore.")

@client.command()
async def evo(ctx, *, number, allForms=True, silent=False):
    unitPage = await getUnitPage(number, True)
    
    #Why you gotta be asking for a monster number that is higher than the most recent in the wiki?
    if (unitPage[SUCCESS_FIELD] is False):
        print('no wiki exit')
        await noWiki(ctx, unitPage[URL_FIELD])
        exit
    
    detailpage = unitPage[SOUP_FIELD]
    soup = BeautifulSoup(detailpage.content, 'html.parser')
    forms = soup.select(f'table[border$="1"]')
    
    name = soup.select(f'h1[id$="firstHeading"]')[0].get_text()
    realNames = [name]

    formIndex = 0
    for form in forms:
        #Find form name by going up the tree until first 
        if formIndex > 0:
            titleSibling = form.find_previous_sibling("h2")
            if titleSibling is not None:
                realNames.append(titleSibling.get_text())
            else:
                titleSibling = form.parent.parent.find_previous_sibling("h2")
                if titleSibling is not None:
                    realNames.append(titleSibling.get_text())

        lines = form.select('tr')
        mskai = False
        msSub = False
        msCellInfos = []
        i = 1
        HpIndex = -1
        for line in lines:
            cells = line.select('td')
            if i == 1:
                msNumber = int(cells[2].get_text())
                if (allForms == False) and (msNumber != int(number)):
                    break
            elif i == 2:
                msrarity = cells[3].get_text().strip()
                msColorIcon = cells[1].find('a')['href']
                msColor = LIGHT
                if msColorIcon.find("DarkIcon") != -1:
                    msColor = DARK
                elif msColorIcon.find("FireIcon") != -1:
                    msColor = RED
                elif msColorIcon.find("WoodIcon") != -1:
                    msColor = GREEN
                elif msColorIcon.find("WaterIcon") != -1:
                    msColor = BLUE

                msclass = cells[0].get_text()
            elif i == 3:
                msBubbleCell = cells[0].find('a')['href']
                mssling = cells[1].get_text()
                msbias = cells[3].get_text().strip()
            elif i == 4:
                msAbility = cells[0].get_text()
                msGauge = cells[1].get_text()
            elif i == 5:
                if len(cells) > 0:
                    mskai = True
                    name = name + " Kai"
                    mskaistuff = cells[1].get_text('|').split("|")
            elif i > 1 and len(cells) > 0:
                if HpIndex == -1:
                    HpIndex = i
                    #The HP line contains the "Obtain" field
                    msObtain = parseObtain(str(cells[1]))

                if i < HpIndex + 3:
                    msCellInfos.append(cells[0].select('b')[0].get_text())
                elif i == HpIndex + 3:
                    #SS
                    strikeSentences = cells[0].get_text().split("Turns")
                    strikePretty = strikeSentences[0] + "Turns. " + strikeSentences[1]
                    msCellInfos.append(strikePretty)
                elif i == HpIndex + 4:
                    #Bump
                    msCellInfos.append(cells[0].get_text().replace(")", "). "))
                elif i == HpIndex + 5 and cells[0].get_text().find("To") == -1:
                    #Sub
                    msSub = True
                    msCellInfos.append(cells[1].get_text().replace(")", "). "))

            i += 1
        
        if (allForms == False) and (msNumber != int(number)):
            continue
        embedVar = discord.Embed(title=f"{unitPage[URL_FIELD]}", description=f"{msrarity} {msclass}", color=msColor)
        embedVar.add_field(name=f"{mssling}", value=f"{msbias} type", inline=False)

        embedVar.add_field(name=f"Ability: {msAbility}", value=f"Gauge: {msGauge}", inline=False)
        if mskai:
            embedVar.add_field(name=f"Connect: {mskaistuff[0]}", value=f"{mskaistuff[1]}", inline=False)

        embedVar.add_field(name=f"HP", value=f"{msCellInfos[0]}", inline=True)
        embedVar.add_field(name=f"ATK", value=f"{msCellInfos[1]}", inline=True)
        embedVar.add_field(name=f"SPD", value=f"{msCellInfos[2]}", inline=True)

        embedVar.add_field(name=f"SS", value=f"{msCellInfos[3]}", inline=False)
        embedVar.add_field(name=f"Bump", value=f"{msCellInfos[4]}", inline=False)
        if msSub:
            embedVar.add_field(name=f"Sub", value=f"{msCellInfos[5]}", inline=False)

        #Author (1st line) thumbnail and title
        try:
            formImage = form.find("img")['data-src']
        except KeyError:
            formImage = form.find("img")['src']
        #Bubble image not currently used but that might very well change
        #if (msBubbleCell.find("Special:Upload") != -1):
        #    msBubbleCell = formImage
        embedVar.set_author(name=f"#{msNumber}: {realNames[formIndex]}", icon_url=formImage)

        #Main thumbnail
        msFullImage = form.find_previous_sibling("div").find("a")['href']
        embedVar.set_thumbnail(
            url=msFullImage
        )

        if silent == False:
            await ctx.send(embed=embedVar)
        formIndex += 1

client.run(TOKEN)