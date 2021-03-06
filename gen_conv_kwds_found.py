#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construct conversations from STT responses of IBM service."""

import os
import json
import datetime


def load_json(json_pathfile):
    """Load JSON file."""
    with open(json_pathfile) as json_file:
        string_json = json_file.read()
        string_json = string_json.replace('\t', '').replace('\n', ' ')
        data_json = json.loads(string_json)
    return data_json


def find_speaker(speaker_labels, from_time, to_time):
    """Return the number of speaker."""
    speaker = -1
    for sp_block in speaker_labels:
        if from_time >= sp_block['from'] and from_time <= sp_block['to']:
            return sp_block['speaker']
        elif to_time >= sp_block['from'] and to_time <= sp_block['to']:
            return sp_block['speaker']
        elif abs(from_time - sp_block['to']) <= 0.5:
            return sp_block['speaker']
        elif abs(from_time - sp_block['from']) <= 0.5:
            return sp_block['speaker']
    if speaker == -1:
        print("from_time = ", from_time)
        print("to_time = ", to_time)
        print("error here")
    return speaker


def get_time(num_seconds):
    time = datetime.timedelta(seconds=float(num_seconds+0.000001))
    return str(time)[:-4]


def extract_conversation(json_data):
    """Construct the conversation linking 'results' and 'speaker_labels'."""
    results = json_data['results']
    speaker_labels = json_data['speaker_labels']
    # Only once
    conversation = []
    init_text_time = json_data['speaker_labels'][0]['from']
    final_text_time = json_data['speaker_labels'][0]['to']
    speaker = json_data['speaker_labels'][0]['speaker']
    text_speaker = ""
    # For all results
    for result in results:
        timestamps = result['alternatives'][0]['timestamps']
        for timestamp in timestamps:
            word = timestamp[0]
            from_time = timestamp[1]
            to_time = timestamp[2]
            speaker_current = find_speaker(speaker_labels, from_time, to_time)

            if speaker_current == speaker:
                text_speaker += f"{word} "
                final_text_time = to_time
            else:
                text_speaker = text_speaker.strip()
                conversation.append([init_text_time, speaker, text_speaker, final_text_time])
                text_speaker = f"{word} "
                speaker = speaker_current
                init_text_time = from_time
                final_text_time = to_time

    text_speaker = text_speaker.strip()
    conversation.append((init_text_time, speaker, text_speaker, final_text_time)) #Adding last line
    return conversation


def extract_keywords(data_json, json_file):
    """Construct the conversation linking 'results' and 'speaker_labels'."""
    #print(data_json)
    results = data_json['results']
    speaker_labels = data_json['speaker_labels']
    keywords_found = []
    for result in results:
        #print("result = ", result)
        if 'keywords_result' in result:
            keywords_result = result['keywords_result']
            for keyword in keywords_result:
                start_time = keywords_result[keyword][0]['start_time']
                end_time = keywords_result[keyword][0]['end_time']
                speaker = find_speaker(speaker_labels, start_time, end_time)
                keywords_found.append((start_time, speaker, keyword, end_time))
    return keywords_found


def save_extracted_data(keywords_found, json_file, folder, label):
    """Save conversation in '*.txt' file."""
    name_file = os.path.splitext(json_file)[0]
    filepath = f'{folder}/{label}_{name_file}.txt'
    filepath_rw = open(filepath, 'w+')
    for elem in keywords_found:
        filepath_rw.write("[{}] - Speaker {}: {} - [{}]\n\n".format(get_time(elem[0]), elem[1], elem[2], get_time(elem[3])))
    filepath_rw.close()


def main():
    """Load JSON files, construct the dialogue and after save them in 'conversations' folder."""
    for json_file in os.listdir('json'):
        json_pathfile = os.path.join('json', json_file)
        if os.path.isfile(json_pathfile):
            print(json_pathfile)
            json_data = load_json(json_pathfile)
            if len(json_data['results']) > 0:
                conversation = extract_conversation(json_data)
                keywords_found = extract_keywords(json_data, json_file)
                save_extracted_data(conversation, json_file, "conversations", "conv")
                save_extracted_data(keywords_found, json_file, "keywords_found", "kwds")


if __name__ == '__main__':
    main()
