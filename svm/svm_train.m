addpath('../../liblinear-1.92/matlab');  % add LIBLINEAR to the path
%[sparseTrainMatrix, trainCategory] = readMatrix('../feature/feature_train.txt');

%numTrainDocs = size(sparseTrainMatrix, 1);
%numTokens = size(sparseTrainMatrix, 2);

% sparseTrainMatrix is a (numTrainDocs x numTokens) sparse matrix.
% Each row represents a unique document (email).
% The j-th column of the row $i$ represents the number of times the j-th
% token appeared in email $i$. 

% tokenlist is a long string containing the list of all tokens (words).
% These tokens are easily known by position in the file TOKENS_LIST

% trainCategory is a (1 x numTrainDocs) vector containing the true 
% classifications for the documents just read in. The i-th entry gives the 
% correct class for the i-th email (which corresponds to the i-th row in 
% the document word matrix).

% Spam documents are indicated as class 1, and non-spam as class 0.
% Note that for the SVM, you would want to convert these to +1 and -1.

% Note that the train function for LIBLINEAR uses the sparse matrix 
% representation of the document word matrix, which is stored in sparseTrainMatrix.
% Additionally, it expects the labels to be a regular vector
% of dimension (numTrainDocs x 1).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% svm_train.m
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% YOUR CODE HERE

dataset_imdb = load('../feature/feature_train.txt');
trainCategory = dataset_imdb(:,1);
sparseTrainMatrix = sparse(dataset_imdb(:, 1:end));

svm_category_train = 2.*trainCategory - 1;
model = train(svm_category_train, sparseTrainMatrix, '-s 1');