from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_core.documents import Document
import json
import os
import re
from langchain_core.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain



def raw_text_to_json(data):
    splits = data.split("**")
    print("splits",splits)
    c=0
    data_gen=[]
    topic={}
    for s_text in splits:
        
        if c>0:
            if c%2!=0:
                topic={}
                texts = s_text.split(":")
                topic['topic']=texts[1]
            else:
                texts = s_text.split("\n\n")
                cl=0
                for text in texts:
                    if cl>0 and text!='':
                        splits_again = text.split("\n")
                        levels = splits_again[0].split(":")
                        match = re.search(r"(Easy|Medium|Hard).*\((\d+)\s*Marks?\)", levels[1], re.IGNORECASE)
                        question={}
                        if match:
                            level=match.group(1)
                            mark=match.group(2)
                            question={'level': level,'mark':mark}
                        questions = splits_again[1].split(":")
                        question['questions']=questions[1]
                        t = topic['topic']
                        question['topic'] = t
                        data_gen.append(question)
                        
                        
                    cl+=1
                
        c+=1
    
    return data_gen

def generateQuestionFromResource(resource):
    print("welcome to AI")
    pdfReader = PdfReader(f"./media/{resource.source_file}")
    print("pdf Reader Object is created")
    
    
    textSplitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=800,
        chunk_overlap=200,
        length_function=len
    )
    print('textSplitter Object is Created')
    
    ollamaEmbedding = OllamaEmbeddings(model="llama3.2")
    print("ollama Embedding is created")
    
    llm = Ollama(model="llama3.2",temperature=0.7)
    print("llm object is created")
    
    all_documents = []
    pno=0
    
    for page in pdfReader.pages:
        page_content = page.extract_text()
        if page_content and pno>2 and pno<5:
            split_texts = textSplitter.split_text(page_content)
            documents = [Document(page_content=text) for text in split_texts]
            all_documents.extend(documents)
        pno+=1
        
    print("Documents are created")
    
    if os.path.exists("./media/documents.json"):
        print("wait sometime for documents to be created")
        with open("documents.json", "w") as f:
            json.dump([doc.page_content for doc in all_documents], f)
        print("Documents are created and saved in local")
    else:
        print("File already exists. Loading from disk...")
    with open("documents.json", "r") as f:
        contents = json.load(f)
    print("Documents loaded from disk")
    documents = [Document(page_content=txt) for txt in contents] 
    
    
    topicwise_prompt = PromptTemplate.from_template(
        "You are an expert question generator. Using the following PDF content, identify distinct topics and generate questions "
        "for each topic. The questions should be categorized by difficulty level: Easy, Medium, and Hard.\n\n"
        "For each topic, generate:\n"
        "- One Easy question worth 5 marks\n"
        "- One Medium question worth 10 marks\n"
        "- One Hard question worth 10 marks\n\n"
        "Each question should be meaningful, relevant to the topic, and suitable for evaluating understanding based on the content. "
        "The content could be from any domain, such as a story, academic subject, or general information.\n\n"
        "Structure your output like this:\n\n"
        "Topic: <Topic Name>\n"
        "Difficulty: Easy (5 Marks)\n"
        "Question: <Easy Question>\n\n"
        "Difficulty: Medium (10 Marks)\n"
        "Question: <Medium Question>\n\n"
        "Difficulty: Hard (10 Marks)\n"
        "Question: <Hard Question>\n\n"
        "Repeat this format for each identified topic.\n\n"
        "PDF Content:\n{context}"
    )
    print("Prompt template created")
    
    question_gen_chain = create_stuff_documents_chain(llm, topicwise_prompt)
    print("Question generation llm chain created")
    
    question_gen_response = question_gen_chain.invoke({
        "context": documents[:10]  # Use multiple chunks for a broader context
    })
    data = raw_text_to_json(question_gen_response)
        
    return data

