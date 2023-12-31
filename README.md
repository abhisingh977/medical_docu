# Project medical_docu

The Medical Docu is a project aimed at addressing a crucial need in the healthcare sector to get updated on vast and ever changing medical knowledge present in research papers, journals, and books. 

The key goal of the Medical Docu is to make sure that medical professionals can get high quality and true information they need on tip of their fingers.

## How is this different from google or chatgpt or other search engines?
While google or chatgpt scrape data is available everywhere on web. Medical docu only have data available from prestigues and renowned medical research papers, journals and books.

## Why is this not already available:
One of the the biggest problems collecting medical information is that they are not avialable on web in form on blogs and articles. They are present in form of pdf(mostly) or ppt files.


## Problem:
Reading pdfs are hard to read for computer it does not have fix layout which makes it a really hard problem to get the clean information from pdf files especially when images and tabular data is involved.
There are several libraries that try to solve this problem such as "PyPDF2", "pdfminer", "unstructured", "layout-parser" but none of them as good as needed for the task.

## Solution:
One fist look this may seems like a nlp problem but is truly a computer vision problem, specifically a bounding box problem. 

The computer vision model has to learn to understant to contextual information and layout present in the pdf pages. But bigger botteneck right now is that exisiting tools does not understand the layout of the PDF files properly. 

### Real User Metrics:
Before you move forward i would like to share this metric dashboard to you. This is the real metrics of my project:
![alt text](img/summary.png?raw=true)
![alt text](img/analytics_dashboard.png?raw=true)

Current work and implementation:
### 1. Data collection and scrapping:
I have collected some 3000 medical books and articles in the field of anesthesia. I tried reading the pdfs using unstructured library but it was too slow so stopped it used PyMuPDF library. For cleaning the data i used libraries like string, re. All the logics for cleaning the data is func.py file. 

### 2.  Convert the text into embeddeding: 
Extracting text from PDF and converting them in small chunks then in turn converting them in embeddeding. Every embedding and text have relavent metadata attached to them.
The script used to convert the pdf files to text chucks that can be used for search is in create_vector_database.py file.

### 3. Upload the embedding Qdrant cloud:
All the embeddings and data created in step 2 is needed to upload on a vector database which can provide accurate, fast and efficient search results. For this task i am using Qdrant vector database:https://qdrant.tech/documentation/overview/
We can somewhere around million index in qdrant for free and easily use it on premises and overall it looks like a great open source company so i went ahead with this.


### 4. Deploy Webapp on Cloud:
I have created the webapp using flask with very simple ui. Its hosted on GCP cloud run. Link to webapp: https://medical-docu-svgzkfaqoa-uc.a.run.app/
![alt text](img/home.png?raw=true)
The flask code is in main.py file. 

### Result after search results
![alt text](img/results.png?raw=true)

### Current System Design:
![alt text](img/system.png?raw=true)


- [x] Added 50 Anesthisia Books in my library.
- [x] Experiment with diffrent word length for embedding.
- [x] Fast API for sentence to embedding model.
- [x] Intergration of Google analytics to track user interaction
- [x] Add Google sign and add firestore to collect user information.
- [ ] Host pdfs in webapp.

Future Work
This marks the v1 release of our project. While we have established an end-to-end workflow that functions effectively, it is only the beginning. There is a substantial amount of work ahead as we continue to enhance and expand the project's capabilities. Stay tuned for updates and improvements!
