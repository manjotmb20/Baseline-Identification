from flask import Flask,render_template,request
from elasticsearch import Elasticsearch
import pickle

cit_count=pickle.load(open("cit_final.pkl","rb"))
# paper_key=pickle.load(open("paper_key2.pickle","rb"))
# paper_title=pickle.load(open("paper_title.pickle","rb"))
# paper_abstract=pickle.load(open("paper_ab.pkl","rb"))

app = Flask(__name__)
es = Elasticsearch('https://ksd41kkwz3:qk932cg8ed@yew-506106106.us-east-1.bonsaisearch.net:443')
# a="e"

# print("ye")
@app.route('/')
def home():
    return render_template('search.html')

@app.route('/search/results', methods=['GET', 'POST'])
def search_request():
    print("here")
    search_term = request.form["input"]

    print(search_term)

    try:
        print(request.values)
    except:
        print("ok")  
          
    new_val=request.form["sort"]      
    # try:
    #     val2=request.form["input2"]=="input1"
    # except:
    #     val2=False    

    # try:
    #     val_2=request.form["Relevance2"]=="on"
    # except:
    #     val_2=False

    # try:
    #     val3=request.form["input2"]=="input1"
    # except:
    #     val3=False    

    # try:
    #     val_3=request.form["Relevance3"]=="on"
    # except:
    #     val_3=False            
              
    
    if new_val=='Year':
        res = es.search(
        index="base-index-new", 
        size=20, 
        body={
            "query": {
                "multi_match" : {
                    "query": search_term, 
                    "fields": [
                        "Title",
                        "Abstract",
                        "Context"
                    ] 
                }
            }
        }
        )
   
        name=set()
        s=dict()
        key=dict()
        cont=dict()
        for hit in res['hits']['hits']:
            name.add(hit['_source']['Title'])
            try:
                key[hit['_source']['Title']]=hit['_source']['Url']
            except:
                key[hit['_source']['Title']]="https://www.semanticscholar.org/"    
            cont[hit['_source']['Title']]=hit['_source']['Abstract']
            # print(hit['_source']['key_paper'].split("-")[0][1:])
            try:
                # val=int(hit['_source']['key_paper'].split("-")[0][1:])
                # if val>20:
                #     val=val+1900
                # else:
                #     val=val+2000    
                s[hit['_source']['Title']]=int(hit['_source']['Date'])
                # s[hit['_source']['paper_name']]=cit_count[hit['_source']['key_paper']]
                # print(s[hit['_source']['paper_name']])
                # print(hit['_source']['key_paper'])

            except:
                q=1    
        name2=sorted(s,key=s.get,reverse=True)
        
        

        return render_template('results.html', res=res , name=name2, key=key,cont=cont,term=search_term )


    elif new_val=='Citations':
        print("isme aayega na ")
        res = es.search(
        index="base-index-new", 
        size=20, 
        body={
            "query": {
                "multi_match" : {
                    "query": search_term, 
                    "fields": [
                        "Title",
                        "Abstract",
                        "Context"
                    ] 
                }
            }
        }
        )
   
        name=set()
        s=dict()
        key=dict()
        cont=dict()
        for hit in res['hits']['hits']:
            name.add(hit['_source']['Title'])
            try:
                key[hit['_source']['Title']]=hit['_source']['Url']
            except:
                key[hit['_source']['Title']]="https://www.semanticscholar.org/"
            cont[hit['_source']['Title']]=hit['_source']['Abstract']
            # print(hit['_source']['key_paper'].split("-")[0][1:])
            try:
                # s[hit['_source']['paper_name']]=int(hit['_source']['key_paper'].split("-")[0][1:])
                s[hit['_source']['Title']]=int(hit['_source']['Citation'])
                # print(s[hit['_source']['paper_name']])
                # print(hit['_source']['key_paper'])

            except:
                q=1    
        name2=sorted(s,key=s.get,reverse=True)

        
        
        

        return render_template('results.html', res=res , name=name2, key=key,cont=cont,term=search_term )    


    

    res = es.search(
        index="base-index-new", 
        size=20, 
        body={
            "query": {
                "multi_match" : {
                    "query": search_term, 
                    "fields": [
                        "Title",
                        "Abstract",
                        "Context"
                    ] 
                }
            }
        }
    )
   
    name=set()
    s=dict()
    key=dict()
    cont=dict()
    for hit in res['hits']['hits']:
        name.add(hit['_source']['Title'])
        try:
            key[hit['_source']['Title']]=hit['_source']['Url']
        except:
            key[hit['_source']['Title']]="https://www.semanticscholar.org/"
        cont[hit['_source']['Title']]=hit['_source']['Abstract']
        # print(hit['_source']['key_paper'].split("-")[0][1:])
        try:
            s[hit['_source']['Title']]=hit['_source']['Url']
        except:
            q=1    
    name2=sorted(s,key=s.get,reverse=True)
    
    

    return render_template('results.html', res=res , name=name, key=key,cont=cont,term=search_term )

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3001)    