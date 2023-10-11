inputfile = "D:\phd-data\NER-annotation-data\German\annotated-data-set\bio\5-folds\fold1.bio"
outputfile = "D:\phd-data\NER-annotation-data\German\annotated-data-set\xml\5-folds\fold1.xml"

with open (inputfile, "r", encoding="utf-8") as f:
    data = f.readlines()
    output = ""
    for line in data:
        try:
            line = line.split()
            if line[-1] != "O":
                line = "<" + line[-1] + ">" + line[0] + "</" + line[-1] + ">"
            else:
                line = line[0]
            output += line + " "
        except:
            output += "\n"

    x = output.count("<I-")
    x += 1
    while x >0:
        try:
            tag = output.index("<I-")
            tag = str(output[tag-9:tag+7])
            output = output.replace(tag, " ")
            x -= 1
        except:
            break

with open(outputfile, "w", encoding="utf-8") as p:
    p.write(output.replace(" .", ".").replace("B-", "").replace("I-", ""))



