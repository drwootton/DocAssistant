# AI Document Assistant
This is a small QT-based program I wrote as part of learning about large language models. This program loads one or more documents into a FAISS vector index then uses a LLM to answer a question about those documents. 
My primary goal was to load and query PDFs. The code is written to also load HTML, .doc, .docx, .ppt, .pptx, .odp or .csv formats although I haven't tested any of those much. The concept is similar so I expect those just work. 

This program runs on your local computer and runs models stored locally on your computer. No internet access should be required.
## Important Note
I wrote this as a learning/hobby exercise in mid-2023 after learning about AI applications at the beginning of the year. As a learning exercise, this meant learning about Python as well as how to write a working program using
HuggingFace and Langchain APIs.

This program just blindly issues the query to the model. It does not attempt to build a properly constructed prompt. So it did what I wanted to accomplish, but is not perfect.

My intent was to load and query PDFs. My loader code does not perform any kind of post-processing of the PDF text after loading it. It just uses the text as is. My experience is this works reasonably for documents which have 
narrative text. It does not work so well for documents with lots of tables, figures, or complex constructs in the document.

So, that means this program may not be the best way to write an AI program. In fact, there's probably lots of room for improvement. But I had someone interested in this code, so decided to upload it, problematic as it may be.
If you think this code is useful, you can do what you want with it.
## What it Does
This program can load one or more documents, as noted, and builds a FAISS vector index. Once you create the index, you can save it so that you can reload it the next time you want it rather than rebuilding it from scratch.

Once the documents are loaded, you can load a model and ask questions about the documents, hopefully ggetting useful reply.

This program works with unquantized models and with some GPTQ models. Since I wrote this mid last year, at this point it doesn't work with GGUF models. Code needs to be written to issue the query to the GGUF model.
It may be as simple as just asking the model to use the following text (from the FAISS query) to answer the queston then appending that text to the prompt.

I wrote this program on a Linux system with a RTX 3060 and RTX 4070 GPU. Since it's QT-based, it should also just work on a Windows system. Mac is enough different that I don't know what problems will occur there.

## Installation
1. Clone this repository ```git clone git@github.com:drwootton/DocAssistant```
2. cd to the top level directory of your cloned copy of this repository
3. Create a Python virtual environment ```python -m venv venv --prompt=DocAssistant```
4. Activate the virtual environment ```. venv/bin/activate```
5. Install prerequisite packages ```pip install -r requirements.txt```

## Usage
1. cd to the top level directory of your cloned copy of this repository
2. Activate the python virtual environment ```. venv/bin/activate```
3. Start this program ```python main.py```
4. The main screen should appear

![image](https://github.com/drwootton/DocAssistant/assets/24721517/8a3ee100-a0b7-4ab4-a315-83efa457004a)

5. Load the documents you want to query using the **Documents** panel on the right side of the screen. For each document, type the document path in the **Document Path** field or use the **Browse** button to navigate to the document then click the **Add** button. Repeat until you have added all your documents.
6. Specify the chunk size (number of characters per document chunk) and number of characters to ovelap chunks
7. After all fields are filled in, click **Load Documents**
8. Once a set of documents is loaded, yoiu may save the generated index by clicking **Save Document Index** in the **File** menu.
9. Create a model profile for each model as needed by clicking the **Add** button in the **Model** pane on the left side of the window and filling in model parameters as needed.
10. Create one or more query profiles by clicking the **Add** button in the **Prompt** pane on the left side of the window
11. Load a model by selecting a model from the **Model profile** list in the Model pane and clicking the **Load** button below the list
12. Select a query profile from the **Profile** list in the Prompt pane
13. Enter your query in the **Prompt** text box in the Prompt window
14. A response should be generated in the center pane
