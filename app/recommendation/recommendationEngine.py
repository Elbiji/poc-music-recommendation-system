import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

class recommender:
    @staticmethod
    async def recommendation_processor(InputVector: dict):
        # Data setup
        BASE_DIR = Path(__file__).resolve().parent
        df_songs = pd.read_csv(f"{BASE_DIR}" + "/dataset.csv")

        # Reducing complexity by dropping key's column
        df_songs = df_songs.drop(columns=['key','mode'],inplace=False)
        print(df_songs)

        # define scaler and columns to be scaled
        scaler_z = StandardScaler()
        zscore_cols = ['loudness','tempo','speechiness']

        # Apply normalization 
        df_songs[zscore_cols] = scaler_z.fit_transform(df_songs[zscore_cols])

        # Setup query vector
        query_vector_dict = {
            'danceability': InputVector.get('danceability'),
            'energy': InputVector.get('energy'),
            'loudness': InputVector.get('loudness'),
            'speechiness': InputVector.get('speechiness'),
            'acousticness': InputVector.get('acousticness'),
            'instrumentalness': InputVector.get('instrumentalness'),
            'liveness': InputVector.get('liveness'),
            'valence': InputVector.get('valence'),
            'tempo': InputVector.get('tempo')
        }

        # Define feature column for comparison
        feature_cols = list(query_vector_dict.keys())

        # Convert dictionary vector to 2D NumPy array since scikit expects a matrix as an input (Sample(row), Features(columns))
        query_array = np.array([list(query_vector_dict.values())])

        # Convert the relevant dataframe features to a NumPy array
        df_vectors = df_songs[feature_cols].values

        # Flatten the similarity result to make it compatible for dataframe assingments from 2D to 1D 
        similarity_scores = cosine_similarity(query_array, df_vectors).flatten()

        # Similarity score assignment
        df_songs['similarity'] = similarity_scores

        # Sort by similarity score
        df_sorted = df_songs.sort_values(by='similarity', ascending=False)

        # Get 5 songs that has the most similiar result
        top_5_results = df_sorted.head()

        return top_5_results

    @staticmethod
    async def user_preference(track_histories: dict):
        # Removing unused columns
        for track in track_histories:
            track.pop('_id', None)
            track.pop('album_name', None)
            track.pop('song_name', None)
            track.pop('artist_name', None)
            track.pop('user_id', None)
            track.pop('played_at', None)

        # Convert to a dataframe
        features = pd.DataFrame(track_histories)

        # Calculate mean per features
        preference_profile = features.mean()

        return preference_profile.to_dict()
    