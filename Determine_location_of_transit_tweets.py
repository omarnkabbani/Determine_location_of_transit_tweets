import re
import nltk
from nltk.tokenize import word_tokenize
import pandas as pd
import numpy as np
from nltk import ngrams
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import matplotlib as plt
from nltk.corpus import stopwords
import math
R = 6373.0
stopwords = stopwords.words('english')

def leaves(tree):
    """Finds NP (nounphrase) leaf nodes of a chunk tree."""
    for subtree in tree.subtrees(filter = lambda t: t.label()=='NP'):
        yield subtree.leaves()

def normalise(word):
    """Normalises words to lowercase and stems and lemmatizes it."""
    word = word.lower()
    # word = stemmer.stem_word(word) #if we consider stemmer then results comes with stemmed word, but in this case word will not match with comment
    word = lemmatizer.lemmatize(word)
    return word

def acceptable_word(word):
    """Checks conditions for acceptable word: length, stopword. We can increase the length if we want to consider large phrase"""
    accepted = bool(2 <= len(word) <= 40
        and word.lower() not in stopwords)
    return accepted

def get_terms(tree):
    for leaf in leaves(tree):
        term = [ normalise(w) for w,t in leaf if acceptable_word(w) ]
        yield term

sentence_re = r'(?:(?:[A-Z])(?:.[A-Z])+.?)|(?:\w+(?:-\w+)*)|(?:\$?\d+(?:.\d+)?%?)|(?:...|)(?:[][.,;"\'?():-_`])'
lemmatizer = nltk.WordNetLemmatizer()
stemmer = nltk.stem.porter.PorterStemmer()
grammar = r"""
    NBAR:
        {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns
        
    NP:
        {<NBAR>}
        {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
"""
chunker = nltk.RegexpParser(grammar)

calgarypoint=geopy.point.Point(51.01,-114.05)
binglocator=geopy.geocoders.Bing("As-wt8JFBlzq0Ao3wRMTCNcobRVxiGuhdiERXb1ygeYr53mR5gi0tIDjCezfKwNW")

data=pd.read_csv("Calgary_Transit_Stops.csv")
stop_ids=data.TELERIDE_NUMBER.values
stop_ids=list(stop_ids)
stop_names=data.STOP_NAME.values
stop_coodinates=data.point.values

data=pd.read_csv("Calgary_Transit_Stations.csv")
station_names=data.Station_Name.values
station_names=list(station_names)
station_names_common=data.Station_Name_Common.values
station_names_common=list(station_names_common)
station_coodinates=data.Coordinates.values
station_coodinates=list(station_coodinates)

data=pd.read_csv("Calgary_Transit_Routes.csv")
route_numbers=data.ROUTE_SHORT_NAME.values
route_numbers=list(route_numbers)
route_common_names=data.COMMON_NAME.values
route_common_names=list(route_common_names)
route_long_names=data.ROUTE_LONG_NAME.values
route_long_names=list(route_long_names)

def hasNumbers(inputString):
  return any(char.isdigit() for char in inputString)

pattern= r"\D(\d{%d})\D" % 4   # \D to avoid matching 567           
file = open("Input.txt",'r',encoding="utf-8")
lines=file.readlines()
file.close()

with open("Out.txt","w") as outfile:
    for line in lines:
        flag="F"
        lineflag="F"
        print(line)
        outfile.write(line)
        outfile.write("\n")
        line=re.sub(r'[^\w]', ' ', line) #remove symbols
        line=line.lower()    
        tokens = word_tokenize(line)
        bigrams=[]
        try:
            _bigrams=ngrams(line.split(),2)
            __bigrams=list(_bigrams)
            for bigram in __bigrams:
                bigram_=bigram[0]+" "+bigram[1]
                bigrams.append(bigram_)
        except:
            bigrams=[]
        if re.search(r"(?<!\d)\d{4}(?!\d)", line)==None:
            pass
        elif re.findall(pattern, line)!=[] or re.findall(pattern, line)!=None:
            for n in re.findall(pattern, line):
                try:
                    number=int(n)
                    index_=tokens.index(str(number))
                    if tokens[index_-1]=="stop" or tokens[index_-2]=="stop":
                        index__=stop_ids.index(int(number))
                        flag="T"
                        print("Stop ID:",stop_ids[index__])
                        outfile.write("Stop ID:")
                        outfile.write(str(stop_ids[index__]))
                        outfile.write("\n")
                        print("Stop Name:",stop_names[index__])
                        outfile.write("Stop Name:")
                        outfile.write(str(stop_names[index__]))
                        outfile.write("\n")
                        print("Stop Coordinates:",stop_coodinates[index__])
                        outfile.write("Stop Coordinates:")
                        outfile.write(stop_coodinates[index__])
                        outfile.write("\n")
                    if tokens[index_-1]=="bus" or (tokens[index_-2]=="bus" and tokens[index_-1]!="stop") or tokens[index_-1]=="car" or tokens[index_-2]=="car" or tokens[index_-1]=="train" or tokens[index_-2]=="train" or tokens[index_-1]=="vehicle" or tokens[index_-2]=="vehicle":
                        flag="T"
                        print("Vehicle ID:",tokens[index_])
                        outfile.write("Vehicle ID:")
                        outfile.write(str(tokens[index_]))
                        outfile.write("\n")
                except:
                    pass
        if "towards" in tokens or "to" in tokens:
            try:
                towardstoposition=tokens.index("to")
            except:
                towardstoposition=tokens.index("towards")
            for token in tokens:
                if (nltk.edit_distance(token,"saddletown")<3) or token=="69" or token =="69st":
                    if (tokens.index(token)-towardstoposition>0) and (tokens.index(token)-towardstoposition<3):
                        flag="T"
                        lineflag="T"
                        print("Line: Blue line")
                        outfile.write("Line: Blue line")
                        outfile.write("\n")
                elif (nltk.edit_distance(token,"somerset")<2) or (nltk.edit_distance(token,"summerset")<2) or (nltk.edit_distance(token,"bridlewood")<3) or (nltk.edit_distance(token,"tuscany")<2):
                    if (tokens.index(token)-towardstoposition>0) and (tokens.index(token)-towardstoposition<3):                        
                        flag="T"
                        lineflag="T"
                        print("Line: Red line")
                        outfile.write("Line: Red line")
                        outfile.write("\n")
        if ("red" in tokens and "line" in tokens) or ("south" in tokens and "train" in tokens) or ("southbound" in tokens and "train" in tokens) or ("sb" in tokens and "train" in tokens) or ("northwest" in tokens and "train" in tokens) or ("nw" in tokens and "train" in tokens) or ("sw" in tokens and "train" in tokens) or ("southwest" in tokens and "train" in tokens):
            print("Line: Red line")
            outfile.write("Line: Red line")
            outfile.write("\n")
            flag="T"
            lineflag="T"
        if ("blue" in tokens and "line" in tokens) or ("west" in tokens and "train" in tokens) or ("westbound" in tokens and "train" in tokens) or ("wb" in tokens and "train" in tokens) or ("northeast" in tokens and "train" in tokens) or ("ne" in tokens and "train" in tokens):
            print("Line: Blue line")
            outfile.write("Line: Blue line")
            outfile.write("\n")
            flag="T"
            lineflag="T"
        if [j for j, x in enumerate(tokens) if (x == "bus" or x=="route")]!=[]:
            templist=[j for j, x in enumerate(tokens) if (x == "bus" or x=="route")]
            for bus_routeposition in templist:
                try:
                    unigram=tokens[bus_routeposition-1]
                    try:
                        unigram=int(unigram)
                    except:
                        pass
                    for route_number in route_numbers:
                        if unigram==route_number:
                            index_____1=route_numbers.index(int(route_number))
                            flag="T"
                            print("Bus route:",route_long_names[index_____1])
                            outfile.write("Bus route:")
                            outfile.write(str(route_long_names[index_____1]))
                            outfile.write("\n")
                    for route_common_name in route_common_names:
                        if unigram==route_common_name:
                            index_____1=route_common_names.index(route_common_name)
                            flag="T"
                            print("Bus route:",route_long_names[index_____1])
                            outfile.write("Bus route:")
                            outfile.write(str(route_long_names[index_____1]))
                            outfile.write("\n")
                except:
                    pass
                try:
                    bigram=str(tokens[bus_routeposition-2])+" "+str(tokens[bus_routeposition-1])
                    for route_common_name in route_common_names:
                        if bigram==route_common_name:
                            index_____2=route_common_names.index(route_common_name)
                            flag="T"
                            print("Bus route:",route_long_names[index_____2])
                            outfile.write("Bus route:")
                            outfile.write(str(route_long_names[index_____2]))
                            outfile.write("\n")
                except:
                    pass
                try:
                    trigram=str(tokens[bus_routeposition-3])+" "+str(tokens[bus_routeposition-2])+" "+str(tokens[bus_routeposition-1])
                    for route_common_name in route_common_names:
                        if trigram==route_common_name:
                            index_____3=route_common_names.index(route_common_name)
                            flag="T"
                            print("Bus route:",route_long_names[index_____3])
                            outfile.write("Bus route:")
                            outfile.write(str(route_long_names[index_____3]))
                            outfile.write("\n")
                except:
                    pass
                try:
                    post=int(tokens[bus_routeposition+1])
                    for route_number in route_numbers:
                        if post==route_number:
                            index_____4=route_numbers.index(route_number)
                            flag="T"
                            print("Bus route:",route_long_names[index_____4])
                            outfile.write("Bus route:")
                            outfile.write(str(route_long_names[index_____4]))
                            outfile.write("\n")
                except:
                    pass
        for token in tokens:
            for station_name_common in station_names_common:
                if token==station_name_common:
                    index___=station_names_common.index(station_name_common)
                    flag="T"
                    if station_names[index___]=="Saddletowne" or station_names[index___]=="69 Street" or station_names[index___]=="Tuscany" or station_names[index___]=="Somerset-Bridlewood":
                        if lineflag=="T":
                            pass
                    elif [i_ for i_ in tokens if i_ in["towards","driver","bus","leaving","left"]]!=[] or [j_ for j_ in bigrams if j_ in ["almost at","heading to","almost to","got to"]]!=[]:
                        pass
                    else:
                        print("CTrain Station Name:",station_names[index___])
                        print("CTrain Station Coordinates:",station_coodinates[index___])     
                        outfile.write("CTrain Station Name:")
                        outfile.write(str(station_names[index___]))
                        outfile.write("\n")
                        outfile.write("CTrain Station Coordinates:")
                        outfile.write(str(station_coodinates[index___]))
                        outfile.write("\n")                    
                elif (nltk.edit_distance(token,station_name_common)<2) and len(token)>5 and hasNumbers(token)==False and token!="street" and token!="st" and token!="str" and token!="avenue" and token!="av" and token!="ave":
                    index___=station_names_common.index(station_name_common)
                    flag="T"
                    if station_names[index___]=="Saddletowne" or station_names[index___]=="69 Street" or station_names[index___]=="Tuscany" or station_names[index___]=="Somerset-Bridlewood":
                        if lineflag=="T":
                            pass
                    elif [i_ for i_ in tokens if i_ in["towards","driver","bus","leaving","left"]]!=[] or [j_ for j_ in bigrams if j_ in ["almost at","heading to","almost to","got to"]]!=[]:
                        pass
                    else:
                        print("CTrain Station Name:",station_names[index___])
                        print("CTrain Station Coordinates:",station_coodinates[index___])
                        outfile.write("CTrain Station Name:")
                        outfile.write(str(station_names[index___]))
                        outfile.write("\n")
                        outfile.write("CTrain Station Coordinates:")
                        outfile.write(str(station_coodinates[index___]))
                        outfile.write("\n") 
        if [i for i in bigrams if i in station_names_common]!=[]:
            index____=station_names_common.index([i for i in bigrams if i in station_names_common][0])
            flag="T"
            if station_names[index____]=="Saddletowne" or station_names[index____]=="69 Street" or station_names[index____]=="Tuscany" or station_names[index____]=="Somerset-Bridlewood":
                if lineflag=="T":
                    pass
            elif [i_ for i_ in tokens if i_ in["towards","driver","bus","leaving","left"]]!=[] or [j_ for j_ in bigrams if j_ in ["almost at","heading to","almost to","got to"]]!=[]:
                pass
            else:
                print("CTrain Station Name:",station_names[index____])
                print("CTrain Station Coordinates:",station_coodinates[index____])
                outfile.write("CTrain Station Name:")            
                outfile.write(str(station_names[index____]))
                outfile.write("\n")
                outfile.write("CTrain Station Coordinates:")
                outfile.write(str(station_coodinates[index____]))
                outfile.write("\n") 
        '''if flag == "F":
            toks = nltk.regexp_tokenize(line, sentence_re)
            postoks = nltk.tag.pos_tag(toks)
            tree = chunker.parse(postoks)
            terms = get_terms(tree)
            for term in terms:
                try:
                    binglocation=binglocator.geocode(" ".join(term),user_location=calgarypoint,exactly_one=False)
                    for locations in binglocation:
                        out=locations.raw
                        lat1 = math.radians(out["point"]["coordinates"][0])
                        lon1 = math.radians(out["point"]["coordinates"][1])
                        lat2 = math.radians(51.01)
                        lon2 = math.radians(-114.05)
                        dlon = lon2 - lon1
                        dlat = lat2 - lat1
                        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
                        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                        distance = R * c
                        if distance<15:
                            print(out["point"]["coordinates"][0],",",out["point"]["coordinates"][1])
                            print(" ".join(term))
                            outfile.write("Location name:")
                            outfile.write(str(" ".join(term))) 
                            outfile.write("\n")
                            outfile.write("Coodinates:")
                            outfile.write(str(out["point"]["coordinates"][0]))
                            outfile.write(",")
                            outfile.write(str(out["point"]["coordinates"][1]))
                            outfile.write("\n")
                except:
                    pass'''
        print("-----------")
        outfile.write("-----------")
        outfile.write("\n")
outfile.close()