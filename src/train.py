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

def generateSequences(seq_length, text_as_int):
    char_dataset = tf.data.Dataset.from_tensor_slices(text_as_int)
    sequences = char_dataset.batch(batch_size=seq_length+1, drop_remainder=True)
    return sequences

def split_input_target(chunk):
    input_text =  chunk[:-1]
    target_text = chunk[1:]
    return input_text, target_text

def trainingBatches(batch_size, buffer_size, dataset):
    dataset = dataset.shuffle(buffer_size).batch(batch_size, drop_remainder=True)
    return dataset

def compute_loss(labels, logits):
    return tf.keras.backend.sparse_categorical_crossentropy(labels, logits, from_logits=True)

def build_model(vocab_size, embedding_dim, rnn_units, batch_size):
    model = tf.keras.Sequential([
      tf.keras.layers.Embedding(vocab_size, embedding_dim, 
                                batch_input_shape=[batch_size, None]),
      LSTM(rnn_units), 
      tf.keras.layers.Dense(vocab_size) 
    ])

    return model

def train(epochs, model):
    optimizer = tf.train.AdamOptimizer()
    checkpoint_dir = './training_checkpoints'
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt_{epoch}")
    for epoch in range(epochs):
        for inp, target in dataset:
            with tf.GradientTape() as tape:
                predictions = model(inp)
                loss = compute_loss(target, predictions)
            grads = tape.gradient(loss, model.trainable_variables)
            optimizer.apply_gradients(zip(grads, model.trainable_variables))
            print(loss.numpy().mean())
        model.save_weights(checkpoint_prefix.format(epoch=epoch))

def generate_text(model, start_string="X", generation_length=2000, char2idx, idx2char):
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

if __name__ == '__main__':
    char2idx, idx2char, text_as_int, vocab = vectorizeTables('irish.abc', '../data/irish.abc')
    sequences = generateSequences(100, text_as_int)
    dataset = sequences.map(split_input_target)
    dataset = trainingBatches(64, 10000, dataset)
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
    model = build_model(len(vocab), embedding_dim, rnn_units, 64)
    train(5, model)
