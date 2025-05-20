from PyPDF2 import PdfReader
from langchain_community.llms.ollama import Ollama
from langchain_core.runnables import Runnable
from langchain_core.prompts import PromptTemplate


def raw_text_to_json(text):
    text_splits = text.split("\n")
    data_gen = []
    
    for i in range(len(text_splits)):
        question = {}
        if i >0 and i!=len(text_splits):
            texxt = text_splits[i].replace("\n","")
            print("texxt",texxt)
            if texxt != "":
                question = {"question": texxt}
                data_gen.append(question)
    
    return data_gen

def generateQuestionFromResource(resource):
    print("welcome to Generative AI")
    pdfreader = PdfReader(f"./media/{resource.source_file}")
    
    pno = 0
    all_docs = []
    for page in pdfreader.pages:
        if  pno<6:
            page_content  = page.extract_text()
            all_docs.append(page_content)
        pno+=1
        
    full_text = "\n".join(all_docs)
    
    prompt = PromptTemplate.from_template("""
                                          You are an expert academic question setter for technical and non-technical subjects. Your task is to generate long-answer questions based on the content provided.

                                            The questions must be:
                                            - Technical and in-depth
                                            - Suitable for an academic or exam setting
                                            - Designed to evaluate critical thinking and understanding
                                            - Relevant to the content provided
                                            - 
                                            

                                            The content is:
                                            {content}

                                            IMPORTANT:
                                            - Output ONLY the questions.
                                            - Do NOT include headings, explanations, or formatting.
                                            - Each long-answer question should be on a new line.
                                            -Ensure that question must be long answer type and not short answer type.
                                            - The questions should be clear and unambiguous.

                                            Now generate the possible long-answer questions based on the content provided:
                                           
                                          """)
    llm = Ollama(model="llama3.2",temperature=0.8,num_ctx=1024,num_thread=4)
    print("llm is created")
    chain: Runnable =prompt | llm
    print("chain is created")
    result = chain.invoke({"content": full_text})
    print("result is generated", result)
    data = raw_text_to_json(result)
    print("data is generated", data)
    return data