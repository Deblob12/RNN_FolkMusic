import tensorflow as tf 
tf.enable_eager_execution()
import numpy as np
import functools
import utility as util

def vectorizeTables(name, path):
    text = open(tf.keras.utils.get_file(name, path)).read()
    vocab = sorted(set(text))
    char2idx = {u:i for i, u in enumerate(vocab)}
    text_as_int = np.array([char2idx[c] for c in text])
    idx2char = np.array(vocab)
    return char2idx, idx2char, text_as_int, vocab

def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
    model = tf.keras.Sequential([
      tf.keras.layers.Embedding(vocab_size, embedding_dim, 
                                batch_input_shape=[batch_size, None]),
      LSTM(rnn_units), 
      tf.keras.layers.Dense(vocab_size) 
    ])

    return model

def generate_text(model, start_string="X", generation_length=3000, char2idx, idx2char):
    input_eval = [char2idx[s] for s in start_string]
    input_eval = tf.expand_dims(input_eval, 0)
    text_generated = []
    model.reset_states()
    for i in range(generation_length):
        predictions = model(input_eval)
        predictions = tf.squeeze(predictions, 0)
        predicted_id = tf.multinomial(predictions, num_samples=1)[-1,0].numpy()
        input_eval = tf.expand_dims([predicted_id], 0)
        text_generated.append(idx2char[predicted_id])
    return (start_string + ''.join(text_generated))

if __name__ == "__main__":
        
    char2idx, idx2char, text_as_int, vocab = vectorizeTables('irish.abc', 'irish.abc')
    vocab_size = len(vocab)
    embedding_dim = 256
    rnn_units = 1024
    if tf.test.is_gpu_available():
        LSTM = tf.keras.layers.CuDNNLSTM
    else:
        LSTM = functools.partial(
        tf.keras.layers.LSTM, recurrent_activation='sigmoid')

    LSTM = functools.partial(LSTM, 
        return_sequences=True, 
        recurrent_initializer='glorot_uniform',
        stateful=True
    )
    model = build_model(vocab_size, embedding_dim, rnn_units, batch_size=1)
    model.load_weights(tf.train.latest_checkpoint('./training_checkpoints'))
    model.build(tf.TensorShape([1, None]))
    text = generate_text(model, start_string="X", char2idx, idx2char)
    util.save_song(text, 'test')