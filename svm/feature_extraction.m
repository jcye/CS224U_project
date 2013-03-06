%feature extraction
clear all;
close all;
clc;


fid = fopen('../review_polarity_dataset/lexicon.txt', 'r');
values = [];
N  = 2998;
words = cell(N,1);
count = 0;
while ~feof(fid)
    count = count + 1;
    words{count} = fscanf(fid, '%s', 1);
    tmp = fscanf(fid, '%s', 1);
    value = fscanf(fid, '%f', 1);
    values = [values; value];
    line = fgetl(fid);
end
save('lexicon_matlab', 'words', 'values');