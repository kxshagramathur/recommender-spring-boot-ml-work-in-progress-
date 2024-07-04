import mysql.connector
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection details
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'frankocean',
    'database': 'recom_model_trial'
}

def connect_to_database():
    """
    Connects to the MySQL database and returns the connection object.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        logging.info("Database connection successful.")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        raise

def fetch_data(conn):
    """
    Fetches users, products, and user interactions from the database.
    """
    query_users = "SELECT * FROM Users"
    query_products = "SELECT * FROM Products"
    query_interactions = "SELECT * FROM User_Interactions"
    
    users = pd.read_sql(query_users, conn)
    products = pd.read_sql(query_products, conn)
    interactions = pd.read_sql(query_interactions, conn)
    
    return users, products, interactions

def create_user_item_matrix(interactions, products):
    weights = {'view': 1, 'add_to_cart': 3, 'share': 2}
    interactions['weight'] = interactions['interaction_type'].map(weights)
    
    user_item_matrix = interactions.pivot_table(
        index='user_id', 
        columns='product_id', 
        values='weight', 
        aggfunc='sum', 
        fill_value=0
    )
    
    for product_id in products['product_id']:
        if product_id not in user_item_matrix.columns:
            user_item_matrix[product_id] = 0
    
    user_item_matrix = user_item_matrix.sort_index(axis=1)
    user_item_matrix = user_item_matrix.div(user_item_matrix.sum(axis=1), axis=0)
    
    return user_item_matrix

def create_item_feature_matrix(products):
    category_dummies = pd.get_dummies(products['category'], prefix='category')
    price_normalized = (products['price'] - products['price'].min()) / (products['price'].max() - products['price'].min())
    
    item_features = pd.concat([category_dummies, price_normalized.rename('price_normalized')], axis=1)
    item_features.index = products['product_id']
    item_features = item_features.sort_index()
    
    return item_features

def compute_item_similarity(item_features):
    return cosine_similarity(item_features)

def get_top_recommendations(user_id, user_item_matrix, item_features, item_similarity, products, n=5):
    if user_id not in user_item_matrix.index:
        return pd.DataFrame()
    
    user_vector = user_item_matrix.loc[user_id].values.reshape(1, -1)
    scores = user_vector.dot(item_similarity)
    score_series = pd.Series(scores.flatten(), index=item_features.index)
    
    interacted_items = user_item_matrix.loc[user_id][user_item_matrix.loc[user_id] > 0].index
    score_series = score_series.drop(interacted_items)
    
    top_recommendations = score_series.sort_values(ascending=False).head(n)
    recommended_products = products[products['product_id'].isin(top_recommendations.index)]
    recommended_products['score'] = recommended_products['product_id'].map(top_recommendations)
    
    return recommended_products.sort_values('score', ascending=False)

def get_user_previous_interactions(user_id, interactions, products):
    user_interactions = interactions[interactions['user_id'] == user_id]
    user_interactions = user_interactions.merge(products, on='product_id', how='left')
    return user_interactions[['interaction_id', 'user_id', 'product_id', 'interaction_type', 'timestamp', 'name', 'category', 'price']]

def main():
    conn = connect_to_database()
    users, products, interactions = fetch_data(conn)
    
    user_item_matrix = create_user_item_matrix(interactions, products)
    item_features = create_item_feature_matrix(products)
    item_similarity = compute_item_similarity(item_features)
    
    test_user_id = 1  # Example user_id for recommendation
    
    user_previous_interactions = get_user_previous_interactions(test_user_id, interactions, products)
    logging.info(f"Previous interactions for user {test_user_id}:")
    logging.info(user_previous_interactions.to_string(index=False))
    
    recommendations = get_top_recommendations(test_user_id, user_item_matrix, item_features, item_similarity, products)
    logging.info(f"\nTop recommendations for user {test_user_id}:")
    logging.info(recommendations.to_string(index=False))
    
    conn.close()

if __name__ == "__main__":
    main()