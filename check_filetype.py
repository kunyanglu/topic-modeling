import os
import numpy as np
import cv2
import pydicom as dicom
import json
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances

def categorize(path):
    
    file_labels_all_folders = {}
    path = 'dcm_data'
    folder_ids = ['22444_20180404', '20198_20180511', '20218_20171201', 
                '21104_20180322', '15751_20180728', '10377_20180815', 
                '14369_20180420', '10651_20171118', '20596_20171118', 
                '10026_20171208']
    
    for folder_id in folder_ids:
        for dirs, _, files in os.walk(f'{path}/{folder_id}'):
            file_id = dirs.split('/')[1]
        
        file_labels_folder_i = compare_files(files, {}, f'{path}/{folder_id}')
        file_labels_all_folders[folder_id] = file_labels_folder_i
    
    with open('ind_categories.json', 'w') as f:
        json.dump(file_labels_all_folders, f)
        f.close()

def compare_files(files, file_labels, img_path):

    for fileA in files:
        dsA = dicom.dcmread(f'{img_path}/{fileA}')
        pixel_array_A = format_pixel_array(dsA.pixel_array)

        for fileB in files[1:]:
            dsB = dicom.dcmread(f'{img_path}/{fileB}')
            pixel_array_B = format_pixel_array(dsB.pixel_array)
            
            cos_similarity = cosine_similarity(pixel_array_A.reshape(1,-1),
                                            pixel_array_B.reshape(1,-1))

            update_file_labels(cos_similarity, fileA, fileB, file_labels)

    return file_labels

def format_pixel_array(pixel_array):

    if pixel_array.ndim == 3:
        return pixel_array.ndim

    elif pixel_array.ndim == 4:
        # suppose shape = (52, 720, 960, 3)
        # then return averaged pixel values over 52 frames
        return np.mean(pixel_array, axis=0)

def update_file_labels(cos_similarity, fileA, fileB, file_labels):

    '''
    fileA and fileB are similar
        * both fileA and fileB are uncategorized files
            - create one new label
        * either fileA or fileB has already been categorized
            - append the new file to existing list of file ids under the correps category
        * both are categorized
            - great!

    fileA and fileB are not similar
        * both fileA and fileB are new uncategorized files
            - create two different labels
            - append each to its own list under its label
        * either fileA or fileB has already been categorized
            - create 1 new label for the uncategorized file
        * both are categorized
            - hooray~ 
    '''
    threshold = 0.9
    
    # fileA and file B are similar types
    if cos_similarity > threshold:
        
        # both fileA and fileB are uncategorized files
        if fileA not in file_labels.values() and fileB not in file_labels.values():
            
            new_label = len(file_labels)+1)
            file_labels[str(new_label)] = [fileA, fileB]
            
        # either fileA or fileB has already been categorized        
        elif fileA in file_labels.values() or fileB in file_labels.values():

            categorized_file = fileA if fileA in file_labels.values() else fileB
            new_file = [fileA, fileB].remove(categorized_file)[0]

            for label, files in file_labels.items():
                if categorized_file in files:
                    new_label = int(label)+1
                    break
            file_labels[str(file_labels)].extend([new_file]) 
    
    # fileA and fileB are not similar types
    else:
        # both fileA and fileB are uncategorized files
        if fileA not in file_labels.values() and fileB not in file_labels.values():
             new_label_1, new_label_2 = len(file_labels)+1, len(file_labels)+2
             file_labels[str(new_label_1)] = [fileA]
             file_labels[str(new_label_2)] = [fileB]
        
        # either fileA or fileB has already been categorized
        elif fileA in file_labels.values() or fileB in file_labels.values():

            categorized_file = fileA if fileA in file_labels.values() else fileB
            new_file = [fileA, fileB].remove(categorized_file)[0]
            file_labels[str(len(file_labels)+1)].extend([new_file])

if __name__ == "__main__":
    return     
