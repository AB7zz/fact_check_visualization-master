###########################################################################################################################
#  This file loads BERT embeddings and extracts the embedding of a given sentence (claim) and sentences of a full article #
#  This code also ranks the sentences of a given article based on their similarity to a given claim                       #
#  The input is given to find_most_similar(article, claim), the output is ranked sentences based on similarity to cliam   #
#  ______________________________________________________________________________________________________________________ #
#  Author : Israa Qasim Jaradat , IDIR lab, University of Texas at Arlington                                              #
###########################################################################################################################

import torch
from pytorch_pretrained_bert import BertTokenizer, BertModel, BertForMaskedLM
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize


# a sentence in an article body
class Article_sent:
    def __init__(self,text):
        self.text = text
        self.vector =None
        self.similarity = 0.0



print ("Initializing BERT ...")
# Load pre-trained model tokenizer (vocabulary)
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# Load pre-trained model (weights) Calling from_pretrained will fetch the model from the internet. The model is a deep neural network with 12 layers!
model = BertModel.from_pretrained('bert-base-uncased')
# Put the model in "evaluation" mode, meaning feed-forward operation. as opposed to training mode. In this case, evaluation mode turns off dropout regularization which is used in training.
model.eval()


# called by find_most_similar(claim)
# sentence_embedding =
MAX_SEQ_LENGTH = 512
def get_sentence_vector(sentence):
    marked_text = "[CLS] " + sentence + " [SEP]"
    tokenized_text = tokenizer.tokenize(marked_text)
    tokenized_text = tokenized_text[:MAX_SEQ_LENGTH]

    #list(tokenizer.vocab.keys())[5000:5020]

    indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)

    segments_ids = [1] * len(tokenized_text)

    # Convert inputs to PyTorch tensors The BERT PyTorch interface requires that the data be in torch tensors rather than Python lists
    tokens_tensor = torch.tensor([indexed_tokens])
    segments_tensors = torch.tensor([segments_ids])

    #Next, let’s fetch the hidden states of the network.

    # Predict hidden states features for each layer
    with torch.no_grad():
        encoded_layers, _ = model(tokens_tensor, segments_tensors)

    # Convert the hidden state embeddings into single token vectors

    # Holds the list of 12 layer embeddings for each token
    # Will have the shape: [# tokens, # layers, # features]
    token_embeddings = []
    batch_i=0
    # For each token in the sentence...
    for token_i in range(len(tokenized_text)):

        # Holds 12 layers of hidden states for each token
        hidden_layers = []

        # For each of the 12 layers...
        for layer_i in range(len(encoded_layers)):
            # Lookup the vector for `token_i` in `layer_i`
            vec = encoded_layers[layer_i][batch_i][token_i]

            hidden_layers.append(vec)

        token_embeddings.append(hidden_layers)

    # Sanity check the dimensions:
    #print("Number of tokens in sequence:", len(token_embeddings))
    #print("Number of layers per token:", len(token_embeddings[0]))

    #concatenated_last_4_layers = [torch.cat((layer[-1], layer[-2], layer[-3], layer[-4]), 0) for layer in token_embeddings] # [number_of_tokens, 3072]
    #summed_last_4_layers = [torch.sum(torch.stack(layer)[-4:], 0) for layer in token_embeddings] # [number_of_tokens, 768]

    sentence_embedding = torch.mean(encoded_layers[11], 1)

    return sentence_embedding




# called by analyze_article() in google_search
# returns relevant_sentences = [relevant sentences from the article in order of similarity]
def find_most_similar(article, claim):
    relevant_sentences = []
    print("Finding most relevant sentences ...")
    claim_vector = get_sentence_vector(claim)
    # sentence_tokens = [sentencefromarticle, sentencefromarticle, sentencefromarticle]
    sentence_tokens = sent_tokenize(article)
    #  if more than 5 sentences then only we
    if len(sentence_tokens) > 5:
        sentences = []
        for sent in sentence_tokens:
            if sent != '.':
                s = Article_sent(sent)
                s.vector = get_sentence_vector(s.text)
                # checks sentences in the article with the sentences in the claim
                s.similarity =  cosine_similarity(s.vector, claim_vector)
                sentences.append(s)


        most_similar_sentences = sorted(sentences, key=lambda x: x.similarity,reverse=True)

        for sent in most_similar_sentences:
            relevant_sentences.append(sent.text)
        return relevant_sentences
    else:
        return None, None


