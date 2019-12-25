import xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, os, urllib, CommonFunctions, re, json, file_downloader

common = CommonFunctions
common.plugin = "Emasti Viewer-1.0"
common.dbg = True # Default
common.dbglevel = 3 # Default
common.USERAGENT = u"Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"

EMASTI_BASE_URL = "http://www.emasti.pk/"
DMASTI_BASE_URL = "http://dmasti.pk/"
thisPlugin = int(sys.argv[1])
addonPath = xbmcaddon.Addon().getAddonInfo("path")

def makeLink(params, baseUrl=sys.argv[0]):
    return "%s?%s" % (
    baseUrl, urllib.urlencode(dict([k.encode('utf-8'), unicode(v).encode('utf-8')] for k, v in params.items())))


def setViewMode():
    skin_used = xbmc.getSkinDir()
    if skin_used == 'skin.confluence':
        xbmc.executebuiltin('Container.SetViewMode(500)') # "Thumbnail" view
    elif skin_used == 'skin.aeon.nox':
        xbmc.executebuiltin('Container.SetViewMode(512)') # "Info-wall" view. 

def getScriptPath():
    return "special://home/addons/plugin.aa.emasti/file_downloader.py"
    
def addListing(arr, isVideo = False):
    global thisPlugin
    scriptPath = getScriptPath()
    down_folder = xbmcplugin.getSetting(thisPlugin, "down_folder")
    for p in arr:
        name = common.makeAscii(p['name'])
        listItem = xbmcgui.ListItem(name)
        
        if "thumb" in p:
            listItem.setThumbnailImage(common.makeAscii(p['thumb']))
            
        if isVideo == True and "video" in p:
            aired = None if "released" not in p else p["released"]
            duration = None if "duration" not in p else p["duration"]
            rating = None if "rating" not in p else p["rating"]
            stars = "" if "stars" not in p else p["stars"]
            desc = None if "desc" not in p else p["desc"]
            isDtubeVideo = "isDtubeVideo" in p and p["isDtubeVideo"] == True
            
            if duration is not None:
                duration = duration * 60
            
            infoLabels = {"Rating": rating, "Cast": stars.split(","), "Plot": desc,
                "Duration": duration, "Aired": aired}
            listItem.setInfo("video", infoLabels)
            
            params = {"isDtubeVideo": isDtubeVideo, "videoPageUrl": p["video"]}
            link = makeLink(params)
            
            params["dest"] = down_folder
            script = "XBMC.RunScript(" + scriptPath + ", " + str(thisPlugin) + ", " + makeLink(params, "") + ")"
            listItem.addContextMenuItems([('Download', script,)])
        else:
            link = makeLink(p)
        hasChildren = "hasChildren" in p and p["hasChildren"] == True
        xbmcplugin.addDirectoryItem(thisPlugin, link, listItem, True)
    
    
    setViewMode()
    xbmcplugin.endOfDirectory(thisPlugin)


def getMenuByUl(ul):
    liMenu = common.parseDOM(ul, "li")
    arrMenu = []
    
    for li in liMenu:
        name = common.makeAscii(common.parseDOM(li, "a", attrs = {"class": "dropdown-toggle dropdown"}))
        common.log(name)
        
        if name != "":
            link = common.parseDOM(li, "a", ret = "href")
            menuItem = {"name": name, "link": common.makeAscii(link)}
            arrMenu.append(menuItem)
            
            sul = common.parseDOM(li, "ul")#does the menu has sub-menu
            if sul is not None:
                menuItem["subMenu"] = getMenuByUl(sul)
    
    return arrMenu

def getHomePageMenuArray():
    # data = file_downloader.fetchPage(EMASTI_BASE_URL)
    
    # if data["status"] == 200:
        # html = data["content"].encode('utf-8')
        # # ulMenu = common.parseDOM(html, "ul", attrs = { "id": "menu" })
        # # arrMenu = getMenuByUl(ulMenu)
        
        # # common.log(arrMenu)
    # else:
        # xbmcgui.Dialog().ok("Emasti Stream", "Failed to download home page menu from emasti.pk")
    
    arrMenu = [
        {
            "name": "Kids", 
            "link": "http://www.emasti.pk/kids", 
            "subMenu": [
                {"name": "Kids Movies", "link": "http://www.emasti.pk/kids/index/0?Cat=movies"},
                {"name": "Cartoon Series", "link": "http://www.emasti.pk/kids/index/0?Cat=KidsCorner"},
                {"name": "Tv Series", "link": "http://www.emasti.pk/kids/index/0?Cat=TvShows"}
                ]
        },
        {
            "name": "Movies", 
            "link": "http://www.emasti.pk/movies", 
            "subMenu": [
                {"name": "Indian Movies", "link": "http://www.emasti.pk/movies/index/0?Cat=indian-movies"},
                {"name": "Dubbed Movies", "link": "http://www.emasti.pk/movies/index/0?Cat=dub-movies"},
                {"name": "3D Movies", "link": "http://www.emasti.pk/movies/index/0?Cat=3d-movies"},
                {"name": "English Movies", "link": "http://www.emasti.pk/movies/index/0?Cat=english-movies"},
                {"name": "Indian Dub Movies", "link": "http://www.emasti.pk/movies/index/0?Cat=indiandub-movies"},
                {"name": "Pakistani Movies", "link": "http://www.emasti.pk/movies/index/0?Cat=pakistani-movies"},
                {"name": "South Indian Movies", "link": "http://www.dmasti.pk/movies?Cat=indiandub-movies"},
                {"name": "Punjabi Movies", "link": "http://www.dmasti.pk/movies?Cat=punjabi-movies"}
                ]
        },
        {
            "name": "Tv Section", 
            "link": "http://www.emasti.pk/tvshows", 
            "subMenu": [
                {"name": "Documentaries", "link": "http://www.emasti.pk/tvshows/index/0?s=Documentary"},
                {"name": "Awards Shows", "link": "http://www.emasti.pk/tvshows/index/0?s=AwardsShows"},
                {"name": "Stage Shows", "link": "http://www.emasti.pk/tvshows/index/0?s=StageShow"},
                {"name": "Tv Series", "link": "http://www.emasti.pk/tvshows/index/0?s=tvseries"},
                {"name": "Wrestling", "link": "http://www.emasti.pk/tvshows/index/0?s=wwe"},
                {"name": "Pakistani Dramas", "link": "http://www.emasti.pk/tvshows/index/0?s=Paki-Dramas"},
                {"name": "Other Shows", "link": "http://www.emasti.pk/tvshows/index/0?s=othershows"}
                ]
        },
        {"name": "Videos", "link": "http://www.emasti.pk/videos/index/0", "hasChildren": False},
        {"name": "Web Tv", "link": "http://www.emasti.pk/webtv"},
        {"name": "Search", "link": "http://www.emasti.pk/search/index/0?keyword=Tom", "hasChildren": False}
    ]
    
    return arrMenu
    
def getVideosWithoutTooltipFromLink(url):
    data = file_downloader.fetchPage(url)
    
    if data["status"] == 200:
        html = data["content"].encode('utf-8')
        divMovieList = common.parseDOM(html, "div", attrs = { "class": "row movie-list" })
        divTooltip = common.parseDOM(divMovieList, "div", attrs = { "class": "item " })
        videos = []
        
        for tt in divTooltip:
            name = common.makeAscii(common.parseDOM(tt, "img", ret = "alt"))
            duration = findNumberFromString(common.makeAscii(common.parseDOM(tt, "div", attrs = { "class": "duration" })))
            link = common.makeAscii(common.parseDOM(tt, "a", attrs = { "class": "poster-video" }, ret = "href"))
            thumb = common.makeAscii(common.parseDOM(tt, "img", ret = "src"))
            isDtubeVideo = link != ""
            
            if link == "":
                link = common.makeAscii(common.parseDOM(tt, "a", attrs = { "class": "name" }, ret = "href"))
                    
            vid = {"name": name, "duration": duration, "thumb": thumb, "video": link, "hasChildren": False, "isDtubeVideo": isDtubeVideo}
                
            videos.append(vid)
        
        return videos
    else:
        xbmcgui.Dialog().ok("Emasti Viewer", "Failed to download home page menu from emasti.pk")
        
        return None
    
def getVideosFromLink(url):
    data = file_downloader.fetchPage(url)
    
    if data["status"] == 200:
        html = data["content"].encode('utf-8')
        divMovieList = common.parseDOM(html, "div", attrs = { "class": "row movie-list" })
        divTooltip = common.parseDOM(divMovieList, "div", attrs = { "class": "tooltiptext" })
        videos = []
        
        for tt in divTooltip:
            quality = common.makeAscii(common.parseDOM(tt, "span", attrs = { "class": "quality" }))
            name = common.makeAscii(common.parseDOM(tt, "h1"))
            rating = findNumberFromString(common.stripTags(common.makeAscii(common.parseDOM(tt, "span", attrs = { "class": "imdb" }))))
            duration = findNumberFromString(common.stripTags(common.makeAscii(common.parseDOM(tt, "span", attrs = { "class": "duration" }))))
            desc = common.makeAscii(common.parseDOM(tt, "p", attrs = { "class": "desc2" }))
            meta = common.parseDOM(tt, "div", attrs = { "class": "meta" })
            link = common.makeAscii(common.parseDOM(tt, "a", attrs = { "class": "watch-now btn full btn-primary" }, ret = "href"))
            
            poster = common.parseDOM(divMovieList, "a", attrs = { "class": "poster", "href": link})
            thumb = common.makeAscii(common.parseDOM(poster, "img", ret = "src"))
            released = None
            stars = None
            
            for m in meta:
                mStripped = common.makeAscii(common.parseDOM(m, "label")).strip()
                if mStripped == "Released:":
                    released = findDateFromString(common.stripTags(common.makeAscii(m)))
                elif mStripped == "Stars:":
                    stars = common.stripTags(common.makeAscii(m))
                    
            vid = {"name": name, "quality": quality, "rating": rating, "duration": duration, "desc": desc, "released": released, 
                "stars": stars, "thumb": thumb, "video": link, "hasChildren": False}
                
            videos.append(vid)
        
        return videos
    else:
        xbmcgui.Dialog().ok("Emasti Viewer", "Failed to download home page menu from emasti.pk")
        
        return None
        
def getNextPrevLinks(link):
    videos = []
    pageIndex = getIndexFromUrl(link)
    
    if pageIndex >= 24:
        prevLink = setIndexInUrl(link, pageIndex - 24)
        prevThumb = os.path.join(addonPath,'resources','Previous-icon.png')
        videos.append({"name": "Previous", "thumb": prevThumb, "link": prevLink, "hasChildren": False})
    
    nextLink = setIndexInUrl(link, pageIndex + 24)
    nextThumb = os.path.join(addonPath,'resources','Next-icon.png')
    videos.append({"name": "Next", "thumb": nextThumb, "link": nextLink, "hasChildren": False})
    
    return videos
    
def getHomePageMenu():
    arrMenu = getHomePageMenuArray()
    listParams = []
    for m in arrMenu:
        hasChildren = True
        if "hasChildren" in m and m["hasChildren"] == False:
            hasChildren = False
            
        listParams.append({"mi": m["name"], "name": m["name"], "hasChildren": hasChildren})
    
    addListing(listParams)
        
def getSubmenu(myparams):
    mi = myparams["mi"]
    
    if mi == "Web Tv":
        getWebtvPage()
    else:
        arrMenu = getHomePageMenuArray()
        listParams = []
        for m in arrMenu:
            if m["name"] == mi and "subMenu" in m:
                for sm in m["subMenu"]:
                    listParams.append({"mi": m["name"], "smi": sm["name"], "name": sm["name"], "hasChildren": True})
                break
        
        addListing(listParams)
        
def performSearch(myparams):
    search = common.getUserInput("Artist", "")
    if search != None:
        link = "http://www.emasti.pk/search/index/0?keyword=" + str(search)
        
        getPageVideos({"mi": "Search", "link": link})
    
def getPageVideos(myparams):
    mi = myparams["mi"]
    smi = None
    link = None if "link" not in myparams else myparams["link"]
    
    if "smi" in myparams:
        smi = myparams["smi"]
    
    if link is None:
        arrMenu = getHomePageMenuArray()
        for m in arrMenu:
            if m["name"] == mi:
                if smi is None:
                    link = m["link"]
                elif "subMenu" in m:
                    for sm in m["subMenu"]:
                        if sm["name"] == smi:
                            link = sm["link"]
                break
    
    if link is not None:
        if mi == "Videos" or mi == "Search":
            arrMenu = getVideosWithoutTooltipFromLink(link)
        else:
            arrMenu = getVideosFromLink(link)
            
        
        nexPrevLinks = getNextPrevLinks(link)
        
        for l in nexPrevLinks:
            l["mi"] = mi
            l["smi"] = smi
        
        arrMenu = arrMenu + nexPrevLinks
        addListing(arrMenu, True)
        
def getWebtvPage():
    global thisPlugin
    data = file_downloader.fetchPage(DMASTI_BASE_URL + "webtv")
    
    if data["status"] == 200:
        html = data["content"].encode('utf-8')
        cats = common.parseDOM(html, "a", attrs = { "class": "channel nav-link" }, ret = True)
        listParams = []
        for cat in cats:
            name = common.parseDOM(cat, "a", attrs = { }, ret = False)
            link = common.parseDOM(cat, "a", attrs = { }, ret = "data-value")

            name = common.makeAscii(name)
            link = common.makeAscii(link)
            listParams.append({"webTvLink": link, "name": name})
        
        addListing(listParams)
    else:
        xbmcgui.Dialog().ok("Emasti Viewer", "Failed to download categories from emasti.pk")


def listWebtvChannels(myparams):
    global thisPlugin
    
    data = file_downloader.fetchPage(EMASTI_BASE_URL + "webtv")
    
    if data["status"] == 200:
        html = data["content"].encode('utf-8')
        divChannels = common.parseDOM(html, "div", attrs = { "class": "channels" })
        channels = common.parseDOM(divChannels, "div", attrs = { "class": "item " })
        
        cat = myparams["cat"]
        
        listParams = []
        for ch in channels:
            genre = common.parseDOM(ch, "div", attrs = { "class": "quality" })
            if common.makeAscii(genre) == "":
                common.log("Genre is empty.")
            elif cat != "All Channels" and common.makeAscii(genre) != cat:
                common.log("Genre is of different category.")
            else:
                img = common.parseDOM(ch, "img")
                video = common.parseDOM(ch, "a", attrs = { "class": "name" }, ret = "href")
                thumb = common.parseDOM(ch, "img", ret = "src")
                name = common.parseDOM(ch, "img", ret = "alt")
                
                params = {
                    "name": common.makeAscii(name),
                    "thumb": common.makeAscii(thumb),
                    "video": common.makeAscii(video),
                    "genre": common.makeAscii(genre)
                }
                
                listParams.append(params)
        
        newList = sorted(listParams, key=lambda k: k['name'].lower())
        
        addListing(listParams)
    else:
        xbmcgui.Dialog().ok("Emasti Viewer", "Failed to download channels of category from emasti.pk")

    return None
def showVideo(params):
    link = params['webTvLink']

    if link == None:
        data = file_downloader.fetchPage(params['video'])
        if data["status"] == 200:
            html = data["content"].encode('utf-8')
            
            divPlayer = common.parseDOM(html, "div", attrs = { "id": "playerDM" })
            clickHandler = common.makeAscii(common.parseDOM(divPlayer, "img", ret = "onclick"))
            indexFirstApostrophe = clickHandler.find("'")
            indexSecondApostrophe = clickHandler.find("'", indexFirstApostrophe + 1)
            link = clickHandler[indexFirstApostrophe + 1:indexSecondApostrophe]

    if link == None:
        xbmcgui.Dialog().ok("Emasti Viewer", "Failed to play requested stream.")
    else:
        common.log(link)
        
        item = xbmcgui.ListItem(params['name'], '', '', path=link)
        if 'thumb' in params:
            item.setThumbnailImage(params['thumb'])

        xbmc.Player().play(item=link, listitem=item)
    

def getIntMonth(strMonth):
    if strMonth == "January":
        return "01"
    elif strMonth == "February":
        return "02"
    elif strMonth == "March":
        return "03"
    elif strMonth == "April":
        return "04"
    elif strMonth == "May":
        return "05"
    elif strMonth == "June":
        return "06"
    elif strMonth == "July":
        return "07"
    elif strMonth == "August":
        return "08"
    elif strMonth == "September":
        return "09"
    elif strMonth == "October":
        return "10"
    elif strMonth == "November":
        return "11"
    elif strMonth == "December":
        return "12"
    else:
        return "01"
        
        
def findNumberFromString(string):
    if string is None or string == "":
        return None
        
    numbers = re.compile('\d+(?:\.\d+)?')
    result = numbers.findall(string)
    
    if len(result) > 0:
        return result[0]
        
    return None

def findDateFromString(string):
    if string is None or string == "":
        return None
        
    dates = re.compile('(\d+) (\w+) (\d+)')
    result = dates.findall(string)
    
    if len(result) == 3:
        #2008-12-07 [('28', 'September', '2012')]
        return str(result[2]) + "-" + getIntMonth(str(result[1])) + "-" + str(result[0])
        
    return None
    
def getIndexFromUrl(url):
    prop = "index/"
    index = url.find(prop)
    endIndex = url.find("?", index + len(prop))
    
    if index == -1:
        return 0
        
    if endIndex == -1:
        return int(url[index + len(prop):])
    else:
        return int(url[index + len(prop):endIndex])
    
def setIndexInUrl(url, newIndex):
    #http://www.emasti.pk/kids/index/144?Cat=movies
    
    prop = "index/"
    index = url.find(prop)
    endIndex = url.find("?", index + len(prop))
    
    if index == -1:
        return url
        
    if endIndex == -1:
        result = url[:index + len(prop)] + str(newIndex)
    else:
        result = url[:index + len(prop)] + str(newIndex) + url[endIndex:]
    
    return result
    
myparams = common.getParameters(sys.argv[2]) # sys.argv[2] would be something like "?path=/root/favorites&login=true"

common.log(myparams)
    
if sys.argv[2] == "":
    #getWebtvPage()
    getHomePageMenu()
elif 'name' in myparams and myparams["name"] == "Search":
    performSearch(myparams)
elif 'smi' in myparams:
    getPageVideos(myparams)
elif 'mi' in myparams:
    if "hasChildren" in myparams and myparams["hasChildren"] == "False":
        getPageVideos(myparams)
    else:
        getSubmenu(myparams)
elif 'cat' in myparams:
    listWebtvChannels(myparams)
elif 'videoPageUrl' in myparams:
    file_downloader.findAndPlayVideo(myparams)
elif 'video' in myparams or 'webTvLink' in myparams:
    showVideo(myparams)