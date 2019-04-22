Vanya Cohen and Oliver Hare

One shot learning on the omniglot dataset (not included)

https://www.cs.cmu.edu/~rsalakhu/papers/oneshot1.pdf

data_processing.py
  contains util methods for loading data

siamese_cnn.py
  contains the cnn, training, and testing code

—————————————————————————————————————————————————————————————————

usage: siamese_cnn.py [-h] [--train] [-learningrate LEARNINGRATE]
                      [-epochs EPOCHS]

siamese cnn for one shot classification

optional arguments:
  -h, --help            show this help message and exit
  --train               include to train the model, leave out to test
  -learningrate LEARNINGRATE
                        Learning rate
  -epochs EPOCHS        Epochs to train for
