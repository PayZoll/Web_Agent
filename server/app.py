from flask import Flask, request, render_template
from test_bot import process_message, get_all_companies_data, post_on_twitter, post_on_reddit, silent_bulk_transfer

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        employee_id = request.form.get("employee_id")
        company_id = request.form.get("company_id")
        message = request.form.get("message")
        
        # Process the message with OpenAI
        response = process_message(employee_id, company_id, message)
        
        # Parse the response
        if isinstance(response["FunctionCalls"], dict):
            function_call = response["FunctionCalls"].get("Name_of_the_function")
        else:
            function_call = response["FunctionCalls"]  # if it's a string
        
        user_response = response["ResponseForTheUser"]["Text_to_show_to_the_user"]
        
        # Handle function calls
        result = user_response
        if function_call:
            func_name, *params = function_call.split(",", 1)
            if func_name == "get_all_companies_data":
                result = get_all_companies_data()
            elif func_name == "post_on_twitter":
                tweet_body = params[0].strip() if params else "Default tweet"
                result = post_on_twitter(tweet_body)
            elif func_name == "post_on_reddit":
                param_list = params[0].split(",", 2) if params else ["test", "Test Title", "Default body"]
                subreddit = param_list[0].strip()
                title = param_list[1].strip() if len(param_list) > 1 else "Default Title"
                body = param_list[2].strip() if len(param_list) > 2 else "Default body"
                result = post_on_reddit(subreddit, title, body)
            elif func_name == "silent_bulk_transfer":
                param_list = params[0].split(",", 1) if params else ["", ""]
                rpc_url = param_list[0].strip()
                employees_json = param_list[1].strip() if len(param_list) > 1 else "[]"
                result = silent_bulk_transfer(rpc_url, employees_json)
        
        return render_template("index.html", result=result)
    
    return render_template("index.html", result="Enter your message below.")

if __name__ == "__main__":
    app.run(debug=True)