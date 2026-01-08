from prompt_library import PromptLibrary
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
import os
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatMessagePromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pre_processing import PreProcessor

load_dotenv()

class EmailInput(BaseModel):
    user_input: str
    user_instructions: str


class LogEmail:
    def __init__(self, payload: EmailInput):
        self.payload = payload

        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        prompts = PromptLibrary()

        email_context_system = SystemMessagePromptTemplate.from_template(
            prompts.email_context_system()
        )
        email_context_human = HumanMessagePromptTemplate.from_template(
            prompts.email_context_human()
        )
        email_composer_system = SystemMessagePromptTemplate.from_template(
            prompts.email_composer_system()
        )
        email_composer_human = HumanMessagePromptTemplate.from_template(
            prompts.email_composer_human()
        )
        email_judge_system = SystemMessagePromptTemplate.from_template(
            prompts.email_judge_system()
        )
        email_judge_human = HumanMessagePromptTemplate.from_template(
            prompts.email_judge_human()
        )
        email_finalizer_system = SystemMessagePromptTemplate.from_template(
            prompts.email_finalizer_system()
        )
        email_finalizer_human = HumanMessagePromptTemplate.from_template(
            prompts.email_finalizer_human()
        )

        self.email_context_prompt = ChatPromptTemplate.from_messages(
            [email_context_system, email_context_human]
        )
        self.email_composer_prompt = ChatPromptTemplate.from_messages(
            [email_composer_system, email_composer_human]
        )
        self.email_judge_prompt = ChatPromptTemplate.from_messages(
            [email_judge_system, email_judge_human]
        )
        self.email_finalizer_prompt = ChatPromptTemplate.from_messages(
            [email_finalizer_system, email_finalizer_human]
        )

        processor = PreProcessor(self.payload)
        self.pre_processed = processor.pre_processing_output()

        self.email_context_chain = (
                self.email_context_prompt
                | self.model
                | JsonOutputParser()
        )
        self.email_composer_chain = (
                self.email_composer_prompt
                | self.model
                | JsonOutputParser()
        )
        self.email_judge_chain = (
                self.email_judge_prompt
                | self.model
                | JsonOutputParser()
        )
        self.email_finalizer_chain = (
                self.email_finalizer_prompt
                | self.model
                | JsonOutputParser()
        )


    def log_email_output(self):
        # best: compute once and reuse so you don't call LLM multiple times
        context = self.email_context_chain.invoke({
            "user_instruction": self.payload.user_instructions,
            "pre_process_output": self.pre_processed,
            "user_input": self.payload.user_input,
        })
        composer = self.email_composer_chain.invoke({
            "email_context_output": context
        })
        judge = self.email_judge_chain.invoke({
            "email_context_output": context,
            "email_composer_output": composer,
        })
        final = self.email_finalizer_chain.invoke({
            "composed_email_json": composer,
            "judge_output_json": judge,
            "email_context_output": context,
        })
        return final