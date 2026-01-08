from prompt_library import PromptLibrary
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
import os
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatMessagePromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

class UserInput(BaseModel):
    user_input: str


class PreProcessor:
    def __init__(self, user_input: UserInput):
        self.user_input = user_input

        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        prompts = PromptLibrary()

        pre_processing_system = SystemMessagePromptTemplate.from_template(prompts.pre_processing_system())
        pre_processing_human = HumanMessagePromptTemplate.from_template(prompts.pre_processing_human())

        self.pre_processing_prompt = ChatPromptTemplate(
            [pre_processing_system, pre_processing_human]
        )

        self.pre_processing_chain = (
                self.pre_processing_prompt
                | self.model
                | JsonOutputParser()
        )


    def pre_processing_output(self):
        return self.pre_processing_chain.invoke({
            "user_input": self.user_input.user_input
        })






