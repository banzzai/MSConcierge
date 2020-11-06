import discord, requests, discord_token, random
from discord.ext import commands
from bs4 import BeautifulSoup
from discord_token import TOKEN
from constants import RED, GREEN, BLUE, LIGHT, DARK

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
async def berry(ctx):
    await superbias(ctx)

@client.command()
async def name(ctx, *, number):
    pageStart = int(number) - int(number)%100 + 1
    pageEnd = int(number) - int(number)%100 + 100
    URL = f'https://monster-strike-enjp.fandom.com/wiki/Monsterpedia_({pageStart}-{pageEnd})'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    image = soup.select(f'img[alt$="{number}.jpg"]')[0]
    try:
        imgSrc = image['data-src']
    except KeyError:
        imgSrc = image['src']
    link = image.find_parent("a")['href']
    await ctx.send(f'{imgSrc}')
    await ctx.send(f'https://monster-strike-enjp.fandom.com{link}')

@client.command()
async def debug(ctx, *, number, allForms=True):
    await evo(ctx=ctx, number=number, silent=True)

@client.command()
async def yolo(ctx):
    number = random.randrange(192, 5164)
    await name(ctx, number=number)

@client.command()
async def evo(ctx, *, number, allForms=True, silent=False):
    pageStart = int(number) - int(number)%100 + 1
    pageEnd = int(number) - int(number)%100 + 100
    URL = f'https://monster-strike-enjp.fandom.com/wiki/Monsterpedia_({pageStart}-{pageEnd})'

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    image = soup.select(f'img[alt$="{number}.jpg"]')[0]
    
    try:
        imgSrc = image['data-src']
    except KeyError:
        imgSrc = image['src']

    link = image.find_parent("a")['href']

    detailpage = requests.get(f'https://monster-strike-enjp.fandom.com{link}')
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
                    mskaistuff = cells[1].get_text().split("Condition: ")
            elif i > 1 and len(cells) > 0:
                if HpIndex == -1:
                    HpIndex = i

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