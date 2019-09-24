## Learning Algorithm

Long short-term memory (LSTM) is an artificial recurrent neural network (RNN) architecture used in the field of deep learning. 
Unlike standard feedforward neural networks, LSTM has feedback connections. 
It can not only process single data points (such as images), but also entire sequences of data (such as speech or video). 
For example, LSTM is applicable to tasks such as unsegmented, connected handwriting recognition or speech recognition.
LSTMs were developed to deal with the exploding and vanishing gradient problems that can be encountered when training traditional RNNs. 
Relative insensitivity to gap length is an advantage of LSTM over RNNs.


Word embedding is the collective name for a set of language modeling and feature learning techniques in natural language processing (NLP) 
where words or phrases from the vocabulary are mapped to vectors of real numbers. 
Conceptually it involves a mathematical embedding from a space with many dimensions per word to a continuous vector space with a much lower dimension.


Residual neural networks do this by utilizing skip connections, or short-cuts to jump over some layers. 
Typical ResNet models are implemented with double- or triple- layer skips 
that contain nonlinearities (ReLU) and batch normalization in between.
One motivation for skipping over layers is to avoid the problem of vanishing gradients, 
by reusing activations from a previous layer until the adjacent layer learns its weights.

## Model Summary

The overall train accuracy is near 0.95, test accuracy is near 0.93. 
This Model is using keras package to bulid. For each neura in RNNR is LSTM combine SpatialDropout regularization method. 
After 2 Bidirectional layers LSTM, build 2 skip connection layers and each skip 2 layers. 

*  Hyperparameters

   Drop rate: 0.25
   
   Lstm units: 128
   
   Dense units: 4 * 128
   
   Activation: relu and tanh
   
   Batch size: 512
   
   Learning Rate: lambda function with 1e-3 * (0.6 ** global_epoch)
   
For more model information please see output file.


##  Future Improvements and Plans

*  Fine Tune Parameters --- In this model, I only run 1 epoch for each fit times and also applied lots of regularization methos.
   Thus this model don't have obvious onverfiting problem. However, to keep improve train accuracy adding more layers or increase
   neuras maybe will improve accurcay. 
