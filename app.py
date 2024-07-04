from flask import Flask, render_template, request
import mysql.connector
import pandas as pd
from recommender import connect_to_database, fetch_data, create_user_item_matrix, create_item_feature_matrix, compute_item_similarity, get_top_recommendations, get_user_previous_interactions

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user')
def user_recommendations():
    user_id = request.args.get('user_id', type=int)
    if user_id is None:
        return "User ID not provided", 400
    
    conn = connect_to_database()
    users, products, interactions = fetch_data(conn)
    
    user_item_matrix = create_user_item_matrix(interactions, products)
    item_features = create_item_feature_matrix(products)
    item_similarity = compute_item_similarity(item_features)
    
    user_previous_interactions = get_user_previous_interactions(user_id, interactions, products)
    recommendations = get_top_recommendations(user_id, user_item_matrix, item_features, item_similarity, products)
    
    conn.close()
    
    return render_template('user.html', user_id=user_id, previous_interactions=user_previous_interactions, recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
