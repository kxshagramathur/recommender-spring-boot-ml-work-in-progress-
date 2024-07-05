import requests
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Microservice URLs
USER_SERVICE_URL = 'http://localhost:8081/users'
PRODUCT_SERVICE_URL = 'http://localhost:8082/products'
INTERACTION_SERVICE_URL = 'http://localhost:8083/interactions'

def fetch_data():
    """Fetches users, products, and user interactions from microservices."""
    try:
        users = pd.DataFrame(requests.get(USER_SERVICE_URL).json())
        logging.info(f"Users Data: {users.head()}")
        products = pd.DataFrame(requests.get(PRODUCT_SERVICE_URL).json())
        logging.info(f"Products Data: {products.head()}")
        interactions = pd.DataFrame(requests.get(INTERACTION_SERVICE_URL).json())
        logging.info(f"Interactions Data: {interactions.head()}")
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        raise e
    
    return users, products, interactions

def create_user_item_matrix(interactions, products):
    try:
        logging.info("Creating user-item matrix.")
        # Rename columns to match the expected names
        interactions.rename(columns={'interactionType': 'interaction_type'}, inplace=True)
        
        weights = {'view': 1, 'add_to_cart': 3, 'share': 2}
        interactions['weight'] = interactions['interaction_type'].map(weights)
        
        user_item_matrix = interactions.pivot_table(
            index='userId', 
            columns='productId', 
            values='weight', 
            aggfunc='sum', 
            fill_value=0
        )
        
        for productId in products['productId']:
            if productId not in user_item_matrix.columns:
                user_item_matrix[productId] = 0
        
        user_item_matrix = user_item_matrix.sort_index(axis=1)
        user_item_matrix = user_item_matrix.div(user_item_matrix.sum(axis=1), axis=0)
        
        return user_item_matrix
    except KeyError as e:
        logging.error(f"KeyError: {e}")
        raise e
    except Exception as e:
        logging.error(f"An error occurred while creating user-item matrix: {e}")
        raise e

def create_item_feature_matrix(products):
    item_features = products.set_index('productId')[['category', 'price']]
    item_features['price'] = (item_features['price'] - item_features['price'].min()) / (item_features['price'].max() - item_features['price'].min())
    item_features = pd.get_dummies(item_features, columns=['category'])
    return item_features

def compute_item_similarity(item_features):
    item_similarity = cosine_similarity(item_features)
    item_similarity_df = pd.DataFrame(item_similarity, index=item_features.index, columns=item_features.index)
    return item_similarity_df

def get_top_recommendations(userId, user_item_matrix, item_features, item_similarity, products, n=10):
    if userId not in user_item_matrix.index:
        return pd.DataFrame(columns=products.columns)
    
    user_vector = user_item_matrix.loc[userId].values.reshape(1, -1)
    scores = user_vector.dot(item_similarity)
    score_series = pd.Series(scores.flatten(), index=item_features.index)
    
    interacted_items = user_item_matrix.loc[userId][user_item_matrix.loc[userId] > 0].index
    score_series = score_series.drop(interacted_items)
    
    top_recommendations = score_series.sort_values(ascending=False).head(n)
    recommended_products = products[products['productId'].isin(top_recommendations.index)]
    recommended_products['score'] = recommended_products['productId'].map(top_recommendations)
    
    return recommended_products.sort_values('score', ascending=False)

def get_user_previous_interactions(userId, interactions, products):
    user_interactions = interactions[interactions['userId'] == userId]
    user_interactions = user_interactions.merge(products, on='productId', how='left')
    return user_interactions[['interactionId', 'userId', 'productId', 'interaction_type', 'productName', 'category', 'price']]

def main():
    users, products, interactions = fetch_data()
    
    user_item_matrix = create_user_item_matrix(interactions, products)
    item_features = create_item_feature_matrix(products)
    item_similarity = compute_item_similarity(item_features)
    
    test_user_id = 1  # Example userId for recommendation
    
    user_previous_interactions = get_user_previous_interactions(test_user_id, interactions, products)
    logging.info(f"Previous interactions for user {test_user_id}:")
    logging.info(user_previous_interactions.to_string(index=False))
    
    recommendations = get_top_recommendations(test_user_id, user_item_matrix, item_features, item_similarity, products)
    logging.info(f"\nTop recommendations for user {test_user_id}:")
    logging.info(recommendations.to_string(index=False))

if __name__ == "__main__":
    main()
