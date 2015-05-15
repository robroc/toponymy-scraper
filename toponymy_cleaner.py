import unicodecsv

with open('toponymy_data.csv', 'r') as in_file, open('topo_clean.csv', 'w') as out_file:
    reader = unicodecsv.reader(in_file)
    writer = unicodecsv.writer(out_file)
    headers = reader.next()
    writer.writerow(headers)
    uniques = []
    for line in reader:
        if line in uniques:
            continue  
        if line[0].startswith("Saint"):
            continue
        line[3] = line[3].replace(" (Ville)", "")
        if line[4].startswith("La Commission de toponymie n'a pas diffus"):
            continue
        uniques.append(line)    
        writer.writerow(line)
	