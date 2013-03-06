%feature extraction
fid = fopen('../review_polarity_dataset/lexicon.txt', 'r');
while ~feof(fid)
    word = fscanf(fid, '%s', 1);
    tmp = fscanf(fid, '%s', 1);
    value = fscanf(fid, '%f', 1);
    line = fgetl(fid);
end