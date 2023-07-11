import argparse
import re
import magic

# Define Indic Character Groups

 # independent vowels
indVowelTam = r'\u0b85-\u0b94'
indVowelOri = r'\u0b05-\u0b14\u0b60\u0b61'
indVowelTel = r'\u0c05-\u0c14\u0c60\u0c61'
indVowelKan = r'\u0c85-\u0c94\u0ce0\u0ce1'
indVowelMal = r'\u0d05-\u0d14\u0d60\u0d61'
indVowels = indVowelTam + indVowelOri + indVowelTel + indVowelMal + indVowelKan

# vowel modifiers and stress marks (Can appear on an independent vowel)
# Should TAM visarga 0b83 also be included here?
# Should avagraha be handled differently?
# Temporarily included: 0324 (combining diaeresis) until permanent nukta is available
vmodTam = r'\u0b82'
vmodOri = r'\u0b01-\u0b03\u0b4d'  
vmodTel = r'\u0c01-\u0c03\u0c4d'
vmodKan = r'\u0c82-\u0c83\u0cbd'
vmodMal = r'\u0d02-\u0d03\u0d3d'
vmodifiers = r'\u0324' + vmodTam + vmodOri + vmodTel + vmodKan + vmodMal

# consonant modifiers (Can appear on any consonant, even pre-consonants in a cluster)
cmodKan = r'\u0cbc'  # KAN nukta
cmodOri = r'\u0b3c'  # ORI nukta
cmodifiers = r'\u0324' + cmodKan + cmodOri  # Temporarily included: 0324 (combining diaeresis) until permanent nukta is available

# consonants
consTam = r'\u0b95-\u0bb9'
consOri = r'\u0b15-\u0b39\u0b5c\u0b5d\u0b5f\u0b70\u0b71'
consTel = r'\u0c15-\u0c39\u0c58\u0c59'
consKan = r'\u0c95-\u0cb9\u0cde'
consMal = r'\u0d15-\u0d39\u0d7a-\u0d7f'
cons = consTam + consOri + consTel + consMal + consKan

# matras
matraTam = r'\u0bbc-\u0bcc\u0bd7'
matraOri = r'\u0b3e-\u0b4c\u0b56\u0b57\u0b62\u0b63'
matraTel = r'\u0c3e-\u0c4c\u0c55\u0c56\u0c62\u0c63'
matraKan = r'\u0cbe-\u0ccc\u0cd5\u0cd6\u0ce2\u0ce3'
matraMal = r'\u0d3e-\u0d4c\u0d57\u0d62\u0d63'
matras = matraTam + matraOri + matraTel + matraKan + matraMal

# Virama
viramaTam = r'\u0bcd'
viramaOri = r'\u0b4d'
viramaTel = r'\u0c4d'
viramaKan = r'\u0ccd'
viramaMal = r'\u0d4d'
viramas = viramaTam + viramaOri + viramaTel + viramaMal + viramaKan

# Word-forming ranges
wordTAM = r'\u0b81-\u0be3'
wordORI = r'\u0b01-\u0b63\u0b70\u0b71'
wordTEL = r'\u0c01-\u0c63\u0c7f'
wordKAN = r'\u0c81-\u0ce3\u0cf1\u0cf2'
wordMAL = r'\u0d01-\u0d63\u0d7a-\u0d7f'
wordChars = r'\u200c\u200d\u0324' + wordTAM + wordORI + wordTEL + wordKAN + wordMAL 

def fixmal(text, nta=0):
    text = text.replace("ന്‍", "ൻ")
    text = text.replace("ര്‍", "ർ")
    text = text.replace("ള്‍", "ൾ")
    text = text.replace("ണ്‍", "ൺ")
    text = text.replace("ല്‍", "ൽ")
    text = text.replace(u"\u0d15\u0d4d\u200d", u"\u0d7f")
    text = text.replace("ൻ്റ്", "ന്റ്")
    text = text.replace("ൻറ്", "ന്റ്")


def hyphenate(text, hyphenChar='='): 
    '''hyphenates the text and inserts the specified hyphenChar at the identified hyphen points'''

    # Define nonWordChars to also exclude the hyphenChar
    # (Variable name beginning with 'g' indicates Grouping parentheses used.)
    nonWordChar = r"(?:[^\u003d" + hyphenChar + wordChars + "])"
    gNonWordChar = r"([^\u003d" + hyphenChar + wordChars + "]|^|$)"

    # components of syllable patterns
    consPattern = "[" + cons + "][" + cmodifiers + "]*"
    viramasPattern = "[" + viramas + r"][\u200c\u200d\u0324]*"	# Temporarily included: 0324 (combining diaeresis) until permanent nukta is available
    optMatras = "[" + matras + vmodifiers + "]*"

    # Syllable patterns
    syllPattern1 = "(?:(?:" + consPattern + viramasPattern + ")*" + consPattern + optMatras + ")"
    syllPattern2 = "(?:(?:" + consPattern + viramasPattern + ")*" + consPattern + viramasPattern + "(?=" + nonWordChar + "))"
    syllPattern3 = "(?:[" + indVowels + "][" + vmodifiers + "]*)"
    gSyllPattern = "(" + syllPattern1 + "|" + syllPattern2 + "|" + syllPattern3 + ")"

    # Remove existing separators
    text = re.sub(r"[\u003d\u200b\u00ad]", "", text) 

    # Begin by inserting a break before EVERY syllable
    text = re.sub(gSyllPattern, hyphenChar + r'\1', text)

    # Remove break at start of word
    text = re.sub(gNonWordChar + hyphenChar, r'\1', text) 
    
    # Remove break after 1st syllable. (Must have at least 2 syll before break.)
    text = re.sub(gNonWordChar + gSyllPattern + hyphenChar, r'\1\2', text) 

    # Remove break before last syllable. (Must have at least 2 syll after break.)
    text = re.sub(hyphenChar + gSyllPattern + gNonWordChar, r'\1\2', text)     
    
    # Remove break before MAL atomic chillu  \u0d7a-\u0d7f
    text = re.sub(hyphenChar + r"(?=[\u0d7a-\u0d7f])" , '', text)     

    # Remove break before MAL old-style chillu 
    text = re.sub(hyphenChar + r"(?=[\u0d23\u0d28\u0d30\u0d32\u0d33\u0d15]\u0d4d\u200d)" , '', text)     

    text = text.replace("=", u'\u00AD')
    return text

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage='parafix [options] -i/--input inputfile -o/--out [outfile]',
        description='Generates a hyphenated text from the input file'
    )

    parser.add_argument('-i',
                        '--input',
                        type=str,
                        required=True,
                        nargs=1,
                        help="Input Filename: Must be a text file")
    
    parser.add_argument('-o',
                        '--output',
                        type=str,
                        nargs=1,
                        help="Output Filename: (Optional) If left blank, out_filename will be the infilename +  '_hyphen'.")
    
    args = parser.parse_args()

    infile = args.input[0]
    filetype = magic.from_file(infile, mime=True)
    infile = infile.strip(".\\")
    infile=infile.split(".")

    try:
        outfile = args.output[0]  
    except:
        outfile = f"{infile[0]}_hyphenated.{infile[-1]}"
    
    if filetype.split("/")[0] == "text":
        try:
            f = open(f'.\\{".".join(infile)}', mode="r", encoding="utf-8")
            fc = f.read()
            o = open(outfile, mode="w", encoding="utf-8")
            o.write(hyphenate(fixmal(fc)))
            o.close()
        except Exception as e:
            print(e)
    else:
        print(f'Sorry! {filetype} is not currently supported.')

