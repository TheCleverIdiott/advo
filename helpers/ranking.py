def convert_to_dict(list1): # converts list to dict
    new_dict = {}
    for itr in list1 :
        new_key = (int)(itr['_id'])
        new_val = itr['keywords']
        new_dict[new_key] = new_val
    
    return new_dict

def make_ranking(docs, kw, order_no, ranking) :
    for itr in docs.keys() : # for every document
        if kw in docs[itr] :
            ranking[itr] += ((docs[itr]).index(kw))*order_no
        else :
            ranking[itr] += 100000 # > 13

def sort_dict(markdict):    
    marklist = sorted((value, key) for (key,value) in markdict.items())
    sortdict = dict([(k,v) for v,k in marklist])
    return sortdict