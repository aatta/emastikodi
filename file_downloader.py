import xbmc, xbmcplugin, xbmcaddon, xbmcgui, sys, os, urllib, CommonFunctions, re, json, SimpleDownloader as downloader

common = CommonFunctions
common.plugin = "Emasti Viewer-1.0"
common.dbg = True # Default
common.dbglevel = 3 # Default
common.USERAGENT = u"Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"

downloader = downloader.SimpleDownloader()

class DownloadCancelException(Exception):
    pass
    
def nameFromUrl(url):
    arr = str(url).split("/")
    return arr[len(arr) - 1]

def extensionFromUrl(url):
    arr = str(url).split("/")
    name = arr[len(arr) - 1]
    arr = str(name).split(".")
    
    return arr[len(arr) - 1]
    
def fetchPage(url):
    result = common.fetchPage({"link": url})
    return result
    
def downloadFile(url, dest, name):
    if not os.path.exists(dest):
        xbmcgui.Dialog().ok("Emasti Viewer", "Destination doesn't exist.", "Destination specified in setting doesn't exist.")
        return None
    else:
        params = { "url": url, "download_path": dest }
        ext = extensionFromUrl(url)
        downloader.download(name+"."+ext, params)
        common.log("EmastiViewer: Download added")
        pass

def getJSPropFromString(string, prop):
    prop = prop + ": '"
    index = string.index(prop)
    endIndex = string.index("'", index + len(prop))
    return string[index + len(prop):endIndex]
    
def findAndPlayVideo(params, isDownload = False):
    url = params["videoPageUrl"]
    isDtubeVideo = params["isDtubeVideo"]
    
    data = fetchPage(url)
    
    if data["status"] == 200:
        html = data["content"].encode('utf-8')
        link = None
        name = None
        thumb = None
        
        if isDtubeVideo == "True":
            body = common.parseDOM(html, "body")
            script = common.makeAscii(common.parseDOM(html, "script"))
            vidInfo = str(common.makeAscii(script[script.index("{"):script.rindex("}") + 1]))
            
            link = getJSPropFromString(vidInfo, "file")
            name = getJSPropFromString(vidInfo, "title")
            thumb = getJSPropFromString(vidInfo, "image")
        else:
            divContainer = common.parseDOM(html, "div", attrs = { "class": "vc_row wpb_row vc_row-fluid" })
            videoLinks = common.parseDOM(divContainer, "a", attrs = { "class": "vh_button red icon-down hover_right" }, ret = "href")
            if len(videoLinks) > 0:
                link = videoLinks[0]
                name = common.makeAscii(common.parseDOM(divContainer, "div", attrs = { "class": "page_title event" }))
                thumbContainer = common.parseDOM(divContainer, "div", attrs = { "class": "image_wrapper2 event shadows" })
                thumb = common.makeAscii(common.parseDOM(thumbContainer, "img", ret = "src"))
            
        
        if link is not None:
            common.log(link)
            if isDownload == False:
                item = xbmcgui.ListItem(name, '', '', path=link)
                item.setThumbnailImage(thumb)
                
                # infoLabels = {"rating": 1.6, "cast": ["A", "B", "C"], "plot": "A very long plot",
                    # "duration": 300, "aired": "2017-08-24"}
                # item.setInfo("video", infoLabels)
                
                xbmc.Player().play(item=link, listitem=item)
            else:
                dest = params["dest"]
                downloadFile(link, dest, name)
        else:
            xbmcgui.Dialog().ok("Emasti Viewer", "Failed to find any video at " + url)

if len(sys.argv) == 3:
    myparams = common.getParameters(sys.argv[2]) # sys.argv[2] would be something like "?path=/root/favorites&login=true"
    common.log(myparams)
    
    if 'dest' in myparams:
        findAndPlayVideo(myparams, True)