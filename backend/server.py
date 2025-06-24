from flask import Flask, request, jsonify
from flask_cors import CORS
from waitress import serve
from article_functions import fetch_articles
from database_functions import search_company_table, get_company_data, company_exists
from ethics_categories import ETHICS_CATEGORIES

app = Flask(__name__)
CORS(app)

@app.get("/search") #?query
def search_company(): 
    """Search company endpoint. 

    Returns:
        json, status_code: return json and status code
    """
    query = request.args.get("query")
    
    if not query:
        json = {"error": "Missing required search parameter 'query'"}
        code = 400
    else:
        query = query.replace("'", "").replace('"', "")
        
        names = search_company_table(query)
        json = {"results": names}
        code = 200
    
    return jsonify(json) , code

@app.get("/company/<string:company>")
def get_company(company):
    
    data = get_company_data(company)
    
    if not data:
        json = {"Error": "Company does not exist in database"}
        code = 404
        print(json)
    
    else:
        json = {"name": data[0], "description": data[1], "website": data[2], "logo": data[3], "industries": data[4]}
        code = 200
            
    return jsonify(json), code


@app.get("/articles") #?company, page, category = none
def get_articles():
    args = request.args
    company = args.get("company")
    category = args.get("category", None)
    page = args.get("page")
    
    if category and (category.lower() == "null" or category.lower() == "none"):
        category = None
        
    if not (company and page):
        json = {"Error": f"Missing one or more required parameters: 'company', 'page'"}
        code = 400
    
    elif category not in ETHICS_CATEGORIES and category is not None:
        json = {"Error": f"Category must be one of the following: {", ".join(ETHICS_CATEGORIES.keys())} or None"}
        code = 400
    else:
        try:
            articles = fetch_articles(company, int(page), category)
        except Exception as e:
            if str(e)[:4] == "page":
                code = 400
            else: #company doesn't exist in db
                code = 404
            json = {"Error": str(e)}
            
        else:
            json = {"articles": [article.to_json() for article in articles]}
            code = 200
    
    return jsonify(json), code

if __name__ =='__main__':
    # serve(app, host = "0.0.0.0", port=8080) production
    app.run(debug=True, port=6969)