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
2. cd to thew root of your newly cloned git repository
3. Create a Python virtual environment ```python -m venv venv --prompt=DocAssistant```
4. Activate the virtual environment ```. venv/bin/activate```
5. Install prerequisite packages ```pip install -r requirements.txt```

