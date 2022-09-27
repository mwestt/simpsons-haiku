import re
import json
import syllapy
import syllables
import warnings
import pandas as pd
import numpy as np
from tqdm import tqdm
from nltk.corpus import cmudict

warnings.simplefilter(action='ignore', category=(FutureWarning, pd.errors.DtypeWarning))

class SimpsonsHaiku():


    def __init__(self, haiku_df=None):
        self.file_path = 'dataset/simpsons_script_lines.csv'
        self.strip_list = [',', '.', '?', '!', ':', '\\', '"']
        self.nltk_dict = cmudict.dict()
        self.syllapy_dict = syllapy.WORD_DICT
        self.simpson_dict = json.load(open('simpson_lect.json'))
        self.script = self.load_script()
        self.haiku_df = haiku_df


    def load_script(self, 
                    on_bad_lines='skip',
                    speaking_only=True):
        """Load Simpsons script into pandas DataFrame."""

        tqdm.pandas()
        script_lines = pd.read_csv(self.file_path, on_bad_lines=on_bad_lines,
                                   dtype={'speaking_lines' : bool})
        
        # Data cleaning on speaking lines
        script_lines['speaking_line'] = script_lines['speaking_line'].replace({'true': True, 'false': False})

        if speaking_only:
            script_lines = script_lines[script_lines['speaking_line'] == True]
            script_lines = script_lines[~script_lines['normalized_text'].isna()]

        # Cleaning missing values
        script_lines[['location_id', 'character_id']] = script_lines[['location_id', 'character_id']].fillna(-1)
        script_lines['raw_character_text'] = script_lines['raw_character_text'].fillna('Missing Character')
        script_lines['raw_location_text'] = script_lines['raw_location_text'].fillna('Missing Location')

        # Split longer lines of dialogue based on delimiters and explode to longer format
        script_lines['spoken_words_split'] = script_lines['spoken_words'].str.replace('?', '.').str.replace('!', '.').str.replace('/', '.').str.split('.')  # split on '.!?/', but could extend to ':;,'
        # TODO Regex version instead? Keep (multiple) delimiters? Exclude Mr. etc.
        # script_lines['spoken_words_split'] = script_lines['spoken_words'].apply(lambda x: re.split('[?!/]', x))  # split on '.!?/', but could extend to ':;,'

        script_lines['number_in_line'] = script_lines['spoken_words_split'].apply(lambda x: [i for i in range(1, len(x)+1)])
        script_lines = script_lines.explode(['spoken_words_split', 'number_in_line'])

        # Order by episode then line sequence
        script_lines = script_lines.sort_values(['episode_id', 'number', 'number_in_line'])

        script_lines['n_syllables'] = script_lines.spoken_words_split.progress_apply(self.count_syllables_line)
        script_lines = script_lines[script_lines.n_syllables > 0]

        return script_lines


    def num_syllables(self, word):
        """Number of syllables using NLTK. Props to user hoju (!) at `https://stackoverflow.com/a/4103234`."""
        
        for char in self.strip_list:
            word = word.replace(char, '')
        word = word.lower()
     
        if word in self.simpson_dict:
            n_syl = self.simpson_dict[word]
        elif word in self.nltk_dict.keys():
            n_syl = [len(list(y for y in x if y[-1].isdigit())) for x in self.nltk_dict[word]][0]
        elif word[-1] == 's' and word[:-1] in self.nltk_dict.keys():
            n_syl = [len(list(y for y in x if y[-1].isdigit())) for x in self.nltk_dict[word[:-1]]][0]
        elif word in self.syllapy_dict:
            n_syl = self.syllapy_dict[word]
        else:  # Resort to estimation
            n_syl = syllables.estimate(word)

        return max(1, n_syl)


    def count_syllables_line(self, line, return_list=False):
        """"Count number of syllables in a line. Return either the final count or a list of cumulative counts from 
        constituent words.
        """

        words = line.lower().replace('-', ' ').replace('/', ' ').split(' ')
        count = 0

        count_list = []
        for word in words:
            for char in self.strip_list:
                word = word.replace(char, '')
            if word:
                n_syllables = self.num_syllables(word)
            else:
                n_syllables = 0 
            count += n_syllables
            count_list.append(count)
        
        if return_list:
            return count_list
        else:
            return count


    def generate_haiku_df(self, save=False):
        """Generate DataFrame of haikus from corpus."""
        
        haiku_list = []
        for i in tqdm(range(len(self.script))):
            for j in range(i+1, min(i+17, len(self.script))):  # Brute force-ish, could be optimized
                if self.script.n_syllables.iloc[i:j].sum() == 17:
                    aggregated_df = self.script.iloc[i:j].groupby('episode_id').agg(list)  # Select 17-syllable sequences from same episode
                    if aggregated_df.shape[0] == 1:
                        aggregated_df.spoken_words_split = ' '.join(aggregated_df.spoken_words_split.values[0])
                        haiku_list.append(aggregated_df)

        haiku_df = pd.concat(haiku_list)

        # Check for parsability, requiring no word-breaks to confirm to 5-7-5 structure
        haiku_df = haiku_df[haiku_df.spoken_words_split.progress_apply(self.is_parsable_as_haiku)]
        
        self.haiku_df = haiku_df

        if save:
            haiku_df.to_csv('haiku_df.csv')

        return haiku_df


    def is_parsable_as_haiku(self, word_string):
        """Return True if string can be parsed as a haiku."""
        count_list = self.count_syllables_line(word_string, return_list=True)
        
        return (count_list[-1]==17) and (5 in count_list) and (12 in count_list)


    def generate_haiku(self, return_list=False, syllable_patterns=[[5,7,5]]):
        """Using an either an exisiting haiku DataFrame or generating one, sample 
        a haiku, parsed in the 5-7-5 line format. Either return as a list or as a
        string delimited with newline characters.
        """

        if self.haiku_df:
            if isinstance(self.haiku_df, str):
                haiku_df = pd.read_csv(self.haiku_df, converters={'n_syllables': eval})
            elif isinstance(self.haiku_df, pd.DataFrame):
                haiku_df = self.haiku_df
            else:
                raise ValueError('`haiku_df` must be of type `str` or `DataFrame`')
        else:
            haiku_df = self.generate_haiku_df(save=True)

        # Select for specific syllable pattern
        haiku_df = haiku_df[haiku_df.n_syllables.apply(lambda x: x in syllable_patterns)]

        haiku = haiku_df.sample().spoken_words_split.values[0]
        words = haiku.replace('-', ' ').replace('/', ' ').split(' ')
        
        count = 0

        haiku_list = ['', '', '']
        syllable_list = [5, 12, 17]

        i = 0
        for word in words:
            for char in self.strip_list:
                word = word.replace(char, '')
            if word:
                n_syllables = self.num_syllables(word)
            else:
                n_syllables = 0 
            count += n_syllables
            
            if count > syllable_list[i]:
                i+=1
            
            haiku_list[i] += word + ' '
        
        haiku_list = [line.strip() for line in haiku_list]

        if return_list:    
            return haiku_list
        else:
            return '\n'.join(haiku_list)


if __name__=='__main__':
    simpsons_haiku = SimpsonsHaiku('haiku_df.csv')
    haiku = simpsons_haiku.generate_haiku()
    print(haiku)
    