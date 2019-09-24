# Toxicity-Online-Conversation-Classification

##  1. Introduction

This project is focus on identify toxicity in online conversations, where toxicity is defined as anything rude, disrespectful
or otherwise likely to make someone leave a discussion.

Build a model that recognizes toxicity and minimizes this type of unintended bias with respect to mentions of identities. 
Using a dataset labeled for identity mentions and optimizing a metric designe to measure unintended bias. 
Develop strategies to reduce unintended bias in machine learning models, and the entire industry, 
build models that work well for a wide range of conversations.

## 2. Enviorment and Packages

This project will mainly use following package:

*  numpy
*  pandas
*  keras


##  3. Significance and Approach

Extracted and clean text data from train dataset.
After tokenizer the train text data, combing two pre-trained embedding matrix use Bidirectional multi-layers LSTM and skip connection
method to build RNN model. 

For more model summary and output, please see Report.md and Output file.

## 4. Repository Structure
*  Input Data
*  Output Result
*  Source Code
*  Report



