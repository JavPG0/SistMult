import pandas as pd
import unidecode
import re
from rapidfuzz import process, fuzz
from sklearn import preprocessing
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import KNNImputer

class Preproceso:

    def normalize_name(self, s):

        if not isinstance(s, str):
            salida = ""
        else:
            s = s.lower().strip()
            s = unidecode.unidecode(s)               # eliminar acentos
            s = re.sub(r"\s*\(.*?\)\s*", "", s)     # eliminar paréntesis y contenido
            s = s.replace("&", "and").replace("-", " ")  # uniformar separadores
            s = re.sub(r"feat\.|ft\.", "feat", s)   # uniformar colaboraciones
            s = re.sub(r"\s+", " ", s)              # colapsar espacios
            salida = s
        return salida

    def get_first_letter(self, s):
        return s[0] if isinstance(s, str) and len(s) > 0 else "_"

    def fast_fuzzy_match(self, df_source, df_target, threshold=60):
        results = []
        for letter in df_source['first_letter'].unique():
            src_subset = df_source[df_source['first_letter'] == letter]
            tgt_subset = df_target[df_target['first_letter'] == letter]
            if tgt_subset.empty:
                results.extend([None] * len(src_subset))
                continue

            # Calcula matriz de similitud usando token_sort_ratio
            score_matrix = process.cdist(
                src_subset['artist_track'].tolist(),
                tgt_subset['artist_track'].tolist(),
                scorer=fuzz.token_sort_ratio,
                workers=-1  # multiproceso
            )

            # Tomamos la mejor coincidencia para cada fila
            best_indices = score_matrix.argmax(axis=1)
            best_scores = score_matrix.max(axis=1)
            matched = [
                tgt_subset.iloc[idx]['artist_track'] if score >= threshold else None
                for idx, score in zip(best_indices, best_scores)
            ]
            results.extend(matched)
        return results

    def preprocesar(self, Spotify_Youtube, Track_Emotions, Track_Genres):

        # Aplicamos normalización a los datasets
        Spotify_Youtube['artist_name'] = Spotify_Youtube['Artist'].astype(str).apply(self.normalize_name)
        Spotify_Youtube['track_name']  = Spotify_Youtube['Track'].astype(str).apply(self.normalize_name)

        Track_Genres['artist_name'] = Track_Genres['artists'].astype(str).apply(self.normalize_name)
        Track_Genres['track_name']  = Track_Genres['track_name'].astype(str).apply(self.normalize_name)
        Track_Genres = Track_Genres.rename(columns={'track_genre': 'genre'})
        Track_Genres['genre'] = Track_Genres['genre'].astype(str).str.strip()  # eliminar espacios al inicio y final

        Track_Emotions['artist_name'] = Track_Emotions['artist'].astype(str).apply(self.normalize_name)
        Track_Emotions['track_name']  = Track_Emotions['track'].astype(str).apply(self.normalize_name)

        # ============================================
        # Crear columnas combinadas (artista + canción)
        # ============================================

        # Combinamos artista y canción en una sola columna para facilitar comparaciones
        Spotify_Youtube['artist_track'] = Spotify_Youtube['artist_name'] + ' - ' + Spotify_Youtube['track_name']
        Track_Genres['artist_track'] = Track_Genres['artist_name'] + ' - ' + Track_Genres['track_name']
        Track_Emotions['artist_track'] = Track_Emotions['artist_name'] + ' - ' + Track_Emotions['track_name']

        # Eliminamos duplicados en los datasets de géneros y emociones
        Track_Genres_Unique = Track_Genres.drop_duplicates(subset=['artist_track'], keep='first').copy()
        Track_Emotions_Unique = Track_Emotions.drop_duplicates(subset=['artist_track'], keep='first').copy()

        # ============================================
        # Coincidencia difusa optimizada (compatible con rapidfuzz 3.x)
        # ============================================

        Spotify_Youtube['first_letter'] = Spotify_Youtube['artist_name'].apply(self.get_first_letter)
        Track_Genres_Unique['first_letter'] = Track_Genres_Unique['artist_name'].apply(self.get_first_letter)
        Track_Emotions_Unique['first_letter'] = Track_Emotions_Unique['artist_name'].apply(self.get_first_letter)

        # Ejecutamos coincidencias difusas
        Spotify_Youtube = Spotify_Youtube.copy()
        Spotify_Youtube['match_genre'] = self.fast_fuzzy_match(Spotify_Youtube, Track_Genres_Unique, threshold=60)
        Spotify_Youtube['match_emotion'] = self.fast_fuzzy_match(Spotify_Youtube, Track_Emotions_Unique, threshold=60)

        # ============================================
        # Merge con géneros y emociones
        # ============================================

        # Hacemos merge de los datos de género basados en la coincidencia difusa
        Unified = pd.merge(
            Spotify_Youtube,
            Track_Genres_Unique[['artist_track', 'genre', 'popularity', 'mode', 'time_signature']],
            left_on='match_genre',
            right_on='artist_track',
            how='left',
            suffixes=('', '_genre')
        )

        # Hacemos merge de los datos de emoción basados en la coincidencia difusa
        Unified = pd.merge(
            Unified,
            Track_Emotions_Unique[['artist_track', 'seeds', 'number_of_emotion_tags', 'valence_tags', 'arousal_tags', 'dominance_tags']],
            left_on='match_emotion',
            right_on='artist_track',
            how='left',
            suffixes=('', '_emotion')
        )

        # Limpiamos columnas innecesarias que quedaron del merge
        Unified = Unified.drop(columns=['artist_track_genre', 'artist_track_emotion'], errors='ignore')

        # Eliminar columnas que no sirven una vez hecho el merge
        Unified.drop(columns=['match_emotion', 'match_genre', 'Artist', 'track_name', 'first_letter'], inplace=True)

        # ============================================
        # RELLENO DE VALORES FALTANTES
        # ============================================
        # Columnas numéricas con KNN
        num_cols = ['popularity', 'mode', 'time_signature', 'valence_tags', 'arousal_tags', 'dominance_tags', 'number_of_emotion_tags']
        imputer = KNNImputer(n_neighbors=5)
        Unified[num_cols] = imputer.fit_transform(Unified[num_cols])

        # Columnas categóricas con moda
        cat_cols = ['genre', 'seeds']
        for col in cat_cols:
            global_mode = Unified[col].mode()[0]
            Unified[col] = Unified.groupby('artist_name')[col].transform(
                lambda x: x.fillna(x.mode()[0] if not x.mode().empty else global_mode)
            )
            Unified[col] = Unified[col].fillna(global_mode, inplace=True)

        # Seleccionar solo columnas numéricas
        # uso de MinMax para normalizar los valores numericos
        numeric_cols = Unified.select_dtypes(include=['float64', 'int64']).columns
        min_max_scaler = MinMaxScaler()
        Unified[numeric_cols] = min_max_scaler.fit_transform(Unified[numeric_cols])

        return Unified
