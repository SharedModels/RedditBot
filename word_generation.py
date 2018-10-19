from keras.layers import Conv1D, Embedding, Dense, MaxPool1D, Flatten
from keras.models import Sequential, load_model
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from comment_reply import CommentReply
import pickle


class ReplyPredictions:
    def __init__(self, vector_size=50, num_filters=10, hidden_size=100):
        self.vector_size = vector_size
        self.num_filters = num_filters
        self.hidden_size = hidden_size
        self.vocab_size = None
        self.output_size = None
        self.seq_length = None
        self.model = None
        self.tokenizer = None
        self.vec = None
        self.max_length = None

    def build_model(self):
        model = Sequential()
        model.add(Embedding(self.vocab_size, self.vector_size, input_length=self.seq_length))
        model.add(Conv1D(128, kernel_size=5, activation='relu', padding='same'))
        model.add(MaxPool1D())
        model.add(Conv1D(128, kernel_size=3, activation='relu', padding='same'))
        # model.add(MaxPool1D())
        # model.add(Conv1D(128, kernel_size=3, activation='relu'))
        model.add(MaxPool1D())
        model.add(Dense(128, activation='relu'))
        model.add(Flatten())
        model.add(Dense(self.output_size, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    @staticmethod
    def process_data(subreddit, post_limit=1000, text_length=50):
        df = CommentReply(post_limit).collect_comment_reply_sentence_break(subreddit)
        df['text_length'] = df['body'].str.len()
        df = df[df['text_length'] < text_length]
        # print(len(df))
        return df

    @staticmethod
    def find_max_length(sequence):
        a = []
        for current_list in sequence:
            a.append(len(current_list))
        return max(a)

    def tokenize_data(self, df, train=True):
        if train:
            self.tokenizer = Tokenizer()
            self.tokenizer.fit_on_texts(df['body_parent'])
            self.vocab_size = len(self.tokenizer.word_index) + 1

        sequences = self.tokenizer.texts_to_sequences(df['body_parent'])
        if train:
            self.max_length = self.find_max_length(sequences)
        sequences = pad_sequences(sequences, self.max_length, padding='post')
        sequences = np.array(sequences)
        if train:
            self.seq_length = sequences.shape[1]
        return sequences

    def process_y(self, df, vec=TfidfVectorizer(min_df=10, stop_words='english')):
        self.vec = vec
        y = df['body']
        y = vec.fit_transform(y)
        self.output_size = y.shape[1]
        return y

    def train(self, X, y, epochs=10, batch_size=128):
        self.model = self.build_model()
        self.model.fit(X, y, batch_size=batch_size, epochs=epochs)
        return self.model

    def build_data(self, subreddit_input):
        if type(subreddit_input) == list:
            df_list = []
            for subreddit in subreddit_input:
                df_list.append(self.process_data(subreddit))
            df = pd.concat(df_list, axis=0)
        elif type(subreddit_input) == str:
            df = self.process_data(subreddit_input)
        else:
            raise ValueError('subreddit_input must be string or list of strings')
        print(df.shape)
        X = self.tokenize_data(df)
        y = self.process_y(df)
        return X, y

    def save_model(self, model_file_path, dict_file_path):
        self.model.save(model_file_path)
        model_dict = {'tokenizer': self.tokenizer, 'vec': self.vec, 'max_length': self.max_length}
        with open(dict_file_path, 'wb') as f:
            pickle.dump(model_dict, f)
            # pickle.dump(model_dict, dict_file_path)

    def build_transform_save(self, subreddit_input, model_file_path='word_model.q5',
                             model_dict_file_path='model_dict.pickle', epochs=10, batch_size=128):
        X, y = self.build_data(subreddit_input)
        self.train(X, y, epochs, batch_size)
        self.save_model(model_file_path, model_dict_file_path)

    def load_model(self, model_file_path, model_dict_file_path):
        self.model = load_model(model_file_path)
        # pickle.load(model_dict_file_path)
        with open(model_dict_file_path, 'rb') as f:
            model_dict = pickle.load(f)
        self.tokenizer = model_dict['tokenizer']
        self.vec = model_dict['vec']
        self.max_length = model_dict['max_length']

    def handle_predictions(self, predictions, num_words):
        columns = np.argpartition(predictions, -num_words)[:, -num_words:].tolist()
        word_list = self.vec.get_feature_names()

        predicted_words = []
        for sentence in columns:
            predicted_words.append(' '.join([word_list[i] for i in sentence]))
        return predicted_words

    def predict_words(self, text_df, num_words=10, model_filepath='word_model.q5',
                      model_dict_file_path='model_dict.pickle'):
        self.load_model(model_filepath, model_dict_file_path)
        test = self.tokenize_data(text_df, train=False)
        predictions = self.model.predict(test)
        predicted_words = self.handle_predictions(predictions, num_words)
        return pd.DataFrame({'body_parent': text_df['body_parent'].tolist(), 'reply': predicted_words})


if __name__ == '__main__':
    obj = ReplyPredictions()
    obj.build_transform_save(['askreddit', 'news', 'worldnews', 'science', 'personalfinance'],
                             epochs=3)
    # test_df = pd.DataFrame({'body_parent': ['me too thanks', 'i love reddit']})
    test_df = CommentReply(subreddit_post_limit=5).collect_comment_reply('gaming').drop_duplicates('body_parent')
    obj.predict_words(test_df, num_words=20).to_csv('test_pred.csv')
