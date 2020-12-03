import discord, requests, discord_token, random
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
async def berry(ctx):
    await superbias(ctx)

def isInRange(number, soup):
    #This should extract a link to the last pedia page, from the top menu (second) tab (first) dropdown link
    lastPageLink = soup.select(f'ul[class$="wds-list wds-is-linked wds-has-bolded-items"]')[1].find("a")['href']
    lastPediaNumer = int(lastPageLink[-5:-1])
    
    if (int(number) > lastPediaNumer):
        return False
    else:
        return True

async def getUnitPage(number, JPFallback=False):
    pageStart = int(number) - int(number)%100 + 1
    pageEnd = int(number) - int(number)%100 + 100
    URL = f'https://monster-strike-enjp.fandom.com/wiki/Monsterpedia_({pageStart}-{pageEnd})'
    
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    if not isInRange(number, soup):
        return None

    image = soup.select(f'img[alt$="{number}.jpg"]')[0]

    link = image.find_parent("a")
    linkHref = link['href']
    newLink = link.find_next_sibling()
    #There is a link, but it's to create the wiki entry, so no result for our purpose
    if (str(newLink).find(CREATE_WIKI_PAGE_HREF) != -1):
        pageUrl = f'https://monster-strike-enjp.fandom.com{linkHref}'

        try:
            #Some links go nowhere so we're testing this one
            detailPage = requests.get(pageUrl)
        except:
            detailPage = None

    #At this stage if detailPage is Empty we need to check JP wiki if desired
    if detailPage is None and JPFallback:
        pageUrl = f'https://monst.appbank.net/monster/{number}.html'
        detailPage = requests.get(pageUrl)

        #Currently there is one image in the 404 page and it has 404 in its name. Hopefully that's a semi-reliable criteria
        img = detailPage.find("img")['src']
        print(f"img in jp page {img}")

    return detailPage

@client.command()
async def name(ctx, *, number, needHatcher=False):
    unitPage = await getUnitPage(number)
    if (unitPage is not None):
        await ctx.send(f'{unitPage}')
    else:
        await ctx.send(f'https://monst.appbank.net/monster/{number}.html')

@client.command()
async def debug(ctx, *, number, allForms=True):
    await evo(ctx=ctx, number=number, silent=True)

async def isHatcher(number):
    detailpage = await getUnitPage(number)
    
    if (detailpage is not None):
        soup = BeautifulSoup(detailpage.content, 'html.parser')

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
    number = random.randrange(192, lastKnownUnit)
    while (hatcherFound is False):
        number = random.randrange(192, lastKnownUnit)
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

async def noWiki(ctx, number):
    await ctx.send("Wiki doesn't have it :(")
    await ctx.send("Here's a link to a different database(jp)")
    await ctx.send(f'https://monst.appbank.net/monster/{number}.html')

@client.command()
async def evo(ctx, *, number, allForms=True, silent=False):
    pageStart = int(number) - int(number)%100 + 1
    pageEnd = int(number) - int(number)%100 + 100
    URL = f'https://monster-strike-enjp.fandom.com/wiki/Monsterpedia_({pageStart}-{pageEnd})'

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    #Why you gotta be asking for a monster number that is higher than the most recent in the wiki?
    if not isInRange(number, soup):
        await noWiki(ctx, number)
    
    #We are looking for an image with the monster number, and it's associated href (the wiki page)
    imageHTML = soup.select(f'img[alt$="{number}.jpg"]')
    
    #It's possible there is no entry at all, even though we are on the right page for this monster (ex: 214)
    if (len(imageHTML) > 0):
        image = imageHTML[0]
    else:
        #No entry for that number
        await noWiki(ctx, number)
        exit

    try:
        imgSrc = image['data-src']
    except KeyError:
        imgSrc = image['src']

    link = image.find_parent("a")['href']

    try:
        detailpage = requests.get(f'https://monster-strike-enjp.fandom.com{link}')
    except:
        #There is nothing behind the wiki link
        await noWiki(ctx, number)
        exit

    soup = BeautifulSoup(detailpage.content, 'html.parser')
    
    forms = soup.select(f'table[border$="1"]')
    
    name = soup.select(f'h1[id$="firstHeading"]')[0].get_text()
    realNames = [name]
    
    #names = soup.select(f'span[class$="mw-headline"]')
    #for nameline in names:
    #    if nameline.get_text().find("(") >= 0:
    #        realNames.append(nameline.get_text())

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
                    print(msObtain)

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
        embedVar = discord.Embed(title=f"{realNames[formIndex]}", description=f"{msrarity} {msclass}", color=msColor)
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
        embedVar.set_author(name=f"#{msNumber}", icon_url=formImage)

        #Main thumbnail
        msFullImage = form.find_previous_sibling("div").find("a")['href']
        embedVar.set_thumbnail(
            url=msFullImage
        )

        if silent == False:
            await ctx.send(embed=embedVar)
        formIndex += 1

client.run(TOKEN)