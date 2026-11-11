import json,sys,datetime as dt,pathlib
R=pathlib.Path(__file__).resolve().parent
# usage: mkjobs.py <commit> <out.json> pid@YYYY-MM-DDTHH:MM(KW) ...
commit,out=sys.argv[1],sys.argv[2]
B=f'https://raw.githubusercontent.com/khalidorgg/diwan.bizz/{commit}/reels/'
J=[];O=[]
for a in sys.argv[3:]:
    pid,at=a.split('@'); p=json.load(open(R/'posts'/f'{pid}.json'))
    kw=dt.datetime.fromisoformat(at+':00+03:00'); sa=kw.astimezone(dt.timezone(dt.timedelta(hours=1)))
    d=sa.strftime('%Y-%m-%dT%H:%M:%S'); date=d+'+01:00'
    text=p['caption'].strip()+'\n\n'+p['hashtags'].strip()
    base=dict(autoPublish=True,descendants=[],draft=False,firstCommentText='',hasNotReadNotes=False,mediaAltText=[],shortener=False,smartLinkData={'ids':[]},publicationDate={'dateTime':d,'timezone':'Europe/Sarajevo'},media=[B+pid+'.mp4'])
    reel=dict(base,providers=[{'network':'instagram'},{'network':'tiktok'}],text=text,videoThumbnailUrl=B+pid+'-cover.jpg',
        instagramData={'type':'REEL','showReelOnFeed':True,'isAiGenerated':True},
        tiktokData={'privacyOption':'PUBLIC_TO_EVERYONE','title':p['title'][:90],'autoAddMusic':False,'isAigc':True})
    story=dict(base,providers=[{'network':'instagram'}],instagramData={'type':'STORY','isAiGenerated':True})
    yt=dict(base,providers=[{'network':'youtube'}],text=text+' #Shorts',youtubeData={'title':(p['title']+' #Shorts')[:99],'type':'short','privacy':'public','tags':['ديوان البزنس','مشاريع','بزنس','الكويت','ريادة أعمال'],'category':'EDUCATION','madeForKids':False,'isAiGeneratedContent':False})
    for k,i in (('reel',reel),('story',story),('yt',yt)): J.append({'id':pid,'kind':k,'date':date,'info':json.dumps(i,ensure_ascii=False)})
    first=p['caption'].strip().split('\n')[0]
    O.append({'id':pid,'at':at.replace('T',' '),'content':first+'\n\n'+' '.join(p['hashtags'].split()[:9]),'video_url':f'https://cdn.jsdelivr.net/gh/khalidorgg/diwan.bizz@{commit}/reels/{pid}.mp4','title':p['title']})
json.dump({'metricool':J,'oneup':O},open(out,'w'),ensure_ascii=False,indent=0)
print(len(J),len(O))
