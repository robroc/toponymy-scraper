import unicodecsv

with open('toponymy_data_new.csv', 'r') as in_file, open('topo_clean_new.csv', 'w') as out_file:
    reader = unicodecsv.reader(in_file)
    writer = unicodecsv.writer(out_file)
    headers = reader.next()
    writer.writerow(headers)
    uniques = []
    for line in reader:
        if line in uniques:
            continue  
        if line[1].startswith("Saint"):
            continue
        if line[6].startswith("La Commission de toponymie n'a pas diffus"):
            continue
        uniques.append(line)    
        writer.writerow(line)
	