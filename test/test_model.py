from app.model.songFeatures import generate_random_feature

NUM_ITERATIONS = 50


def test_generate_random_feature():
    for _ in range(NUM_ITERATIONS):
        feature = generate_random_feature()

        assert 0.55 <= feature.danceability <= 0.85
        assert -12.0 <= feature.loudness <= -6.0
        assert 90 <= feature.tempo <= 150
        assert feature.mode in (0, 1)
        assert 0 <= feature.key <= 11
        assert -12.0 <= feature.loudness <= -6.0
        assert 0.03 <= feature.speechiness <= 0.1
        assert 0.0 <= feature.instrumentalness <= 0.5
        assert 0.08 <= feature.liveness <= 0.25
        assert 0.4 <= feature.valence <= 0.8
        assert 90 <= feature.tempo <= 150
        assert isinstance(feature.danceability, float)
        assert isinstance(feature.tempo, int)
